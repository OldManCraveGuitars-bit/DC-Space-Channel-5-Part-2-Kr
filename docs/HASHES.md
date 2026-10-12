# V1.103 패치 전후 SHA-256

일본판 원본에서 한 번 적용하는 통합 패치입니다. 두 출력 형식 모두 실제 배포 적용기로 생성해 확인했습니다.

## 원본 → CUE 출력

### `Space Channel 5 Part 2 (Japan) (Track 1).bin`

크기: 1,980,384바이트

패치 전

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

V1.103 패치 후

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

### `Space Channel 5 Part 2 (Japan) (Track 2).bin`

크기: 2,076,816바이트

패치 전

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

V1.103 패치 후

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

### `Space Channel 5 Part 2 (Japan) (Track 3).bin`

크기: 1,185,760,800바이트

패치 전

```text
af9f53094aee1c3cba1cda183b0a60710732ec81c7e32a39e9127d816709a29f
```

V1.103 패치 후

```text
581737e9d7d757eecc49a6862d06b8e879300379d0468c6a8aee4a6a053836fc
```

### `Space Channel 5 Part 2 (Japan).cue`

크기: 384바이트

패치 전

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

V1.103 패치 후

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

## GDI 출력

Track 1·3은 CUE 출력과 같은 데이터입니다. Track 2는 150섹터 프리갭만 제거하며 원본 오디오 바이트 순서는 유지합니다.

| 파일 | 크기 | SHA-256 |
| --- | ---: | --- |
| `disc.gdi` | 83 | `abb78c115a0179dfc2af5271817eb97e18baa2704253bac821bb44d8def5d5f7` |
| `track01.bin` | 1,980,384 | `0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17` |
| `track02.raw` | 1,724,016 | `ced05b98c256a32b3d0f1c565834726c378d059245496051f4896af82dbd5a97` |
| `track03.bin` | 1,185,760,800 | `581737e9d7d757eecc49a6862d06b8e879300379d0468c6a8aee4a6a053836fc` |

## 패치·적용기

| 파일 | 크기 | SHA-256 |
| --- | ---: | --- |
| `SC5P2KR.patch.gz` | 21,414,788 | `0f8b4678bcad20faab103328185bef877d8edfa92aec3deef565515918aad2b8` |
| `SC5Part2KoreanPatch_v1.103.exe` | 25,088 | `8e36a13a439ea8e6f3bc1294ec77b473b765e7b932f7fd361cd795301c7006c4` |

이전 V1.102의 Track 3은 `2c0182ce6b49cee69dff70bca6cf35c7f3c77610acb213ef58dda45faab07b8d`입니다.

ZIP 해시는 [SHA256SUMS.txt](SHA256SUMS.txt), 전체 전후 값은 [JSON](original-and-output-hashes.json)에 있습니다.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'disc.gdi','track01.bin','track02.raw','track03.bin' | Format-List
```
