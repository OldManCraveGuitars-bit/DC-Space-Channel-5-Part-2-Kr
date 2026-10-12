"""Build a separate, incomplete menu/font trial disc with verified Mode 1 ECC."""
from pathlib import Path
import sys,json,hashlib,shutil,struct,argparse,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sc5.disc import GDImage,SECTOR,PAYLOAD
from sc5.sector import update_mode1,verify_mode1
from sc5.texture_edits import edits_hash

def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--options-probe',action='store_true');parser.add_argument('--judgment-menu',action='store_true');parser.add_argument('--menu-images',action='store_true');parser.add_argument('--texture-edits',action='store_true');parser.add_argument('--subtitle-style',action='store_true');parser.add_argument('--output-name');parser.add_argument('--settings-core-dir',default='settings-core');parser.add_argument('--stream-copy',action='store_true',help='Copy original bytes in bounded buffers, retaining destination NTFS compression')
    parser.add_argument('--movie-video-build',help='Hash-bound project movie-video-prototype build to preserve in the disc')
    args=parser.parse_args()
    if args.output_name and (not args.output_name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.output_name)):parser.error('Invalid output name')
    if not args.settings_core_dir or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.settings_core_dir):parser.error('Invalid settings core directory')
    if args.movie_video_build and any(not(c.isalnum() or c in '-_') for c in args.movie_video_build):parser.error('Invalid movie video build name')
    spec=json.loads((ROOT/'data/source-hashes.json').read_text('utf-8'))
    source=Path(spec['source']);out=ROOT/'work'/(args.output_name or ('judgment-menu-test-disc' if args.judgment_menu else 'options-test-disc' if args.options_probe else 'menu-test-disc'));out.mkdir(exist_ok=True)
    asset=ROOT/'work/menu-prototype'
    caption_manifest=json.loads((asset/'manifest.json').read_text('utf-8'))
    caption_names={item['name'] for item in caption_manifest['files']}
    assets={name:asset/name for name in ('ZENFONT.GD',)}
    for item in caption_manifest['files']:
        name=item['name']
        if name!=Path(name).name or not name.endswith('.BIN'):raise ValueError('Invalid caption asset name')
        assets[name]=asset/name
        if digest(assets[name])!=item['new_sha256']:raise ValueError('Caption payload mismatch')
    movie_manifest=None
    ctl_manifest=None
    if caption_manifest.get('ctl_text_draft_lines'):
        ctl_dir=ROOT/'work/ctl-text-prototype'
        ctl_manifest=json.loads((ctl_dir/'manifest.json').read_text('utf-8'))
        if ctl_manifest['font_base_sha256']!=digest(asset/'ZENFONT.GD'):raise ValueError('CTL/font mismatch')
        for item in ctl_manifest['files']:
            path=ctl_dir/item['name']
            if item['name']!='CTL_TEXT.AFS' or digest(path)!=item['sha256']:raise ValueError('CTL payload mismatch')
            assets[item['name']]=path
    if caption_manifest.get('embedded_files'):
        movie_dir=ROOT/'work/movie-caption-prototype'
        movie_manifest=json.loads((movie_dir/'manifest.json').read_text('utf-8'))
        if movie_manifest['font_base_sha256']!=digest(asset/'ZENFONT.GD'):raise ValueError('Movie caption/font mismatch')
        for item in movie_manifest['files']:
            name=item['name'];path=movie_dir/name
            if name!=Path(name).name or not name.endswith('.AFS'):raise ValueError('Invalid embedded caption archive')
            if digest(path)!=item['sha256']:raise ValueError('Movie caption archive payload mismatch')
            assets[name]=path
    image_manifest=None
    if args.menu_images:
        image_manifest=json.loads((ROOT/'work/menu-image-prototype/manifest.json').read_text('utf-8'))
        for item in image_manifest['files']:
            path=ROOT/'work/menu-image-prototype'/item['name']
            if digest(path)!=item['sha256']:raise ValueError('Menu image payload mismatch')
            assets[item['name']]=path
    texture_manifest=None
    if args.texture_edits:
        texture_manifest=json.loads((ROOT/'work/texture-edit-prototype/manifest.json').read_text('utf-8'))
        current_edits=json.loads((ROOT/'data/edits.json').read_text('utf-8')).get('images',{})
        if texture_manifest.get('texture_edits_sha256')!=edits_hash(current_edits):raise ValueError('PNG imports changed; rebuild texture edits')
        if not texture_manifest.get('source_hashes_verified'):raise ValueError('Texture edit source verification missing')
        if texture_manifest.get('with_menu_images')!=args.menu_images:raise ValueError('Texture edit/menu base mismatch; rebuild texture edits with matching --with-menu-images')
        for item in texture_manifest['files']:
            name=item['name'];path=ROOT/'work/texture-edit-prototype'/name
            if name!=Path(name).name or not name.endswith('.PVM'):raise ValueError('Invalid texture edit archive')
            if digest(path)!=item['sha256']:raise ValueError('Texture edit payload mismatch')
            if item.get('menu_base_sha256'):
                base=next((row for row in image_manifest['files'] if row['name']==name),None)
                if not base or base['sha256']!=item['menu_base_sha256']:raise ValueError('Texture edit menu build changed')
            assets[name]=path
    if args.options_probe:
        assets['TITLE.BIN']=ROOT/'work/judgment-research/TITLE.BIN'
    if args.judgment_menu:
        assets['TITLE.BIN']=ROOT/'work/judgment-menu/TITLE.BIN'
    settings=None
    if args.options_probe or args.judgment_menu:
        core_dir=ROOT/'work'/args.settings_core_dir
        settings=json.loads((core_dir/'manifest.json').read_text('utf-8'))
        assets['ZENFONT.GD']=core_dir/'ZENFONT.GD'
        assets['1ST_READ.BIN']=core_dir/'1ST_READ.BIN'
        if digest(assets['ZENFONT.GD'])!=settings['font_sha256']:raise ValueError('Settings font mismatch')
        if digest(assets['1ST_READ.BIN'])!=settings['main_sha256']:raise ValueError('Settings main mismatch')
        if hashlib.sha256((asset/'ZENFONT.GD').read_bytes()).hexdigest()!=settings['font_base_sha256']:raise ValueError('Caption/font build mismatch')
        menu_manifest=ROOT/('work/judgment-menu/manifest.json' if args.judgment_menu else 'work/judgment-research/options-probe-manifest.json')
        entrypoints=json.loads(menu_manifest.read_text('utf-8')).get('settings_entrypoints')
        if not entrypoints:raise ValueError('Rebuild menu to verify settings core entrypoints')
        if any(settings['symbols'].get(name)!=address for name,address in entrypoints.items()):raise ValueError('Menu/settings core entrypoint mismatch')
    subtitle_style=None
    if args.subtitle_style:
        if settings is None:raise ValueError('Subtitle style requires a verified settings main')
        subtitle_style=json.loads((ROOT/'work/subtitle-style/manifest.json').read_text('utf-8'))
        if subtitle_style['settings_main_sha256']!=settings['main_sha256']:raise ValueError('Subtitle style settings input mismatch')
        assets['1ST_READ.BIN']=ROOT/'work/subtitle-style/1ST_READ.BIN'
        if digest(assets['1ST_READ.BIN'])!=subtitle_style['main_sha256']:raise ValueError('Subtitle style payload mismatch')
    reused_source_copies=[]
    for entry in spec['files']:
        path=source/entry['name']
        if path.stat().st_size!=entry['size'] or digest(path)!=entry['sha256']:
            raise ValueError(f'Original hash mismatch: {path.name}')
        destination=out/path.name
        if args.stream_copy:
            if destination.resolve()==path.resolve():raise ValueError('Original and output paths must differ')
            if destination.exists() and destination.stat().st_size==entry['size'] and digest(destination)==entry['sha256']:
                reused_source_copies.append(path.name)
            else:
                with path.open('rb') as reader,destination.open('wb') as writer:
                    while chunk:=reader.read(1024*1024):
                        writer.write(chunk)
                        writer.flush();os.fsync(writer.fileno())
                shutil.copystat(path,destination)
        else:
            shutil.copy2(path,destination)
        if destination.stat().st_size!=entry['size'] or digest(destination)!=entry['sha256']:
            raise ValueError('Copied source bytes differ: '+path.name)
    changes={};proof=[];allocations=[];movie_video_composition=None
    with GDImage(source) as disc:
        entries={e.name:e for e in disc.entries()}
        if args.movie_video_build:
            from sc5.movie_edits import compose_opening_namecards
            e=entries['MAKUMA.AFS'];original_movie_archive=disc.read(e.lba,e.size)
            base=assets['MAKUMA.AFS'].read_bytes() if 'MAKUMA.AFS' in assets else original_movie_archive
            merged,movie_video_composition=compose_opening_namecards(original_movie_archive,base,
                ROOT/'work/movie-video-prototype'/args.movie_video_build)
            video_assets=out/'verified-movie-assets';video_assets.mkdir(exist_ok=True)
            path=video_assets/'MAKUMA.AFS';assert not path.exists();path.write_bytes(merged)
            assets['MAKUMA.AFS']=path
        free=max(e.lba+(e.size+2047)//2048 for e in entries.values())
        # GD-ROM boot data must end before the final 150-sector run-out.
        # The main executable already ends there; that run-out is not free
        # space for expanded TITLE/font/texture files (V1.104 hardware fix).
        data_limit=45000+disc.track3_sectors-150
        tail_available=max(0,data_limit-free)
        tail_required=sum((path.stat().st_size+2047)//2048 for name,path in assets.items()
                          if not name.endswith('.PVM') and
                          (name=='ZENFONT.GD' or path.stat().st_size>(entries[name].size+2047)//2048*2048))
        # A whole-game source table grows the font/core container beyond the
        # original tail allowance. Preserve the track length by moving that
        # container into an independently checked empty prefix extent.
        font_in_prefix=tail_required>tail_available
        # The source places all ordinary files on the outer part of the GD.
        # After the ISO directory, reserve only source sectors proven empty.
        prefix_free=max(45032,disc.root_lba+(disc.root_size+2047)//2048)
        prefix_limit=min(e.lba for e in entries.values())
        directory=bytearray(disc.read(disc.root_lba,disc.root_size))
        for name,path in assets.items():
            e=entries[name];raw=path.read_bytes()
            if name in caption_names:
                caption=next(item for item in caption_manifest['files'] if item['name']==name)
                if hashlib.sha256(disc.read(e.lba,e.size)).hexdigest()!=caption['original_sha256']:raise ValueError('Caption source mismatch')
            if movie_manifest and name.endswith('.AFS'):
                item=next((item for item in movie_manifest['files'] if item['name']==name),None)
                if item and hashlib.sha256(disc.read(e.lba,e.size)).hexdigest()!=item['source_sha256']:raise ValueError('Movie caption archive source mismatch')
            if ctl_manifest and name=='CTL_TEXT.AFS':
                if hashlib.sha256(disc.read(e.lba,e.size)).hexdigest()!=ctl_manifest['files'][0]['source_sha256']:raise ValueError('CTL archive source mismatch')
            if name=='TITLE.BIN':
                native=json.loads((ROOT/('work/judgment-menu/manifest.json' if args.judgment_menu else 'work/judgment-research/options-probe-manifest.json')).read_text('utf-8'))
                if hashlib.sha256(disc.read(e.lba,e.size)).hexdigest()!=native['source_sha256']:raise ValueError('Native source mismatch')
                if digest(path)!=native['title_sha256']:raise ValueError('Native payload mismatch')
                if not native.get('settings_core_required'):raise ValueError('Settings dependency missing')
            if name=='1ST_READ.BIN':
                if hashlib.sha256(disc.read(e.lba,e.size)).hexdigest()!=settings['main_source_sha256']:raise ValueError('Settings main source mismatch')
            if image_manifest and name.endswith('.PVM'):
                image_source=next((item for item in image_manifest['files'] if item['name']==name),None)
                if image_source and hashlib.sha256(disc.read(e.lba,e.size)).hexdigest()!=image_source['source_sha256']:raise ValueError('Menu image source mismatch')
            if texture_manifest and name.endswith('.PVM'):
                texture_source=next((item for item in texture_manifest['files'] if item['name']==name),None)
                if texture_source and hashlib.sha256(disc.read(e.lba,e.size)).hexdigest()!=texture_source['source_sha256']:raise ValueError('Texture edit source mismatch')
            if name=='ZENFONT.GD' or len(raw)>(e.size+2047)//2048*2048:
                count=(len(raw)+2047)//2048
                if name.endswith('.PVM') or (name=='ZENFONT.GD' and font_in_prefix) or free+count>data_limit:
                    lba=prefix_free
                    if lba+count>prefix_limit:raise ValueError('Expanded atlas exceeds unused ISO prefix')
                    blank=disc.read(lba,count*2048)
                    if len(blank)!=count*2048 or any(blank):raise ValueError('Expanded atlas prefix is not empty')
                    prefix_free+=count
                    allocations.append({'name':name,'lba':lba,'sectors':count,
                                        'reason':'font/core exceeds combined tail capacity' if name=='ZENFONT.GD' else 'expanded texture',
                                        'source_payloads_all_zero':True,
                                        'source_payloads_sha256':hashlib.sha256(blank).hexdigest()})
                else:
                    lba=free;free+=count
                if lba+count>data_limit:raise ValueError('Expanded file crosses reserved GD-ROM run-out')
                # Never overwrite a file extent in the original disc.
                for other in entries.values():
                    if lba<other.lba+(other.size+2047)//2048 and lba+count>other.lba:raise ValueError('Extent overlap')
            else:
                if len(raw)>(e.size+2047)//2048*2048:raise ValueError('Menu prototype exceeds original extent')
                lba=e.lba
                if name!='TITLE.BIN':raw=raw.ljust(e.size,b'\0')
            if lba!=e.lba or len(raw)!=e.size:
                pos=0;found=0
                while pos<len(directory):
                    size=directory[pos]
                    if not size:pos=(pos//2048+1)*2048;continue
                    filename=bytes(directory[pos+33:pos+33+directory[pos+32]]).split(b';')[0]
                    if filename==name.encode('ascii'):
                        found+=1
                        for offset,value in ((2,lba),(10,len(raw))):
                            struct.pack_into('<I',directory,pos+offset,value);struct.pack_into('>I',directory,pos+offset+4,value)
                    pos+=size
                if found!=1:raise ValueError('Expected one directory record')
            for i in range((len(raw)+2047)//2048):
                payload=raw[i*2048:(i+1)*2048].ljust(2048,b'\0')
                if disc.read(lba+i,2048)!=payload:changes[lba+i]=payload
            proof.append({'name':name,'source_lba':e.lba,'new_lba':lba,'bytes':len(raw),'asset_sha256':digest(path)})
        original_dir=disc.read(disc.root_lba,disc.root_size)
        for i in range((len(directory)+2047)//2048):
            data=bytes(directory[i*2048:(i+1)*2048]).ljust(2048,b'\0')
            if data!=original_dir[i*2048:(i+1)*2048].ljust(2048,b'\0'):changes[disc.root_lba+i]=data
        target=out/disc.track3.name
        with target.open('r+b') as f:
            for lba,payload in sorted(changes.items()):
                f.seek((lba-45000)*SECTOR);original=f.read(SECTOR)
                updated=update_mode1(original,payload)
                if not verify_mode1(updated):raise AssertionError('ECC verification failed')
                f.seek((lba-45000)*SECTOR);f.write(updated)
        with GDImage(out) as trial:
            patched={e.name:e for e in trial.entries()}
            for item in proof:
                e=patched[item['name']];expected=assets[e.name].read_bytes()
                if trial.read(e.lba,len(expected))!=expected:raise AssertionError('Patched ISO reread mismatch')
    report={'status':'incomplete trial; full voice/movie subtitles and broad gameplay/VMU verification still pending','native_option_control_prototype':args.options_probe or args.judgment_menu,'native_korean_menu_prototype':args.judgment_menu,'native_judgment_hook_included':settings is not None and settings.get('native_judgment_hook_included',False),'korean_menu_images_included':args.menu_images,'native_caption_style_included':subtitle_style is not None,'native_caption_background_alpha':subtitle_style['background_alpha'] if subtitle_style else None,'persistent_settings_core_included':settings is not None,'vmu_auto_save_enabled':settings is not None and settings['vmu_enabled_by_default'],'source_hashes_verified':True,'source_unchanged':True,'changed_sectors':len(changes),'source_empty_prefix_allocations':allocations,'files':proof,'cue':str(next(out.glob('*.cue')))}
    report['workbench_texture_edits_included']=texture_manifest is not None
    report['workbench_texture_edit_count']=len(texture_manifest['textures']) if texture_manifest else 0
    voice_settings=settings.get('voice_subtitles',{}) if settings else {}
    report['native_voice_subtitle_layer_included']=bool(voice_settings)
    report['voice_subtitle_diagnostic_drawing']=voice_settings.get('diagnostic_drawing_enabled',False)
    report['voice_subtitle_production_records']=voice_settings.get('production_subtitle_records',0)
    report['voice_source_identity_records']=voice_settings.get('source_identity_records',0)
    report['voice_source_identity_scope']=voice_settings.get('source_identity_scope')
    report['voice_source_identical_shared_groups']=voice_settings.get('shared_identity_rows',0)
    report['settings_core_dir']=args.settings_core_dir if settings else None
    report['movie_video_trial']=args.movie_video_build
    report['movie_video_composition']=movie_video_composition
    report['original_copy_mode']='bounded-stream' if args.stream_copy else 'native-copy2'
    report['copied_original_file_bytes_and_hashes_verified']=True
    report['reused_exact_original_copy_files']=reused_source_copies
    (out/'proof.json').write_text(json.dumps(report,indent=2),'utf-8');print(json.dumps(report))

if __name__=='__main__':main()
