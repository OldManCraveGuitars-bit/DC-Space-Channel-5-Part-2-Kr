# V1.101 패치 전후 SHA-256

입력은 아래 일본판 원본 CUE+BIN 3개입니다. CUE 출력과 ODE용 GDI 출력 모두 배포 EXE로 생성하여 독립 대조했습니다.

## 원본 → CUE 출력

### Space Channel 5 Part 2 (Japan) (Track 1).bin

크기: **1,980,384바이트**

패치 전 — 일본판 원본

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

패치 후 — V1.101 CUE 출력

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

### Space Channel 5 Part 2 (Japan) (Track 2).bin

크기: **2,076,816바이트**

패치 전 — 일본판 원본

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

패치 후 — V1.101 CUE 출력

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

### Space Channel 5 Part 2 (Japan) (Track 3).bin

크기: **1,185,760,800바이트**

패치 전 — 일본판 원본

```text
af9f53094aee1c3cba1cda183b0a60710732ec81c7e32a39e9127d816709a29f
```

패치 후 — V1.101 CUE 출력

```text
5217c7f807825f411e886ac4d76c6c60e7975589aae0dd2b1a9d23568560f435
```

### Space Channel 5 Part 2 (Japan).cue

크기: **384바이트**

패치 전 — 일본판 원본

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

패치 후 — V1.101 CUE 출력

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

## GDI 출력

`track01.bin`과 `track03.bin`은 CUE 출력의 해당 트랙과 동일합니다. `track02.raw`는 원본 Track 2에서 150섹터 프리갭을 제외한 파일이며, 오디오 바이트 순서는 유지합니다. `disc.gdi`는 새 설명 파일입니다.

| 파일 | 크기 (바이트) | SHA-256 |
| --- | ---: | --- |
| `disc.gdi` | 83 | `abb78c115a0179dfc2af5271817eb97e18baa2704253bac821bb44d8def5d5f7` |
| `track01.bin` | 1,980,384 | `0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17` |
| `track02.raw` | 1,724,016 | `ced05b98c256a32b3d0f1c565834726c378d059245496051f4896af82dbd5a97` |
| `track03.bin` | 1,185,760,800 | `5217c7f807825f411e886ac4d76c6c60e7975589aae0dd2b1a9d23568560f435` |

## 패치·적용기

| 파일 | 크기 (바이트) | SHA-256 |
| --- | ---: | --- |
| `SC5P2KR.patch.gz` | 21,412,870 | `1eeee0f78d85a57edd999f659c28e09de3b84671a6e1a8f589602e5c497b9933` |
| `SC5Part2KoreanPatch_v1.101.exe` | 25,088 | `a61ca12b57fc80c27fbe63e7bbe451a75019892d771c282b6fc6e24883767f4a` |

V1.1의 Track 3 해시는 `3c73a2e38f7ce2b674d71ee230f71e84102232a78acb8863c6081166fb76e398`입니다. 위 V1.101 값과 구분하세요.

ZIP 해시는 [SHA256SUMS.txt](SHA256SUMS.txt), 전체 파일의 기계 판독용 목록은 [JSON](original-and-output-hashes.json)에 있습니다. ZIP·GDI 설명 파일·게임 트랙의 해시는 서로 다른 파일의 값입니다.

PowerShell에서 ODE 결과를 확인하는 예:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'disc.gdi','track01.bin','track02.raw','track03.bin' | Format-List
```

CUE 결과를 확인할 때는 원래 긴 트랙 파일 이름을 사용합니다. 공백·줄바꿈도 CUE와 GDI 해시에 포함됩니다.

[설치](INSTALL.md) · [부팅 변경](HARDWARE-BOOT.md) · [처음으로](../README.md)
