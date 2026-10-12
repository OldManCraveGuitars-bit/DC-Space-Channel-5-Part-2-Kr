"""Freeze V1.103 code unchanged for the V1.104 disc-layout repair."""
import copy,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    base=ROOT/'work/settings-core-hardware-v1103';out=ROOT/'work/settings-core-hardware-v1104'
    mr=(base/'manifest.json').read_bytes();assert sha(mr)=='e7843ac0893a89a58274755fbe25ba370913df05841a95ede98fa62fb3830a7c'
    assert not out.exists();out.mkdir()
    for name in ['1ST_READ.BIN','ZENFONT.GD','core.bin','core.elf','font-hook.bin','title-hook.bin','judgment-hook.bin','subtitle-extra.bin','symbols.txt','disassembly.txt']:
        shutil.copy2(base/name,out/name)
    shutil.copytree(base/'native-source',out/'native-source')
    m=json.loads(mr);m.update(version='1.104',status='V1.104 disc run-out repair; V1.103 native code unchanged; actual hardware untested',native_code_reference_manifest_sha256=sha(mr))
    (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'status':'frozen','code_unchanged_from':'1.103'}))
if __name__=='__main__':main()
