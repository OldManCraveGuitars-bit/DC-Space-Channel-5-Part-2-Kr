"""Defer subtitle hook installation until TITLE creation, retaining approved C objects."""
import copy, hashlib, json, shutil, struct
from pathlib import Path
from build_options_probe import ROOT, run

def sha(b): return hashlib.sha256(b).hexdigest()
def write(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', 'utf8')

def main():
    base=ROOT/'work/settings-core-hardware-v1102'
    out=ROOT/'work/settings-core-hardware-v1103'
    assert not (out/'manifest.json').exists(), 'Preserve completed builds'
    out.mkdir(exist_ok=True); archive=out/'native-source'; archive.mkdir(exist_ok=True)
    mr=(base/'manifest.json').read_bytes()
    assert sha(mr)=='b50621c261913fcf9c44422a0bf7cd1aca059c3dc7bfa67f5f5b8526e389e7c4'
    m=json.loads(mr)
    original=(ROOT/'work/original/1ST_READ.BIN').read_bytes()
    assert sha(original)==m['main_source_sha256']=='05ccc4b7620871b903631cf790b47af2750e9c684abfa8b27e9fd06dcbba8383'
    main=bytearray((base/'1ST_READ.BIN').read_bytes())
    pos=0x2add6; size=56
    assert main[pos:pos+size]==(base/'font-hook.bin').read_bytes()
    # SDK function used by the bootstrap must still be the original function.
    assert main[0x63b6:0x6608]==original[0x63b6:0x6608]
    expected='e62f12ded62f224f12d3e65d441e0b43e36410d20b42036411d3061e0b43e364d82d0589264fd3640ed3f66d2b43f66e264ff66d0b00f66e'
    assert original[pos:pos+size].hex()==expected
    shutil.copy2(ROOT/'native/settings-core.S',archive/'settings-core.S')
    ld=(base/'native-source/settings-core.ld').read_text('utf8')
    ld=ld.replace(' .font_hook ', ' .title_hook 0x8c270000 : { *(.title_hook) }\n .font_hook ')
    (archive/'settings-core.ld').write_text(ld,'utf8')
    objects=['core.o','core-asm.o','judgment-phase.o','judgment-phase-asm.o','voice-subtitles.o','voice-subtitles-asm.o']
    reused=[]
    for name in objects:
        if name=='core-asm.o': continue
        shutil.copy2(base/name,out/name)
        reused.append({'file':name,'sha256':sha((out/name).read_bytes())})
    run('as','-little','-isa=sh4',archive/'settings-core.S','-o',out/'core-asm.o')
    run('ld','-EL','-T',archive/'settings-core.ld',*[out/n for n in objects],'-o',out/'core.elf')
    run('objcopy','-O','binary','--only-section=.entry','--only-section=.text','--only-section=.data',out/'core.elf',out/'core.bin')
    for section,name in [('.title_hook','title-hook.bin'),('.font_hook','font-hook.bin'),('.judgment_hook','judgment-hook.bin'),('.subtitle_extra','subtitle-extra.bin')]:
        run('objcopy','-O','binary','--only-section='+section,out/'core.elf',out/name)
    nm=run('nm','-n',out/'core.elf'); (out/'symbols.txt').write_text(nm,'utf8')
    symbols={v.split()[2]:int(v.split()[0],16) for v in nm.splitlines() if len(v.split())==3}
    (out/'disassembly.txt').write_text(run('objdump','-d',out/'core.elf'),'utf8')
    payload=(out/'core.bin').read_bytes(); hook=(out/'font-hook.bin').read_bytes()
    assert len(hook)==56 and len(payload)==symbols['_payload_code_bytes']<0x10000
    assert symbols['_settings_core_end']<m['main_heap_address']==0x8c300000
    assert struct.unpack_from('<4I',hook,26)==(0x8c2f0000,len(payload),0x8c0163b6,0xac2f0030)
    for name in ('_native_state_init','_native_vmu_tick','_native_vmu_changed','_native_font_entry','_native_judgment_phase_entry'):
        assert symbols[name]==m['symbols'][name]
    assert (out/'subtitle-extra.bin').read_bytes()==(base/'subtitle-extra.bin').read_bytes()
    assert (out/'judgment-hook.bin').read_bytes()==(base/'judgment-hook.bin').read_bytes()
    assert payload[56:60]==struct.pack('<I',symbols['_font_boot_uncached']+0x20000000)
    main[pos:pos+size]=hook; (out/'1ST_READ.BIN').write_bytes(main)
    zero_bytes=symbols['_settings_core_end']-(m['payload_address']+len(payload))
    assert zero_bytes==m['hardware_boot']['explicit_zero_BSS_bytes']
    font=(base/'ZENFONT.GD').read_bytes()[:m['font_reserve_bytes']]+payload+bytes(zero_bytes)
    (out/'ZENFONT.GD').write_bytes(font)
    result=copy.deepcopy(m)
    result.update(status='V1.103 deferred subtitle hooks; bounded source verification required; hardware untested',
        payload_bytes=len(payload),payload_sha256=sha(payload),payload_bss_end=symbols['_settings_core_end'],
        main_sha256=sha(main),font_bytes=len(font),font_sha256=sha(font),symbols=symbols,reused_objects=reused,
        accepted_object_reference=str(base.relative_to(ROOT)),accepted_object_reference_manifest_sha256=sha(mr))
    next(c for c in result['main_changes'] if c['offset']==pos).update(expected=expected,replacement=hook.hex())
    result['voice_subtitles']['diagnostics_address']=symbols['_subtitle_diagnostics']
    result['voice_subtitles']['halfwidth_font']['pointer_address']=symbols['_halfwidth_font']
    for i,h in enumerate(result['voice_subtitles']['hooks']):
        target=symbols['_native_subtitle_'+h['name']]; site=int(h['address'],16)
        prefix=struct.pack('<3H',0xd001,0x402b,9)
        template=prefix+struct.pack('<I',target)+b'\x09\x00' if site&2 else prefix+b'\x09\x00'+struct.pack('<I',target)
        offset=symbols['_subtitle_hook_templates']-m['payload_address']+i*12
        assert payload[offset:offset+12]==template
        h.update(target=hex(target),replacement=template.hex())
    result['hardware_boot'].update(code_bytes=len(payload),
        explicit_zero_BSS_bytes=zero_bytes,subtitle_install_phase='TITLE object creation at 0x8c270000',
        font_boot_calls=['state_init','original_font_init'],actual_hardware_tested=False)
    write(out/'manifest.json',result)
    write(out/'change-specification.json',{'version':'1.103','base_manifest_sha256':sha(mr),
        'reason':'Font-load initialization installed CRI hooks and began polling audio handles during the logo/startup phase. Defer installation to TITLE object creation.',
        'original_main_sha256':sha(original),'original_font_bytes':expected,'base_main_sha256':sha((base/'1ST_READ.BIN').read_bytes()),
        'changed_main_offset':pos,'bytes':56,'original_bytes':expected,
        'previous_bytes':(base/'1ST_READ.BIN').read_bytes()[pos:pos+size].hex(),'replacement_bytes':hook.hex(),
        'source_sha256':sha((archive/'settings-core.S').read_bytes()),'reused_objects':reused,
        'caption_data_identical':True,'all_C_objects_identical':True,'early_subtitle_install_removed':True,'deferred_install_entry':'_native_title_entry','title_original_prologue':'e62f224ff87f0fd3522f611f','title_replacement':(out/'title-hook.bin').read_bytes().hex(),'hardware_tested':False})
    print(json.dumps({'payload_bytes':len(payload),'bss_end':hex(symbols['_settings_core_end']),
        'font_bytes':len(font),'hook_bytes':len(hook),'status':'compiled'}))

if __name__=='__main__':main()
