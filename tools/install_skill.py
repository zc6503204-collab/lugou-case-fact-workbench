#!/usr/bin/env python3
"""Install only the pinned Lugou skill files; never install dependencies or models."""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

NAME = 'case-fact-structuring'
VERSION = 'v0.3'
SHA256 = '580e1b0139ab1cc6c53ac200680bb24ccdb1e47ce404d5edfeed8bc95618248d'
SITE = 'https://zc6503204-collab.github.io/lugou-case-fact-workbench/'
MAX_BYTES = 8 * 1024 * 1024

def download(platform):
    url = SITE + 'downloads/' + platform + '-lugou-' + VERSION + '.zip'
    if shutil.which('curl'):
        result = subprocess.run(['curl','--fail','--location','--silent','--show-error',
            '--proto','=https','--proto-redir','=https','--max-time','45',
            '--max-filesize',str(MAX_BYTES),url],capture_output=True)
        if result.returncode: raise ValueError('下载失败，请检查网络或使用官网安装包；未更改安装目录。')
        return result.stdout
    with urllib.request.urlopen(url,timeout=45) as response:
        payload = response.read(MAX_BYTES+1)
    if len(payload)>MAX_BYTES: raise ValueError('安装包超过大小限制。')
    return payload

def unpack(payload, destination):
    if hashlib.sha256(payload).hexdigest()!=SHA256: raise ValueError('安装包 SHA-256 不一致，停止安装。')
    destination = Path(destination)
    seen=set()
    with zipfile.ZipFile(io.BytesIO(payload)) as package:
        if len(package.infolist())>60 or sum(i.file_size for i in package.infolist())>MAX_BYTES:
            raise ValueError('安装包结构或大小异常。')
        for info in package.infolist():
            p = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            if '\\' in info.filename or p.is_absolute() or '..' in p.parts or ':' in info.filename or not p.parts or p.parts[0]!=NAME or stat.S_ISLNK(mode):
                raise ValueError('安装包含不安全路径或符号链接。')
            if info.is_dir(): continue
            relative = Path(*p.parts[1:])
            if not relative.parts or relative.as_posix() in seen: raise ValueError('安装包存在重复或空文件路径。')
            seen.add(relative.as_posix())
            target = destination / relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(package.read(info))
    entry=destination/'SKILL.md'
    if not entry.is_file() or 'name: '+NAME not in entry.read_text(encoding='utf-8'):
        raise ValueError('安装包缺少正确 Skill 入口。')
    return sorted(seen)

def no_linked_path(path, boundary):
    current=Path(path)
    while True:
        if current.is_symlink(): raise ValueError('安装路径包含符号链接，未覆盖；请核对实际安装位置。')
        if current==boundary: break
        current=current.parent

def install(platform, dest=None, payload=None):
    if platform not in {'codex','workbuddy'}: raise ValueError('请选择 Codex 或 WorkBuddy.app。')
    app_home = Path(os.environ.get('CODEX_HOME') or Path.home()/'.codex').expanduser() if platform=='codex' else Path.home()/'.workbuddy'
    parent = (Path(dest).expanduser() if dest else app_home/'skills').resolve()
    target = parent/NAME
    no_linked_path(parent,Path(parent.anchor))
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError('已有安装位置不是普通目录，未覆盖。')
    payload = download(platform) if payload is None else payload
    with tempfile.TemporaryDirectory(prefix='lugou-install-') as temp:
        stage=Path(temp)/'package';stage.mkdir()
        files=unpack(payload,stage)
        changed=[]
        for name in files:
            existing=target/name
            no_linked_path(existing,target)
            if existing.exists() and not existing.is_file(): raise ValueError('文件与目录冲突：'+name)
            if not existing.exists() or existing.read_bytes()!=(stage/name).read_bytes(): changed.append(name)
        if not changed:
            return {'status':'already_installed','platform':platform,'version':VERSION,'path':str(target),'verified_files':len(files)}
        parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            # Stage in the same parent so final rename cannot cross filesystems.
            with tempfile.TemporaryDirectory(prefix='.lugou-stage-',dir=parent) as local_stage:
                ready=Path(local_stage)/NAME;shutil.copytree(stage,ready)
                if target.exists(): raise ValueError('安装位置刚被其他程序创建，请重试。')
                ready.rename(target)
            return {'status':'installed','platform':platform,'version':VERSION,'path':str(target),'verified_files':len(files)}
        # Back up only files that will be overwritten, outside the discovery directory.
        backup_root=parent.parent/'skill-backups'/NAME
        no_linked_path(backup_root,Path(backup_root.anchor))
        stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup=backup_root/stamp;backup.mkdir(parents=True)
        previous={name:(target/name).exists() for name in changed}
        for name,exists in previous.items():
            if exists:
                saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target/name,saved)
        (backup/'restore.json').write_text(json.dumps({'skill':NAME,'files':previous},ensure_ascii=False,indent=2),encoding='utf-8')
        written=[]
        try:
            for name in changed:
                final=target/name;final.parent.mkdir(parents=True,exist_ok=True)
                with tempfile.NamedTemporaryFile(dir=final.parent,prefix='.lugou-',delete=False) as stream:
                    temporary=Path(stream.name);stream.write((stage/name).read_bytes())
                try:
                    os.replace(temporary,final)
                    written.append(name)
                finally:
                    temporary.unlink(missing_ok=True)
            if any((target/name).read_bytes()!=(stage/name).read_bytes() for name in files):
                raise ValueError('安装后文件核验失败。')
        except Exception:
            for name in reversed(written):
                if previous[name]: shutil.copy2(backup/name,target/name)
                else: (target/name).unlink(missing_ok=True)
            raise
        return {'status':'updated','platform':platform,'version':VERSION,'path':str(target),
                'verified_files':len(files),'backup':str(backup),'preserved':'本机配置、运行环境及其他本地新增文件未覆盖'}

def main():
    parser=argparse.ArgumentParser(description='安装律构·案件事实梳理；只放置 Skill 文件')
    parser.add_argument('--platform',required=True,choices=['codex','workbuddy'])
    parser.add_argument('--dest',help='指定 Skills 父目录；测试或自定义安装时使用')
    parser.add_argument('--source-zip',help='使用已下载安装包，仍执行固定 SHA-256 校验')
    args=parser.parse_args()
    try:
        payload=Path(args.source_zip).read_bytes() if args.source_zip else None
        print(json.dumps(install(args.platform,args.dest,payload),ensure_ascii=False,indent=2))
    except Exception as error:
        print(json.dumps({'status':'failed','error':str(error)},ensure_ascii=False),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__': sys.exit(main())
