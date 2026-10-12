"""Move TITLE/COSROOM out of GD-ROM run-out; preserve all ISO file contents."""
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
    prior=ROOT/'work/korean-hardware-v1103-final-disc';core=ROOT/'work/settings-core-hardware-v1104';out=ROOT/'work/korean-hardware-v1104-disc'
    assert not out.exists();spec=json.loads((ROOT/'data/source-hashes.json').read_bytes())
    mr=(core/'manifest.json').read_bytes();gate=json.loads((core/'source-disassembly-review-proof.json').read_bytes())
    assert gate['status']=='passed' and gate['candidate_manifest_sha256']==sha(mr) and gate['new_executable_code_changes'] is False
    with GDImage(prior) as d,GDImage(spec['source']) as original:
        assert digest(d.track3)=='581737e9d7d757eecc49a6862d06b8e879300379d0468c6a8aee4a6a053836fc'
        assert digest(original.track3)==next(r['sha256'] for r in spec['files'] if '(Track 3)' in r['name'])
        end=d.volume_start+d.track3_sectors;limit=end-150;assert (limit,end)==(549000,549150)
        entries=d.entries();by={e.name:e for e in entries}
        offenders=[e for e in entries if e.lba+(e.size+2047)//2048>limit]
        assert sorted(e.name for e in offenders)==['COSROOM.PVM','TITLE.BIN']
        boot=by['1ST_READ.BIN'];assert boot.lba+(boot.size+2047)//2048==limit
        assert not any(original.read(limit,150*2048))
        prefix_limit=min(e.lba for e in original.entries())
        start=(max(e.lba+(e.size+2047)//2048 for e in entries if e.lba<prefix_limit)+31)&~31
        targets={};assets={};relocations=[]
        for name in ('TITLE.BIN','COSROOM.PVM'):
            e=by[name];raw=d.read(e.lba,e.size);count=(len(raw)+2047)//2048
            assert start+count<prefix_limit
            assert not any(d.read(start,count*2048)) and not any(original.read(start,count*2048))
            for other in entries:assert start+count<=other.lba or start>=other.lba+(other.size+2047)//2048
            assets[name]=raw;targets[name]=start
            relocations.append({'name':name,'previous_lba':e.lba,'new_lba':start,'bytes':len(raw),'sectors':count,'sha256':sha(raw),'destination_originally_zero':True})
            start=(start+count+31)&~31
        assert sha(assets['TITLE.BIN'])=='c64df57c8dcb717353157d2b94f6a9a32ddeaa1bbcf57acea96fbaa8ec25c7e6'
        assert sha(assets['COSROOM.PVM'])=='28a7b1a0cd5993c0aeda8b399251f2cad4d5b0eb280919e127041ebbebc580fa'
        directory=bytearray(d.read(d.root_lba,d.root_size));p=0;found=[]
        while p<len(directory):
            n=directory[p]
            if not n:p=(p//2048+1)*2048;continue
            name=directory[p+33:p+33+directory[p+32]].split(b';')[0].decode('ascii')
            if name in assets:
                assert struct.unpack_from('<I',directory,p+2)[0]==by[name].lba
                assert struct.unpack_from('<I',directory,p+10)[0]==by[name].size
                struct.pack_into('<I',directory,p+2,targets[name]);struct.pack_into('>I',directory,p+6,targets[name]);found.append(name)
            p+=n
        assert sorted(found)==sorted(assets)
        changes={}
        for lba,data in [(d.root_lba,bytes(directory)),(limit,bytes(150*2048))]+[(targets[n],r) for n,r in assets.items()]:
            for i in range((len(data)+2047)//2048):
                before=d.read(lba+i,2048);chunk=data[i*2048:(i+1)*2048];after=chunk+before[len(chunk):]
                if before!=after:assert lba+i not in changes;changes[lba+i]=after
        assert not any(45000<=lba<45016 for lba in changes)
        out.mkdir()
        for row in spec['files']:shutil.copy2(prior/row['name'],out/row['name'])
        with (out/d.track3.name).open('r+b') as f:
            for lba,data in sorted(changes.items()):
                offset=(lba-45000)*SECTOR;f.seek(offset);before=f.read(SECTOR);after=update_mode1(before,data)
                assert verify_mode1(after);f.seek(offset);f.write(after)
        actual=[]
        with d.track3.open('rb') as a,(out/d.track3.name).open('rb') as b:
            i=0
            while before:=a.read(SECTOR*4096):
                after=b.read(len(before));assert len(before)==len(after)
                if before!=after:
                    for k in range(len(before)//SECTOR):
                        lo=k*SECTOR;hi=lo+SECTOR
                        if before[lo:hi]!=after[lo:hi]:
                            lba=45000+i+k;assert lba in changes and after[lo+16:lo+2064]==changes[lba] and verify_mode1(after[lo:hi]);actual.append(lba)
                i+=len(before)//SECTOR
            assert not b.read(1)
        assert set(actual)==set(changes)
        with GDImage(out) as result:
            new=result.entries();assert len(new)==len(entries)
            for old,e in zip(entries,new):
                assert (old.name,old.size,old.flags)==(e.name,e.size,e.flags)
                assert e.lba+(e.size+2047)//2048<=limit
                if e.name in assets:assert e.lba==targets[e.name] and result.read(e.lba,e.size)==assets[e.name]
                else:assert old.lba==e.lba and not any(e.lba<=l<e.lba+(e.size+2047)//2048 for l in changes)
            assert result.read(45000,32768)==original.read(45000,32768)
        with original.track3.open('rb') as a,(out/d.track3.name).open('rb') as b:
            off=(limit-45000)*SECTOR;a.seek(off);b.seek(off);tail=a.read();assert tail==b.read() and len(tail)==150*SECTOR
        build=copy.deepcopy(json.loads((prior/'proof.json').read_bytes()))
        build.update(status='V1.104 reserved GD-ROM run-out restored; native code unchanged; hardware untested',reference_disc=prior.name,
            settings_core_dir=core.name,cue=str(next(out.glob('*.cue'))),merged_core_manifest_sha256=sha(mr),changed_sectors_from_previous=len(actual))
        for row in build['files']:
            if row['name'] in assets:row.update(new_lba=targets[row['name']],bytes=len(assets[row['name']]),asset_sha256=sha(assets[row['name']]))
        write(out/'proof.json',build)
        proof={'version':'1.104','status':'passed','candidate_core_manifest_sha256':sha(mr),'trial_track_sha256':digest(out/d.track3.name),
            'changed_lbas':actual,'changed_sectors':len(actual),'relocations':relocations,'all_other_raw_sectors_exact':True,
            'all_ISO_file_contents_byte_exact':True,'preserved_ISO_files':len(entries),'all_AFS_extents_preserved':True,'IP_BIN_exact':True,
            'boot_main_lba':boot.lba,'boot_main_bytes':boot.size,'boot_main_end':limit,'main_and_font_unchanged':True,
            'runout_start_lba':limit,'runout_sectors':150,'runout_raw_exact_original':True,'files_crossing_runout':0,
            'actual_hardware_tested':False,'new_audio_playback_or_screen_QA':False}
        write(out/'asset-preservation-proof.json',proof)
        write(core/'change-specification.json',{'version':'1.104','scope':'ISO extents and GD-ROM run-out only','relocations':relocations,
            'all_file_contents_unchanged':True,'runout_restored_from_original':True,'native_code_changes':False,'hardware_tested':False})
        print(json.dumps({k:v for k,v in proof.items() if k!='changed_lbas'}))
if __name__=='__main__':main()
