# V1.102 패치 전후 SHA-256

입력은 지정된 일본판 원본 CUE+BIN 3개입니다. CUE 출력과 ODE용 GDI 출력 모두 실제 배포 EXE로 생성하여 기준 파일과 독립 대조했습니다.

## 원본 → CUE 출력

### Space Channel 5 Part 2 (Japan) (Track 1).bin

크기: **1,980,384바이트**

패치 전 — 일본판 원본

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

패치 후 — V1.102 CUE 출력

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

### Space Channel 5 Part 2 (Japan) (Track 2).bin

크기: **2,076,816바이트**

패치 전 — 일본판 원본

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

패치 후 — V1.102 CUE 출력

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

### Space Channel 5 Part 2 (Japan) (Track 3).bin

크기: **1,185,760,800바이트**

패치 전 — 일본판 원본

```text
af9f53094aee1c3cba1cda183b0a60710732ec81c7e32a39e9127d816709a29f
```

패치 후 — V1.102 CUE 출력

```text
2c0182ce6b49cee69dff70bca6cf35c7f3c77610acb213ef58dda45faab07b8d
```

### Space Channel 5 Part 2 (Japan).cue

크기: **384바이트**

패치 전 — 일본판 원본

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

패치 후 — V1.102 CUE 출력

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

## GDI 출력

`track01.bin`과 `track03.bin`은 CUE 출력의 해당 트랙과 동일합니다. `track02.raw`는 원본 Track 2에서 150섹터 프리갭만 제외합니다. `disc.gdi`는 GDI 설명 파일입니다.

| 파일 | 크기 (바이트) | SHA-256 |
| --- | ---: | --- |
| `disc.gdi` | 83 | `abb78c115a0179dfc2af5271817eb97e18baa2704253bac821bb44d8def5d5f7` |
| `track01.bin` | 1,980,384 | `0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17` |
| `track02.raw` | 1,724,016 | `ced05b98c256a32b3d0f1c565834726c378d059245496051f4896af82dbd5a97` |
| `track03.bin` | 1,185,760,800 | `2c0182ce6b49cee69dff70bca6cf35c7f3c77610acb213ef58dda45faab07b8d` |

## 패치·적용기

| 파일 | 크기 (바이트) | SHA-256 |
| --- | ---: | --- |
| `SC5P2KR.patch.gz` | 21,414,709 | `7b33525a79b21042fc6bffe819de0dd236f63ea23de81b9404b91b297e3ef85a` |
| `SC5Part2KoreanPatch_v1.102.exe` | 25,088 | `1680818558dd826b5fc649ebf4523addaf26151952e4275d139d114af5e9748b` |

V1.101의 Track 3은 `5217c7f807825f411e886ac4d76c6c60e7975589aae0dd2b1a9d23568560f435`입니다. V1.102 결과와 구분하세요.

ZIP 해시는 [SHA256SUMS.txt](SHA256SUMS.txt), 모든 원본/결과 파일 값은 [JSON](original-and-output-hashes.json)에 있습니다.

PowerShell에서 ODE 결과를 확인하는 예:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'disc.gdi','track01.bin','track02.raw','track03.bin' | Format-List
```

CUE 결과는 원래 긴 트랙 이름으로 확인합니다. ZIP과 게임 트랙, 설명 파일은 서로 다른 파일의 해시입니다.

[설치](INSTALL.md) · [부팅 수정](HARDWARE-BOOT.md) · [처음으로](../README.md)
