# V1.104 패치 전후 SHA-256

지정된 일본판 원본에 한 번 적용하는 통합 패치입니다.

## 원본 → CUE 출력

### `Space Channel 5 Part 2 (Japan) (Track 1).bin`

크기: 1,980,384바이트

패치 전

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

V1.104 패치 후

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

### `Space Channel 5 Part 2 (Japan) (Track 2).bin`

크기: 2,076,816바이트

패치 전

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

V1.104 패치 후

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

### `Space Channel 5 Part 2 (Japan) (Track 3).bin`

크기: 1,185,760,800바이트

패치 전

```text
af9f53094aee1c3cba1cda183b0a60710732ec81c7e32a39e9127d816709a29f
```

V1.104 패치 후

```text
28df43bd4191f9f6f0a8257459f4654b4795f752ea19da89b76a2a17d3c83873
```

### `Space Channel 5 Part 2 (Japan).cue`

크기: 384바이트

패치 전

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

V1.104 패치 후

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

## GDI 출력

Track 1·3은 CUE 출력과 같은 데이터입니다. Track 2는 150섹터 프리갭만 제거합니다.

| 파일 | 크기 | SHA-256 |
| --- | ---: | --- |
| `disc.gdi` | 83 | `abb78c115a0179dfc2af5271817eb97e18baa2704253bac821bb44d8def5d5f7` |
| `track01.bin` | 1,980,384 | `0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17` |
| `track02.raw` | 1,724,016 | `ced05b98c256a32b3d0f1c565834726c378d059245496051f4896af82dbd5a97` |
| `track03.bin` | 1,185,760,800 | `28df43bd4191f9f6f0a8257459f4654b4795f752ea19da89b76a2a17d3c83873` |

## 패치·적용기

| 파일 | 크기 | SHA-256 |
| --- | ---: | --- |
| `SC5P2KR.patch.gz` | 21,415,631 | `f620dc48e48697d37c676e6307175534b477b642efcdc84ba34a8aad8c37fff9` |
| `SC5Part2KoreanPatch_v1.104.exe` | 25,088 | `91cdc9e5c0003e28d2a1cdde55df427868f558a18d2c7792f18b11da3da81d42` |

V1.103 Track 3: `581737e9d7d757eecc49a6862d06b8e879300379d0468c6a8aee4a6a053836fc`

ZIP 해시는 [SHA256SUMS.txt](SHA256SUMS.txt), 전체 값은 [JSON](original-and-output-hashes.json)에 있습니다.
