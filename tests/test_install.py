"""Disposable installation checks; never touch the user's installed skills."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'tools/install_skill.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
PAYLOAD=(ROOT/'docs/downloads/codex-lugou-v0.3.zip').read_bytes()

class Installation(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.dest=self.root/'codex'/'skills'
    def install(self,platform='codex',dest=None):
        return installer.install(platform,dest or self.dest,PAYLOAD)
    def test_new_install_and_idempotence(self):
        first=self.install();target=Path(first['path'])
        self.assertEqual(first['status'],'installed');self.assertEqual(first['verified_files'],17)
        self.assertFalse((target/'case.json').exists())
        original=(target/'SKILL.md').stat().st_mtime_ns
        repeat=self.install()
        self.assertEqual(repeat['status'],'already_installed')
        self.assertEqual((target/'SKILL.md').stat().st_mtime_ns,original)
    def test_platform_destinations(self):
        with patch.dict(os.environ,{'CODEX_HOME':str(self.root/'custom-codex')}):
            r=installer.install('codex',payload=PAYLOAD)
            self.assertEqual(Path(r['path']),self.root/'custom-codex/skills/case-fact-structuring')
        with patch.object(Path,'home',return_value=self.root):
            r=installer.install('workbuddy',payload=PAYLOAD)
            self.assertEqual(Path(r['path']),self.root/'.workbuddy/skills/case-fact-structuring')
            self.assertFalse((self.root/'.workbuddy-ai').exists())
    def test_update_backup_and_local_records(self):
        target=Path(self.install()['path'])
        (target/'SKILL.md').write_text('本机旧版，待备份',encoding='utf-8')
        (target/'runtime.local.json').write_text('{"local":true}',encoding='utf-8')
        (target/'律师备注.md').write_text('保留人工笔记',encoding='utf-8')
        (target/'.runtime').mkdir();(target/'.runtime/marker').write_text('本机环境')
        (target/'scripts/macos_ocr.swift').unlink()
        result=self.install();backup=Path(result['backup'])
        self.assertEqual(result['status'],'updated')
        self.assertFalse(backup.is_relative_to(self.dest))
        self.assertEqual((backup/'SKILL.md').read_text(),'本机旧版，待备份')
        self.assertEqual((target/'runtime.local.json').read_text(),'{"local":true}')
        self.assertEqual((target/'律师备注.md').read_text(),'保留人工笔记')
        self.assertEqual((target/'.runtime/marker').read_text(),'本机环境')
        self.assertTrue((target/'scripts/macos_ocr.swift').exists())
    def test_checksum_failure_does_not_create_install_dir(self):
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            installer.install('codex',self.dest,PAYLOAD+b'changed')
        self.assertFalse(self.dest.exists())
    def test_download_is_pinned_to_this_project(self):
        class Result:
            returncode=0;stdout=PAYLOAD
        with patch.object(installer.shutil,'which',return_value='/usr/bin/curl'),patch.object(installer.subprocess,'run',return_value=Result()) as run:
            self.assertEqual(installer.download('workbuddy'),PAYLOAD)
            args=run.call_args.args[0]
            self.assertEqual(args[-1],installer.SITE+'downloads/workbuddy-lugou-v0.3.zip')
            self.assertIn('--proto-redir',args);self.assertNotIn('-k',args)
    def test_symbolic_link_does_not_modify_other_directory(self):
        other=self.root/'other';other.mkdir();(other/'private-note').write_text('保留')
        self.dest.mkdir(parents=True);(self.dest/installer.NAME).symlink_to(other,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'普通目录'): self.install()
        self.assertEqual((other/'private-note').read_text(),'保留')
        self.assertFalse((other/'SKILL.md').exists())
    def test_linked_file_in_existing_skill_stops_update(self):
        target=Path(self.install()['path']);other=self.root/'private.txt';other.write_text('本机文件')
        (target/'SKILL.md').unlink();(target/'SKILL.md').symlink_to(other)
        with self.assertRaisesRegex(ValueError,'符号链接'):self.install()
        self.assertEqual(other.read_text(),'本机文件')
    def test_partial_update_failure_rolls_back(self):
        target=Path(self.install()['path'])
        (target/'SKILL.md').write_text('旧版入口')
        (target/'agents/openai.yaml').write_text('旧版元数据')
        real_replace=installer.os.replace;calls=[]
        def fail_second(src,dst):
            calls.append(str(dst))
            if len(calls)==2:raise OSError('模拟写入中断')
            return real_replace(src,dst)
        with patch.object(installer.os,'replace',side_effect=fail_second):
            with self.assertRaisesRegex(OSError,'模拟写入中断'): self.install()
        self.assertEqual((target/'SKILL.md').read_text(),'旧版入口')
        self.assertEqual((target/'agents/openai.yaml').read_text(),'旧版元数据')
    def test_unsafe_archive_paths_and_symlinks(self):
        for name,symlink in [('case-fact-structuring/../../outside',False),('/outside',False),('case-fact-structuring/scripts/link',True)]:
            with self.subTest(name=name):
                blob=io.BytesIO()
                with zipfile.ZipFile(blob,'w') as z:
                    info=zipfile.ZipInfo(name)
                    if symlink:info.external_attr=(stat.S_IFLNK|0o777)<<16
                    z.writestr(info,b'outside')
                raw=blob.getvalue()
                with patch.object(installer,'SHA256',hashlib.sha256(raw).hexdigest()):
                    with self.assertRaisesRegex(ValueError,'不安全'):installer.unpack(raw,self.root/'unpack')
                self.assertFalse((self.root/'outside').exists())
    def test_published_manifest_matches_helper_and_package(self):
        manifest=json.loads((ROOT/'docs/install-manifest.json').read_text())
        self.assertEqual(manifest['installer']['sha256'],hashlib.sha256((ROOT/'docs/install_skill.py').read_bytes()).hexdigest())
        self.assertEqual((ROOT/'docs/install_skill.py').read_bytes(),(ROOT/'tools/install_skill.py').read_bytes())
        for platform in ['codex','workbuddy']:
            self.assertEqual(manifest['packages'][platform]['sha256'],hashlib.sha256((ROOT/f'docs/downloads/{platform}-lugou-v0.3.zip').read_bytes()).hexdigest())

if __name__=='__main__':unittest.main(verbosity=2)
