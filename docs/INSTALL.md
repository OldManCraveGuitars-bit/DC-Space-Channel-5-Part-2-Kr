# 설치 방법

## 준비물

- Dreamcast 일본판 **Space Channel 5 Part 2 (Japan)**의 원본 CUE 1개와 BIN 3개.
- [V1.1 릴리스](https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Part-2-Kr/releases/tag/v1.1)의 **`DC-Space-Channel-5-Part-2-v1.1-Patch.zip`**.
- Windows와 .NET Framework 4.x 실행 환경.
- 결과 이미지를 만들 여유 공간 약 **2GB 이상**. 결과 4개 파일의 합계는 1,189,818,384바이트입니다.

이 배포물은 차이 패치와 적용기입니다. 게임 원본·완성 ROM·BIOS는 포함하지 않습니다. 다른 지역판, PC판, PS2판, 1편, 이전 한글 패치본에 적용하는 용도가 아닙니다.

## 순서

1. ZIP을 **폴더에 전부 압축 해제**합니다. 적용기 EXE와 `SC5P2KR.patch.gz`를 같은 폴더에 둡니다.
2. `SC5Part2KoreanPatch_v1.1.exe`를 실행합니다.
3. **원본 CUE / 폴더**에서 원본 CUE를 선택합니다. 동일 폴더에 아래 이름의 BIN 3개가 있어야 합니다.
4. **새 결과 폴더**를 지정합니다. 원본 폴더 밖의 **아직 존재하지 않는 새 폴더 이름**을 사용합니다.
5. **패치 적용**을 누르고 완료 메시지를 기다립니다. 원본 파일과 패치 파일의 해시를 검사하고, 새 결과를 만든 뒤 결과 해시까지 검사합니다.
6. 결과 폴더의 **`Space Channel 5 Part 2 (Japan).cue`**를 실행합니다. 원본 CUE와 혼동하지 않도록 결과 폴더를 확인해 주세요.
7. 옵션에서 원하는 **판정 설정** 단계를 선택합니다. 초기값은 원작과 같은 **1**입니다. 기존 노래 가사를 표시하려면 **가사 켜기**를 사용합니다.

```text
원본 폴더/
  Space Channel 5 Part 2 (Japan).cue
  Space Channel 5 Part 2 (Japan) (Track 1).bin
  Space Channel 5 Part 2 (Japan) (Track 2).bin
  Space Channel 5 Part 2 (Japan) (Track 3).bin
```

적용기는 원본을 읽기 전용으로 열고 결과를 별도 폴더에 만듭니다. 기존 결과 폴더를 덮어쓰지 않습니다. **구버전에서 갱신할 때도 일본판 원본부터 V1.1을 새로 적용**해 주세요. 단계별로 이전 패치를 먼저 적용할 필요가 없습니다.

게임 내 저장은 기존 가상 VMU를 그대로 사용하여 이어갈 수 있습니다. 패치 교체 후에는 새로 부팅하고 게임 내 LOAD를 사용해 주세요. 이전 버전에서 만든 에뮬레이터 상태 저장은 이전 메모리를 함께 되살릴 수 있습니다.

## 자주 만나는 적용 오류

| 상황 | 확인할 내용 |
| --- | --- |
| 원본 파일이 필요하다고 나옴 | CUE와 3개 BIN의 이름, 위치, 크기를 확인하세요. |
| 원본 해시가 다름 | 다른 덤프·수정본일 수 있습니다. [원본 해시 표](HASHES.md)와 비교하세요. CUE의 줄바꿈이나 공백 변경도 해시를 바꿉니다. |
| 결과 폴더가 이미 있음 | 기존 폴더를 고르지 말고 새 이름을 지정하세요. |
| 패치 파일 검사가 실패함 | ZIP을 다시 내려받고 전부 압축 해제하세요. 다른 버전의 EXE와 패치를 섞지 마세요. |
| CHD/GDI만 가지고 있음 | 이 적용기의 입력은 지정된 CUE+3BIN입니다. 확장자를 바꾸는 것으로 변환되지 않습니다. |
| 게임이 기존 언어로 실행됨 | 새 결과 폴더의 CUE를 실행했는지 확인하세요. |

CHD나 GDI의 해시는 이 릴리스의 BIN 해시와 직접 비교할 수 없습니다. 다른 형식으로 변환하기 전에 CUE+BIN 결과 해시를 확인해 주세요. 변환 도구는 이 배포물에 포함하지 않습니다.

## 패키지 구성

| 파일 | 용도 |
| --- | --- |
| `SC5Part2KoreanPatch_v1.1.exe` | Windows 패치 적용기 |
| `SC5P2KR.patch.gz` | V1.1 차이 패치 |
| `README.txt` | 압축 해제 후 읽는 설치 안내 |
| `manifest.json` | 버전, 파일 크기, 패치와 적용기 해시, 원본/결과 해시 |
| `original-and-output-hashes.json` | 원본과 결과의 파일별 SHA-256 |
| `HASHES.md`, `JUDGMENT.md` | 해시와 판정 설정 설명 |
| `patch-roundtrip.json` | 배포 적용기로 4개 파일 생성·검사한 기록 |
| `THIRD_PARTY_NOTICES.md`, `licenses/` | 글꼴 출처와 라이선스 |

[판정 설정 자세히](JUDGMENT.md) · [스크린샷](GALLERY.md) · [처음으로](../README.md)
