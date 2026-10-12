"""Confirm no executable, font, subtitle, timing or settings changes in V1.104."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    out=ROOT/'work/settings-core-hardware-v1104';base=ROOT/'work/settings-core-hardware-v1103'
    m=(out/'manifest.json').read_bytes();old=json.loads((base/'source-disassembly-review-proof.json').read_bytes());assert old['status']=='passed'
    files=[]
    for path in sorted(out.rglob('*')):
        if not path.is_file() or path.name=='manifest.json':continue
        rel=path.relative_to(out);assert path.read_bytes()==(base/rel).read_bytes();files.append({'file':rel.as_posix(),'sha256':sha(path.read_bytes())})
    proof={'version':'1.104','status':'passed','candidate_manifest_sha256':sha(m),'native_code_unchanged_from':'1.103',
        'inherited_source_review_sha256':sha((base/'source-disassembly-review-proof.json').read_bytes()),'files':files,
        'new_executable_code_changes':False,'hardware_tested':False,'new_audio_or_screen_QA':False}
    (out/'source-disassembly-review-proof.json').write_text(json.dumps(proof,indent=2)+'\n','utf8')
    print(json.dumps({'status':'passed','byte_exact_files':len(files)}))
if __name__=='__main__':main()
