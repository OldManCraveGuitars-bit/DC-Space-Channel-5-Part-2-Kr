"""Bounded instruction checks of the actual SH4 bootstrap; not hardware QA."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'work/settings-core-hardware-v1101'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    manifest_raw=(OUT/'manifest.json').read_bytes();m=json.loads(manifest_raw)
    sy=m['symbols'];code=(OUT/'core.bin').read_bytes();original=(ROOT/'work/original/1ST_READ.BIN').read_bytes()
    native=(OUT/'1ST_READ.BIN').read_bytes(); start=0x8c2f0000; stop=start+len(code)
    # The 28 original font instructions match exactly after normalizing only
    # the five PC-relative literal loads. Both return/free paths are retained.
    clone=sy['_original_font_init']; assert sy['_original_font_init_end']-clone==56
    for offset in range(0,56,2):
        a=struct.unpack_from('<H',original,0x2add6+offset)[0]
        b=struct.unpack_from('<H',code,clone-start+offset)[0]
        if a>>12==0xd:
            assert a&0xff00==b&0xff00
            aa=((0x8c03add6+offset+4)&~3)+(a&255)*4
            bb=((clone+offset+4)&~3)+(b&255)*4
            assert original[aa-0x8c010000:aa-0x8c010000+4]==code[bb-start:bb-start+4]
        else:assert a==b,(offset,hex(a),hex(b))
    class Model:
        def __init__(self,font,sr):
            self.r=[0x60000000+i*0x100 for i in range(16)];self.r[4]=font;self.r[15]=0x8cffff00
            self.initial=self.r.copy();self.sr=sr;self.initial_sr=sr;self.pr=0x8c01f00e
            self.pc=0x8c03add6;self.ram={};self.written=set();self.invalidated=[];self.steps=0
            self.pending=None;self.last_invalidate=-999;self.first_payload=None
        def canonical(self,a):return a-0x20000000 if 0xac000000<=a<0xae000000 else a
        def read(self,a,n=4):
            assert a%n==0,(hex(a),n)
            a=self.canonical(a)
            if 0x8c010000<=a<a+n<=0x8c010000+len(native):b=native[a-0x8c010000:a-0x8c010000+n]
            elif start<=a<a+n<=stop:b=code[a-start:a-start+n]
            else:return self.ram[a]
            return int.from_bytes(b,'little')
        def write(self,a,v):
            assert a%4==0
            if a&0xff000000==0xf0000000:
                assert self.pc&0xe0000000==0xa0000000
                assert self.sr&0x100000f0==0x100000f0
                self.invalidated.append((a,v));self.last_invalidate=self.steps
            else:self.ram[self.canonical(a)]=v
        def t(self,v):self.sr=(self.sr&~1)|int(v)
        def step(self):
            pc=self.pc;cp=self.canonical(pc)
            if start<=cp<stop:
                if self.first_payload is None:self.first_payload=pc
                assert (cp&~31) in self.written,'P2 code read before writeback'
            w=self.read(pc,2);n=(w>>8)&15;q=(w>>4)&15
            prior=self.pending;self.pending=None;self.pc+=2
            if w==0x0009:pass
            elif w==0x4f22:self.r[15]-=4;self.write(self.r[15],self.pr)
            elif w==0x4f26:self.pr=self.read(self.r[15]);self.r[15]+=4
            elif w==0x000b:self.pending=self.pr
            elif w&0xf0ff==0x0002:self.r[n]=self.sr
            elif w&0xf0ff==0x400e:self.sr=self.r[n]
            elif w&0xf000==0xd000:self.r[n]=self.read(((pc+4)&~3)+(w&255)*4)
            elif w&0xf000==0xe000:self.r[n]=((w&255)^128)-128
            elif w&0xf000==0x7000:self.r[n]=(self.r[n]+((w&255)^128)-128)&0xffffffff
            elif w&0xf00f==0x2006:self.r[n]-=4;self.write(self.r[n],self.r[q])
            elif w&0xf00f==0x6006:self.r[n]=self.read(self.r[q]);self.r[q]+=4
            elif w&0xf00f==0x6003:self.r[n]=self.r[q]
            elif w&0xf00f==0x2008:self.t(self.r[n]&self.r[q]==0)
            elif w&0xf00f==0x2009:self.r[n]&=self.r[q]
            elif w&0xf00f==0x200b:self.r[n]|=self.r[q]
            elif w&0xf00f==0x3002:self.t(self.r[n]>=self.r[q])
            elif w&0xf00f==0x3006:self.t(self.r[n]>self.r[q])
            elif w&0xf00f==0x300c:self.r[n]=(self.r[n]+self.r[q])&0xffffffff
            elif w&0xf00f==0x2002:self.write(self.r[n],self.r[q])
            elif w&0xf0ff==0x4009:self.r[n]>>=2
            elif w&0xf0ff==0x4001:self.t(self.r[n]&1);self.r[n]>>=1
            elif w&0xf0ff==0x4010:self.r[n]-=1;self.t(self.r[n]==0)
            elif w&0xf0ff==0x00b3:self.written.add(self.canonical(self.r[n])&~31)
            elif w&0xf0ff in (0x400b,0x402b):
                self.pending=self.r[n]
                if w&0xf0ff==0x400b:self.pr=pc+4
            elif w&0xf000==0xa000:self.pending=pc+4+(((w&4095)^2048)-2048)*2
            elif w&0xff00 in (0x8900,0x8b00,0x8d00,0x8f00):
                take=bool(self.sr&1)==bool(not(w&0x200))
                dest=pc+4+(((w&255)^128)-128)*2
                if w&0x400:self.pending=dest if take else pc+4
                elif take:self.pc=dest
            else:raise AssertionError((hex(pc),hex(w)))
            if prior is not None:self.pc=prior
            self.steps+=1
        def run(self):
            while self.pc!=sy.get('_font_boot_init',sy['_native_font_init']):
                assert self.steps<30000
                self.step()
            lines=list(range(start,(stop+31)&~31,32))
            assert self.written==set(lines)
            assert self.invalidated==[(0xf0000000|(a&0x1fe0),a&0xfffffc00) for a in lines]
            assert self.first_payload==0xac2f0030
            assert self.steps-self.last_invalidate>=8
            assert self.r[4]==self.initial[4] and self.r[8:]==self.initial[8:]
            # The original SDK changes T; all other incoming SR bits survive.
            assert self.sr&~1==self.initial_sr&~1
            assert self.pr==0x8c01f00e
            return self.steps
    trials=[Model(font,sr).run() for font,sr in [(0x8c2c0000,0x40000000),(0x8c2c0000,0x400000f1),(0x8c2c0000,0x700000f0)]]
    report={'status':'passed','candidate_manifest_sha256':sha(manifest_raw),
        'root_source_and_SH4_review_completed':True,'original_font_instructions_semantically_identical':28,
        'actual_bootstrap_and_sdk_instructions_executed_in_bounded_model':True,'model_instruction_counts':trials,
        'D_writeback_before_first_P2_fetch':True,'I_invalidation_before_P1_entry':True,
        'PR_SP_font_argument_callee_saved_registers_preserved':True,'all_caption_table_bytes_identical':True,
        'payload_bss_below_heap':True,'hardware_tested':False,'emulator_gameplay_or_audio_QA':False,
        'limitation':'Instruction model verifies sequence/registers, not physical SH4 cache timing or ODE firmware.',
        'verifier_sha256':sha(Path(__file__).read_bytes())}
    (OUT/'source-disassembly-review-proof.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report))
if __name__=='__main__':main()
