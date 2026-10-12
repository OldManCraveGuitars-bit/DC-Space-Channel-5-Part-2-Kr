"""Check deferred initialization's actual SH4 call order and preserved inputs."""
import hashlib,json,struct
from pathlib import Path
import check_hardware_core_v1101 as boot
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'work/settings-core-hardware-v1103'
BASE=ROOT/'work/settings-core-hardware-v1102'
def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    boot.OUT=OUT;boot.main()
    m=json.loads((OUT/'manifest.json').read_bytes());old=json.loads((BASE/'manifest.json').read_bytes())
    s=m['symbols'];base=m['payload_address'];code=(OUT/'core.bin').read_bytes()
    font=(OUT/'ZENFONT.GD').read_bytes();oldfont=(BASE/'ZENFONT.GD').read_bytes()
    assert font[:m['font_reserve_bytes']]==oldfont[:m['font_reserve_bytes']]
    assert font[m['font_reserve_bytes']+len(code):]==bytes(1580)
    assert len(font)==m['payload_bss_end']-m['font_address']<0x40000
    assert (OUT/'subtitle-extra.bin').read_bytes()==(BASE/'subtitle-extra.bin').read_bytes()
    for item in m['reused_objects']:
        assert (OUT/item['file']).read_bytes()==(BASE/item['file']).read_bytes()
    # Literal destinations are checked after relocation, not just in source.
    for name,target in [('boot_ready','_font_boot_init'),('boot_state_init','_state_init'),
                        ('boot_font_init','_original_font_init'),('title_subtitle_init','_subtitle_init'),
                        ('title_resume',None)]:
        assert struct.unpack_from('<I',code,s[name]-base)[0]==(s[target] if target else 0x8c27000c)
    class Calls:
        def __init__(self,entry):
            self.r=[0x65430000+i*256 for i in range(16)];self.r[4]=0x8c2c0000;self.r[15]=0x8cffff00
            self.saved=self.r.copy();self.pr=0x8c000800;self.pc=s[entry];self.mem={};self.pending=None;self.calls=[]
        def read(self,a,n):
            assert a%n==0
            if base<=a<a+n<=base+len(code):return int.from_bytes(code[a-base:a-base+n],'little')
            return self.mem[a]
        def run(self):
            known={s[k]:k for k in ('_state_init','_original_font_init','_subtitle_init','_original_title_init')}
            for _ in range(100):
                if self.pc==0x8c000800:break
                if self.pc in known:
                    self.calls.append(known[self.pc])
                    if known[self.pc]=='_original_font_init':assert self.r[4]==0x8c2c0000
                    if known[self.pc]=='_original_title_init':assert self.r[4:8]==self.saved[4:8]
                    # C calls may destroy all caller-saved integer registers.
                    for i in range(8):self.r[i]=0x12340000+i
                    self.pc=self.pr;continue
                pc=self.pc;w=self.read(pc,2);n=(w>>8)&15;q=(w>>4)&15
                prior=self.pending;self.pending=None;self.pc+=2
                if w==9:pass
                elif w==0x4f22:self.r[15]-=4;self.mem[self.r[15]]=self.pr
                elif w==0x4f26:self.pr=self.read(self.r[15],4);self.r[15]+=4
                elif w&0xf00f==0x2006:self.r[n]-=4;self.mem[self.r[n]]=self.r[q]
                elif w&0xf00f==0x6006:self.r[n]=self.read(self.r[q],4);self.r[q]+=4
                elif w&0xf000==0xd000:self.r[n]=self.read(((pc+4)&~3)+(w&255)*4,4)
                elif w&0xf0ff in (0x400b,0x402b):
                    self.pending=self.r[n]
                    if w&0xf0ff==0x400b:self.pr=pc+4
                else:raise AssertionError((hex(pc),hex(w)))
                if prior is not None:self.pc=prior
            assert self.pc==0x8c000800 and self.r[8:]==self.saved[8:] and self.pr==0x8c000800
            return self.calls
    early=Calls('_font_boot_init').run();late=Calls('_native_title_entry').run()
    assert early==['_state_init','_original_font_init']
    assert late==['_subtitle_init','_original_title_init']
    original=bytes.fromhex('e62f224ff87f0fd3522f611f')
    clone=code[s['_original_title_init']-base:s['_original_title_init']-base+12]
    assert original[:6]==clone[:6] and original[8:]==clone[8:]
    w=int.from_bytes(clone[6:8],'little');assert w>>8==0xd3
    literal=((s['_original_title_init']+10)&~3)+(w&255)*4
    assert struct.unpack_from('<I',code,literal-base)[0]==0x8c274f14
    assert (OUT/'title-hook.bin').read_bytes()==bytes.fromhex('01d02b400900090050002f8c')
    # All six templates still target their linked callbacks; original sites
    # remain untouched on disk and are source-gated by the reused initializer.
    main=(OUT/'1ST_READ.BIN').read_bytes()
    for i,h in enumerate(m['voice_subtitles']['hooks']):
        addr=int(h['address'],16);off=s['_subtitle_hook_templates']-base+i*12
        assert code[off:off+12]==bytes.fromhex(h['replacement'])
        assert main[addr-0x8c010000:addr-0x8c010000+12]==bytes.fromhex(h['expected'])
    for key in ('production_subtitle_binding_records','trial_subtitle_binding_records'):
        assert m['voice_subtitles'][key]==old['voice_subtitles'][key]
    p=OUT/'source-disassembly-review-proof.json';proof=json.loads(p.read_bytes())
    proof.update(version='1.103',font_boot_calls=early,title_tick_calls=late,
        modified_wrappers_actual_SH4_instruction_model=True,all_C_objects_reused_byte_exact=True,
        font_and_caption_prefix_byte_exact=True,all_six_hooks_original_until_TITLE=True,
        explicit_zero_BSS_bytes=1580,hardware_tested=False,verifier_sha256=sha(Path(__file__).read_bytes()))
    p.write_text(json.dumps(proof,indent=2)+'\n','utf8')
    print(json.dumps({'status':'passed','font_boot_calls':early,'title_tick_calls':late}))
if __name__=='__main__':main()
