# 패치 전후 SHA-256

대상은 **Dreamcast 일본판 Space Channel 5 Part 2 (Japan), CUE + BIN 3개**입니다. 파일 이름·바이트 수·SHA-256이 모두 일치해야 합니다. 아래 값은 V1.1 배포 적용기로 직접 만든 결과와 최신 작업본을 비교하여 확인했습니다.

**변경되는 파일은 Track 3입니다. Track 1, Track 2, CUE는 원본과 바이트가 같습니다.** 각 해시는 전체 파일을 대상으로 계산한 SHA-256입니다.

| 파일 | 크기 (바이트) | 변경 여부 |
| --- | ---: | --- |
| `Space Channel 5 Part 2 (Japan) (Track 1).bin` | 1,980,384 | 동일 |
| `Space Channel 5 Part 2 (Japan) (Track 2).bin` | 2,076,816 | 동일 |
| `Space Channel 5 Part 2 (Japan) (Track 3).bin` | 1,185,760,800 | 변경 |
| `Space Channel 5 Part 2 (Japan).cue` | 384 | 동일 |

## Space Channel 5 Part 2 (Japan) (Track 1).bin

패치 전 — 일본판 원본

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

패치 후 — 비공식 한글판 V1.1

```text
0253b2fb053cd253cec3a114be98359c6fc8c5be25c84acbfc3bcf732c2fbb17
```

## Space Channel 5 Part 2 (Japan) (Track 2).bin

패치 전 — 일본판 원본

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

패치 후 — 비공식 한글판 V1.1

```text
98738afbc741875fcdb5e5fe695cadfb60e492b66820b1e901ba2254f226c203
```

## Space Channel 5 Part 2 (Japan) (Track 3).bin

패치 전 — 일본판 원본

```text
af9f53094aee1c3cba1cda183b0a60710732ec81c7e32a39e9127d816709a29f
```

패치 후 — 비공식 한글판 V1.1

```text
3c73a2e38f7ce2b674d71ee230f71e84102232a78acb8863c6081166fb76e398
```

## Space Channel 5 Part 2 (Japan).cue

패치 전 — 일본판 원본

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

패치 후 — 비공식 한글판 V1.1

```text
055f8098a992cda53aaee073dea1c8aa0dd0211c273a0ad3f408f92afccf904f
```

## 패치 파일과 적용기 자체의 해시

이 값은 게임 이미지 해시와 다른 값입니다. 아래 파일은 ZIP 안에 들어 있습니다.

| 파일 | 크기 (바이트) | SHA-256 |
| --- | ---: | --- |
| `SC5P2KR.patch.gz` | 21,412,269 | `0e2976bf46545ab33a5bb351a976ff8eef8e51976d6b51ec87a6140b56ee1284` |
| `SC5Part2KoreanPatch_v1.1.exe` | 21,504 | `73ab9576429fa42c0c24082ffb4328402043a18da153829c3cb5c1e9bd591d88` |

ZIP 자체의 SHA-256은 [SHA256SUMS.txt](SHA256SUMS.txt) 및 릴리스 첨부 파일에서 확인할 수 있습니다. JSON이 필요한 경우 [original-and-output-hashes.json](original-and-output-hashes.json)을 사용하세요.

## Windows에서 직접 비교

PowerShell에서 검사할 폴더를 열고 다음 명령을 실행합니다.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'Space Channel 5 Part 2 (Japan) (Track 3).bin' | Format-List
```

전체 4개 파일을 검사하려면:

```powershell
$gameFiles = @(
  'Space Channel 5 Part 2 (Japan) (Track 1).bin',
  'Space Channel 5 Part 2 (Japan) (Track 2).bin',
  'Space Channel 5 Part 2 (Japan) (Track 3).bin',
  'Space Channel 5 Part 2 (Japan).cue'
)
$gameFiles | ForEach-Object { Get-FileHash -Algorithm SHA256 -LiteralPath $_ } | Format-List
```

출력된 영문 대소문자는 비교 결과에 영향을 주지 않습니다. CHD/GDI/ZIP 같은 다른 컨테이너의 해시는 BIN 해시와 다릅니다. 특히 CUE는 같은 트랙을 가리키더라도 공백과 줄바꿈만 달라져도 해시가 달라집니다.

[설치 방법](INSTALL.md) · [검증 범위](VERIFICATION.md) · [처음으로](../README.md)
