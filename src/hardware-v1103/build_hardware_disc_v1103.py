"""Replace only the resident bootstrap and font-native payload in V1.102."""
import copy,hashlib,json,shutil,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sc5.disc import GDImage,SECTOR
from sc5.sector import update_mode1,verify_mode1
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
    previous=ROOT/'work/korean-hardware-v1102-disc'; core=ROOT/'work/settings-core-hardware-v1103'
    out=ROOT/'work/korean-hardware-v1103-final-disc'; assert not out.exists()
    spec=json.loads((ROOT/'data/source-hashes.json').read_bytes())
    mr=(core/'manifest.json').read_bytes();m=json.loads(mr)
    gate=json.loads((core/'source-disassembly-review-proof.json').read_bytes())
    assert gate['status']=='passed' and gate['candidate_manifest_sha256']==sha(mr)
    with GDImage(previous) as image:
        assert digest(image.track3)=='2c0182ce6b49cee69dff70bca6cf35c7f3c77610acb213ef58dda45faab07b8d'
        entries=list(image.entries());lookup={e.name:e for e in entries};mainentry=lookup['1ST_READ.BIN'];fontentry=lookup['ZENFONT.GD']
        main=bytearray(image.read(mainentry.lba,mainentry.size));base=ROOT/'work/settings-core-hardware-v1102'
        before=bytes(main);pos=0x2add6
        assert main[pos:pos+56]==(base/'1ST_READ.BIN').read_bytes()[pos:pos+56]
        main[pos:pos+56]=(core/'font-hook.bin').read_bytes()
        assert main[:pos]==before[:pos] and main[pos+56:]==before[pos+56:]
        assert image.read(fontentry.lba,fontentry.size)==(base/'ZENFONT.GD').read_bytes()
        assets={'1ST_READ.BIN':bytes(main),'ZENFONT.GD':(core/'ZENFONT.GD').read_bytes()}
        titleentry=lookup['TITLE.BIN'];title=bytearray(image.read(titleentry.lba,titleentry.size))
        assert title[:12].hex()=='e62f224ff87f0fd3522f611f'
        title[:12]=(core/'title-hook.bin').read_bytes()
        assets['TITLE.BIN']=bytes(title)
        boundary=min(e.lba for e in entries if e.lba>fontentry.lba)
        assert fontentry.lba+(len(assets['ZENFONT.GD'])+2047)//2048<=boundary
        directory=bytearray(image.read(image.root_lba,image.root_size));p=found=0
        while p<len(directory):
            length=directory[p]
            if not length:p=(p//2048+1)*2048;continue
            if directory[p+33:p+33+directory[p+32]].split(b';')[0]==b'ZENFONT.GD':
                assert struct.unpack_from('<I',directory,p+10)[0]==fontentry.size
                struct.pack_into('<I',directory,p+10,len(assets['ZENFONT.GD']));struct.pack_into('>I',directory,p+14,len(assets['ZENFONT.GD']));found+=1
            p+=length
        assert found==1
        changes={}
        for lba,raw in [(image.root_lba,bytes(directory))]+[(lookup[k].lba,v) for k,v in assets.items()]:
            for i in range((len(raw)+2047)//2048):
                prior=image.read(lba+i,2048);part=raw[i*2048:(i+1)*2048];after=part+prior[len(part):]
                if prior!=after:assert lba+i not in changes;changes[lba+i]=after
        assert not any(45000<=lba<45016 for lba in changes), 'IP.BIN unchanged'
        out.mkdir()
        for r in spec['files']:shutil.copy2(previous/r['name'],out/r['name'])
        with (out/image.track3.name).open('r+b') as f:
            for lba,data in sorted(changes.items()):
                offset=(lba-image.volume_start)*SECTOR;f.seek(offset);raw=f.read(SECTOR)
                patched=update_mode1(raw,data);assert verify_mode1(patched);f.seek(offset);f.write(patched)
        actual=[]
        with image.track3.open('rb') as a,(out/image.track3.name).open('rb') as b:
            i=0
            while raw:=a.read(SECTOR*4096):
                other=b.read(len(raw));assert len(raw)==len(other)
                if raw!=other:
                    for k in range(len(raw)//SECTOR):
                        first=raw[k*SECTOR:(k+1)*SECTOR];second=other[k*SECTOR:(k+1)*SECTOR]
                        if first!=second:
                            lba=image.volume_start+i+k;assert lba in changes and second[16:2064]==changes[lba] and verify_mode1(second);actual.append(lba)
                i+=len(raw)//SECTOR
            assert not b.read(1)
        assert set(actual)==set(changes)
        with GDImage(out) as result:
            current=list(result.entries()); assert len(current)==len(entries)
            for old,new in zip(entries,current):
                assert (old.name,old.lba,old.flags)==(new.name,new.lba,new.flags)
                if old.name in assets:assert result.read(new.lba,new.size)==assets[old.name]
                else:assert old.size==new.size and not any(old.lba<=lba<old.lba+(old.size+2047)//2048 for lba in changes)
        build=copy.deepcopy(json.loads((previous/'proof.json').read_bytes()))
        build.update(status='V1.103 deferred subtitle hook installation; actual hardware untested',reference_disc=previous.name,
            settings_core_dir=core.name,cue=str(next(out.glob('*.cue'))),merged_core_manifest_sha256=sha(mr),
            merged_source_review_sha256=digest(core/'source-disassembly-review-proof.json'),changed_sectors_from_previous=len(actual))
        for row in build['files']:
            if row['name'] in assets:row.update(bytes=len(assets[row['name']]),asset_sha256=sha(assets[row['name']]))
        write(out/'proof.json',build)
        proof={'status':'passed','candidate_core_manifest_sha256':sha(mr),'trial_track_sha256':digest(out/image.track3.name),
            'changed_lbas':actual,'changed_assets':{k:sha(v) for k,v in assets.items()},'all_other_raw_sectors_exact':True,
            'IP_BIN_exact':True,'all_ISO_extents_preserved':True,'preserved_ISO_files':len(entries)-3,
            'main_bootstrap_only_changed':True,'TITLE_entry_12_bytes_changed':True,'actual_hardware_tested':False,'new_audio_playback_or_screen_QA':False}
        write(out/'asset-preservation-proof.json',proof)
        print(json.dumps(proof))
if __name__=='__main__':main()
