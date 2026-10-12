# V1.102 설치 방법

Dreamcast 일본판 **Space Channel 5 Part 2 (Japan)**의 지정된 원본 CUE 1개와 BIN 3개, Windows/.NET Framework 4.x, 약 2GB 이상의 여유 공간이 필요합니다. 이 배포물에는 게임 원본·완성 ROM·BIOS가 없습니다.

1. [V1.102 릴리스](https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Part-2-Kr/releases/tag/v1.102)에서 **`DC-Space-Channel-5-Part-2-Kr-v1.102-Patch.zip`**을 받고 전부 압축을 풉니다. `Source code` ZIP은 설치용 패치가 아닙니다.
2. **`SC5Part2KoreanPatch_v1.102.exe`**를 실행합니다. EXE와 `SC5P2KR.patch.gz`는 같은 폴더에 둡니다.
3. 원본 CUE를 선택하고, 원본 폴더 밖의 아직 없는 새 결과 폴더를 지정합니다.
4. **GDEMU / MODE 등 ODE에서는 기본값인 GDI**를 선택합니다. 기존 형식이 필요하면 CUE+BIN을 선택합니다.
5. 적용을 누릅니다. 원본·패치·최종 결과의 해시가 맞을 때만 결과 폴더가 완성됩니다.
6. GDI 결과의 **아래 4개 파일을 함께** 기기의 게임 폴더에 넣습니다. GDEMU는 기존 카드의 다음 게임용 숫자 폴더를 사용하세요. `disc.gdi`만 복사하거나 파일 확장자만 바꾸지 마세요.

```text
GDI 결과/
  disc.gdi
  track01.bin
  track02.raw
  track03.bin
```

입력 원본의 이름은 아래와 같아야 합니다. 적용기는 이 네 파일의 크기와 SHA-256을 검사합니다.

```text
원본 폴더/
  Space Channel 5 Part 2 (Japan).cue
  Space Channel 5 Part 2 (Japan) (Track 1).bin
  Space Channel 5 Part 2 (Japan) (Track 2).bin
  Space Channel 5 Part 2 (Japan) (Track 3).bin
```

**V1.1/V1.101 수정본에 덧씌우지 말고 일본판 원본에서 V1.102를 한 번 적용**합니다. 기존 결과 폴더와 원본은 덮어쓰지 않습니다. GDI/CHD만 보유한 경우 이 적용기의 입력 해시와 형식이 일치하지 않으며, 이름만 바꿔 적용할 수 없습니다.

CUE 출력은 원래 긴 파일 이름을 유지합니다. 결과 폴더의 CUE를 실행하세요. GDI 출력은 CUE 파일을 포함하지 않습니다. `track03.bin`의 데이터는 CUE 출력의 Track 3 BIN과 동일하며, Track 2는 150섹터 프리갭만 제거합니다. 원래 오디오의 바이트 순서는 바꾸지 않습니다.

기존 게임 진행 VMU 파일과 판정 설정 저장은 유지됩니다. 새 이미지를 처음부터 부팅하고 게임 내 저장을 불러오세요. 판정 설정 조작·시간 범위·VMU 저장은 [상세 안내](JUDGMENT.md)를 참고하세요.

## 오류 대응

| 상황 | 확인할 내용 |
| --- | --- |
| 원본 해시가 다름 | 다른 덤프 또는 수정본일 수 있습니다. [원본 해시](HASHES.md)를 확인하세요. CUE의 줄바꿈·공백도 해시에 포함됩니다. |
| 결과 폴더가 이미 있음 | 아직 없는 새 결과 폴더를 지정하세요. |
| 패치 파일 검사 실패 | ZIP을 다시 받고 EXE와 패치를 같은 버전으로 맞추세요. |
| ODE에 게임이 보이지 않음 | GDI 출력 4개 파일이 같은 게임 폴더에 있는지 확인하세요. |
| SEGA 로고 뒤 멈춤이 계속됨 | [V1.102 확인 범위](HARDWARE-BOOT.md)와 Track 3 해시를 확인하세요. 실제 기기 종류와 재현 결과는 Issues에 남길 수 있습니다. |

**V1.101의 실기 재시험에서 같은 정지가 보고됐습니다. V1.102의 해결 여부는 아직 미확인입니다.** V1.102는 추가 자막의 BIOS 글꼴 접근을 제거하고 메모리 초기화·실행 코드 설치 순서를 보강한 버전입니다.

패키지에는 적용기, 차이 패치, 설치·해시·판정·부팅 수정 안내, 배포 명세와 CUE/GDI 적용 검사 기록, 글꼴 라이선스가 포함됩니다.

[패치 전후 해시](HASHES.md) · [판정 설정 상세](JUDGMENT.md) · [스크린샷](GALLERY.md) · [처음으로](../README.md)
