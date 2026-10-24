"""Issue #1: revise one subtitle's data, preserving V1.104 executable bytes."""
import copy
import hashlib
import json
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_options_probe import run
from sc5.disc import GDImage, SECTOR
from sc5.gd_font import GDFont
from sc5.sector import update_mode1, verify_mode1
from sc5.subtitle_text import encode_subtitle, layout

ISSUE = 'https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Part-2-Kr/issues/1'
ID = 'R43VOICE.AFS:014'
BEFORE = '하나 더 해!'
AFTER = '한 번 더 뒤!'
SOURCE = 'もうひとつうしろ！'
BASE_HASH = '28df43bd4191f9f6f0a8257459f4654b4795f752ea19da89b76a2a17d3c83873'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    base = ROOT / 'work/settings-core-hardware-v1104'
    prior = ROOT / 'work/korean-hardware-v1104-disc'
    core = ROOT / 'work/settings-core-caption-v1105'
    disc = ROOT / 'work/korean-caption-v1105-disc'
    assert not core.exists() and not disc.exists()
    spec = json.loads((ROOT / 'data/source-hashes.json').read_bytes())
    for item in spec['files']:
        p = Path(spec['source']) / item['name']
        assert p.stat().st_size == item['size'] and digest(p) == item['sha256']
    mr = (base / 'manifest.json').read_bytes()
    assert sha(mr) == '519e20d9f5de2b0f6b681595937b5219611ff6c2e30f6ebb09db815a075c3a1c'
    m = json.loads(mr)
    gate = json.loads((base / 'source-disassembly-review-proof.json').read_bytes())
    for item in gate['files']:
        assert digest(base / item['file']) == item['sha256']
    rows = m['voice_subtitles']['production_subtitle_binding_records'] + m['voice_subtitles']['trial_subtitle_binding_records']
    matches = [i for i, row in enumerate(rows) if row['source_voice_id'] == ID]
    assert matches == [612]
    index = matches[0]
    row = rows[index]
    assert row['translation'] == BEFORE and (row['start_ms'], row['end_ms']) == (0, 1064)
    font_raw = (base / 'ZENFONT.GD').read_bytes()
    font = GDFont.read(font_raw)
    mapping = {c: int(v, 16) for c, v in json.loads((ROOT / 'work/menu-prototype/manifest.json').read_bytes())['mapping'].items()}
    old_tokens = encode_subtitle(BEFORE, font, mapping)
    tokens = encode_subtitle(AFTER, font, mapping)
    old_text = struct.pack('<' + 'H' * len(old_tokens), *old_tokens)
    new_text = struct.pack('<' + 'H' * len(tokens), *tokens)
    extra = (base / 'subtitle-extra.bin').read_bytes()
    table_address = m['symbols']['_subtitle_records']
    extra_offset = table_address - m['font_address']
    assert font_raw[extra_offset:extra_offset + len(extra)] == extra
    record_offset = index * 24
    record = struct.unpack_from('<6I', extra, record_offset)
    # The shipped table is authoritative: prior data-only revisions can retain
    # historical text-symbol labels while changing a record's text pointer.
    old_pointer = record[4]
    assert font_raw[old_pointer - m['font_address']:old_pointer - m['font_address'] + len(old_text)] == old_text
    bank_hash = 2166136261
    for c in row['bank'].lower().encode('ascii'):
        bank_hash = ((bank_hash ^ c) * 16777619) & 0xffffffff
    assert record == (bank_hash, 14, 0, 1064, old_pointer, row.get('caption_box_bottom', 392))
    # Append in verified unused loaded font storage; no new code or file growth.
    half = m['voice_subtitles']['halfwidth_font']
    assert sha(font_raw[half['font_offset']:half['font_offset'] + half['bytes']]) == half['sha256']
    new_offset = (max(extra_offset + len(extra), half['font_offset'] + half['bytes']) + 3) & ~3
    new_pointer = m['font_address'] + new_offset
    assert new_offset + len(new_text) <= m['font_reserve_bytes']
    assert not any(font_raw[new_offset:m['font_reserve_bytes']])
    updated_extra = bytearray(font_raw[extra_offset:new_offset] + new_text)
    struct.pack_into('<I', updated_extra, record_offset + 16, new_pointer)
    updated_font = bytearray(font_raw)
    updated_font[extra_offset:extra_offset + len(updated_extra)] = updated_extra
    assert len(updated_font) == len(font_raw)
    assert updated_font[:extra_offset] == font_raw[:extra_offset]
    assert updated_font[m['font_reserve_bytes']:] == font_raw[m['font_reserve_bytes']:]
    for i in range(len(rows)):
        old = struct.unpack_from('<6I', extra, i * 24)
        new = struct.unpack_from('<6I', updated_extra, i * 24)
        assert new == (old[:4] + (new_pointer,) + old[5:] if i == index else old)
    core.mkdir()
    for name in ('1ST_READ.BIN', 'core.bin', 'font-hook.bin', 'title-hook.bin', 'judgment-hook.bin'):
        shutil.copy2(base / name, core / name)
    shutil.copytree(base / 'native-source', core / 'native-source')
    (core / 'ZENFONT.GD').write_bytes(updated_font)
    (core / 'subtitle-extra.bin').write_bytes(updated_extra)
    run('objcopy', '--update-section', '.subtitle_extra=' + str(core / 'subtitle-extra.bin'),
        '--add-symbol', '_subtitle_issue1_text=.subtitle_extra:' + hex(new_offset - extra_offset) + ',local,object',
        base / 'core.elf', core / 'core.elf')
    before_disassembly = run('objdump', '-d', base / 'core.elf').splitlines()[2:]
    after_disassembly = run('objdump', '-d', core / 'core.elf').splitlines()[2:]
    assert before_disassembly == after_disassembly
    (core / 'disassembly.txt').write_text(run('objdump', '-d', core / 'core.elf'), 'utf8')
    symbols = run('nm', '-n', core / 'core.elf')
    (core / 'symbols.txt').write_text(symbols, 'utf8')
    run('objcopy', '-O', 'binary', '--only-section=.subtitle_extra', core / 'core.elf', core / 'elf-data-check.bin')
    assert (core / 'elf-data-check.bin').read_bytes() == updated_extra
    review = {k: row[k] for k in ('bank', 'member', 'source_sha256', 'sample_rate', 'sample_count', 'duration_ms', 'source_bytes')}
    review.update(id=ID, source_reviewed=True, original_audio_listened=False,
                  review_method='User-authorized correction from GitHub issue #1; previous ASR reading was incorrect.',
                  issue=ISSUE, segments=[{'start_ms': 0, 'end_ms': 1064, 'source': SOURCE, 'translation': AFTER}])
    review_path = ROOT / 'work/speech-audit/issue1-v1105/R43VOICE-014.json'
    review_path.parent.mkdir(parents=True, exist_ok=True)
    write(review_path, review)
    updated = copy.deepcopy(m)
    target = updated['voice_subtitles']['trial_subtitle_binding_records'][index - m['voice_subtitles']['production_subtitle_records']]
    assert target['source_voice_id'] == ID
    target.update(source=SOURCE, translation=AFTER, source_review_method=review['review_method'],
                  source_review_proof=str(review_path.relative_to(ROOT)), source_review_proof_sha256=digest(review_path))
    updated.update(version='1.105', status='Issue #1 text correction; V1.104 executable bytes retained',
                   font_sha256=sha(updated_font), native_code_reference_manifest_sha256=sha(mr))
    updated['symbols']['_subtitle_issue1_text'] = new_pointer
    write(core / 'manifest.json', updated)
    change = {'version': '1.105', 'issue': ISSUE, 'source_voice_id': ID, 'before': BEFORE, 'after': AFTER,
              'corrected_source': SOURCE, 'record_index': index, 'old_pointer': hex(old_pointer), 'new_pointer': hex(new_pointer),
              'font_pointer_offset': extra_offset + record_offset + 16, 'new_text_font_offset': new_offset,
              'old_text_hex': old_text.hex(), 'new_text_hex': new_text.hex(), 'layout': layout(tokens, len(font.codes)),
              'start_ms': 0, 'end_ms': 1064, 'timing_and_placement_preserved': True,
              'other_caption_records_preserved': len(rows) - 1, 'executable_bytes_unchanged': True,
              'executable_disassembly_identical': True, 'font_file_size_unchanged': True,
              'base_manifest_sha256': sha(mr), 'base_track3_sha256': BASE_HASH,
              'candidate_manifest_sha256': digest(core / 'manifest.json'), 'new_audio_or_screen_QA': False, 'hardware_tested': False}
    write(core / 'change-specification.json', change)
    write(core / 'source-disassembly-review-proof.json', dict(change, status='passed', new_executable_code_changes=False))
    # Update editable translation inputs; retain historical ASR evidence separately.
    edits_path = ROOT / 'data/edits.json'
    edits = json.loads(edits_path.read_bytes())
    e = edits['voices'][ID]
    assert e['translation'] == BEFORE
    e.update(source=SOURCE, translation=AFTER, additional_segment_source_review_proof=str(review_path.relative_to(ROOT)), status='corrected_issue1_v1105')
    e['segments'][0].update(source=SOURCE, translation=AFTER)
    write(edits_path, edits)
    source_path = ROOT / 'data/stage4-voice-gap-fix05.json'
    source_data = json.loads(source_path.read_bytes())
    def correct(value):
        if isinstance(value, dict):
            if value.get('id') == ID and 'translation' in value:
                assert value['translation'] == BEFORE
                value.update(source=SOURCE, translation=AFTER, review_note='Corrected by GitHub issue #1: directional うしろ, not imperative しろ. ' + ISSUE)
            for child in value.values():
                correct(child)
        elif isinstance(value, list):
            for child in value:
                correct(child)
    correct(source_data)
    write(source_path, source_data)
    with GDImage(prior) as source:
        assert digest(source.track3) == BASE_HASH
        entries = source.entries()
        entry = next(e for e in entries if e.name == 'ZENFONT.GD')
        assert source.read(entry.lba, entry.size) == font_raw
        changes = {}
        for i in range((entry.size + 2047) // 2048):
            before = source.read(entry.lba + i, 2048)
            chunk = updated_font[i * 2048:(i + 1) * 2048]
            after = bytes(chunk) + before[len(chunk):]
            if after != before:
                changes[entry.lba + i] = after
        assert len(changes) == 2
        disc.mkdir()
        for item in spec['files']:
            shutil.copy2(prior / item['name'], disc / item['name'])
        out_track = disc / source.track3.name
        with out_track.open('r+b') as f:
            for lba, data in changes.items():
                pos = (lba - 45000) * SECTOR
                f.seek(pos)
                raw = update_mode1(f.read(SECTOR), data)
                assert verify_mode1(raw)
                f.seek(pos)
                f.write(raw)
        actual = []
        with source.track3.open('rb') as a, out_track.open('rb') as b:
            i = 0
            while before := a.read(SECTOR * 4096):
                after = b.read(len(before))
                assert len(before) == len(after)
                if before != after:
                    for k in range(len(before) // SECTOR):
                        lo = k * SECTOR
                        if before[lo:lo + SECTOR] != after[lo:lo + SECTOR]:
                            actual.append(45000 + i + k)
                i += len(before) // SECTOR
            assert not b.read(1)
        assert sorted(actual) == sorted(changes)
        with GDImage(disc) as result:
            assert result.entries() == entries
            assert result.read(entry.lba, entry.size) == updated_font
        build = json.loads((prior / 'proof.json').read_bytes())
        build.update(status='V1.105 issue #1 correction', reference_disc=prior.name, settings_core_dir=core.name,
                     cue=str(next(disc.glob('*.cue'))), merged_core_manifest_sha256=digest(core / 'manifest.json'), changed_sectors_from_previous=len(changes))
        for item in build['files']:
            if item['name'] == 'ZENFONT.GD':
                item.update(asset_sha256=sha(updated_font), bytes=len(updated_font))
        write(disc / 'proof.json', build)
        proof = dict(change, status='passed', trial_track_sha256=digest(out_track), changed_lbas=sorted(actual),
                     changed_sectors=len(actual), all_other_raw_sectors_exact=True, all_ISO_extents_and_sizes_preserved=True,
                     changed_ISO_files=['ZENFONT.GD'], other_ISO_files_preserved=len(entries) - 1)
        write(disc / 'asset-preservation-proof.json', proof)
        print(json.dumps({'status': 'passed', 'version': '1.105', 'changed_sectors': len(actual), 'track3_sha256': proof['trial_track_sha256']}))


if __name__ == '__main__':
    main()
