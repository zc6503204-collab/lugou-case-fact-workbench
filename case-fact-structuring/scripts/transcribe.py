#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import wave

def srt_time(sec):
    ms = max(0,round(sec*1000))
    return "%02d:%02d:%02d,%03d"%(ms//3600000,ms//60000%60,ms//1000%60,ms%1000)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input");p.add_argument("--out",required=True);p.add_argument("--model",required=True)
    p.add_argument("--ffmpeg",required=True);p.add_argument("--language",default="zh")
    a = p.parse_args()
    model = Path(a.model).resolve()
    if not (model/"config.json").is_file() or not (model/"weights.npz").is_file():
        raise RuntimeError("本地模型配置或权重缺失")
    os.environ["HF_HUB_OFFLINE"]="1"
    os.environ["TRANSFORMERS_OFFLINE"]="1"
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    wav=out/"audio-16k.wav"
    subprocess.run([a.ffmpeg,"-nostdin","-v","error","-y","-i",str(Path(a.input).resolve()),
        "-ar","16000","-ac","1","-c:a","pcm_s16le",str(wav)],check=True,capture_output=True)
    import numpy as np
    with wave.open(str(wav),"rb") as w:
        audio=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
    duration=len(audio)/16000
    if not len(audio):
        raise RuntimeError("原录音未含有效音频帧；请确认文件完整性并补交原录音")
    segments=[]
    silence=float(np.max(np.abs(audio)))<0.0001
    if not silence:
        import mlx_whisper
        result=mlx_whisper.transcribe(audio,path_or_hf_repo=str(model),language=a.language,
            word_timestamps=True,condition_on_previous_text=False,temperature=0.0,verbose=False)
        for si,s in enumerate(result.get("segments",[]),1):
            # Engine windows may span many sentences. Use its word times for
            # short replay units, preserving the untouched engine text below.
            groups=[];pending=[]
            for w in s.get("words",[]):
                pending.append(w)
                if re.search(r"[，,。.!！?？;；]$",w["word"]):
                    groups.append(pending);pending=[]
            if pending:groups.append(pending)
            if not groups:groups=[[{"word":s["text"],"start":s["start"],"end":s["end"]}]]
            for words in groups:
                start=max(0,float(words[0]["start"]));end=min(duration,float(words[-1]["end"]))
                text="".join(w["word"] for w in words).strip()
                if text and end>start:
                    segments.append({"start":start,"end":end,"text":text,"speaker":"未确认",
                        "review_status":"待听核","engine_segment_index":si,
                        "avg_logprob":s.get("avg_logprob"),"no_speech_prob":s.get("no_speech_prob"),"words":words})
    d={"source":str(Path(a.input).resolve()),"model":str(model),"duration":duration,
       "language":a.language,"silence":silence,"segments":segments,
       "engine_segments":[] if silence else result.get("segments",[]),
       "note":"自动转写供定位，关键姓名、金额和原话需回听。"}
    (out/"transcript.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    srt="\n\n".join("%d\n%s --> %s\n%s"%(i,srt_time(s["start"]),srt_time(s["end"]),s["text"])
                  for i,s in enumerate(segments,1))
    (out/"transcript.srt").write_text(srt,encoding="utf-8")
    print(json.dumps({"duration":duration,"segments":len(segments),"silence":silence},ensure_ascii=False))

if __name__=="__main__": main()
