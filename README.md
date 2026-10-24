# DC-Space-Channel-5-Part-2-Kr

## 스페이스 채널 5 파트 2 · 비공식 한글판 정식 버전 V1.105

**Dreamcast / 일본판 기반 / KOREAN LOCALIZATION BY GIKAKNO**

![스페이스 채널 5 파트 2 한글판 타이틀](docs/screenshots/01-title.png)

Space Channel 5 Part 2의 메뉴와 설명, 대사·영상 자막, 후반부와 엔딩 가사를 한국어로 즐길 수 있도록 만든 비공식 패치입니다. 원래 음성과 영문 로고의 분위기를 살리고, 게임 안에 한국어 표시와 **6단계 판정 설정**을 추가했습니다.

**[V1.105 다운로드](https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Part-2-Kr/releases/tag/v1.105)** · **[패치 ZIP 바로 받기](https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Part-2-Kr/releases/download/v1.105/DC-Space-Channel-5-Part-2-Kr-v1.105-Patch.zip)**

[설치 방법](docs/INSTALL.md) · [판정 설정 상세](docs/JUDGMENT.md) · [스크린샷 16장](docs/GALLERY.md) · [패치 전후 해시](docs/HASHES.md) · [변경 내역](CHANGELOG.md)

## 배포 정보

| 항목 | 내용 |
| --- | --- |
| 버전 | **V1.105 · 비공식 한글판 정식 버전** |
| 기종 | SEGA Dreamcast |
| 대상 원본 | **Space Channel 5 Part 2 (Japan)**, CUE 1개 + BIN 3개 |
| 한국어화 | **GIKAKNO** |
| 배포 형태 | Windows 적용기 + 차이 패치 + 설치·해시 안내 |
| 판정 설정 | **1~6단계**, 기본값 1, VMU 자동 저장 |
| 원작 음성 | 유지 · 추가 한국어 자막 |

게임 원본·완성 ROM·BIOS는 포함하지 않습니다. 지정된 일본판 원본이 필요합니다. 이전 한글 패치본에 덧씌우지 말고 원본에서 V1.105를 한 번 적용해 주세요.

## V1.105 · 스테이지 4 오역 수정

스테이지 4에서 마이클을 구출한 뒤 퍼지·로봇과 싸우는 구간의 방향 지시를 수정했습니다.

| 이전 | V1.105 |
| --- | --- |
| 하나 더 해! | **한 번 더 뒤!** |

원문의 `もうひとつうしろ`는 뒤쪽 방향을 지시하는 말입니다. [오역 제보 #1](https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Part-2-Kr/issues/1)을 반영했습니다. 자막 시간·위치·투명도는 유지됩니다.

[변경 내용과 확인 범위](docs/TRANSLATION-FIX-V1105.md)

## 포함된 한글화 내용

- **메뉴와 안내:** 옵션, 의상실, 아이템, 리포트 설명, 결과 화면의 한국어 표시.
- **대사와 영상:** 인물 소개 이름표와 장소 표기, 플레이 중·영상 속 대사 자막, 신고된 누락 구간의 연결 보완.
- **후반부:** 퓨즈·울랄라·동료·마이클 대사, 음악에 섞인 대사와 노래·호응 구간의 자막 보완.
- **엔딩:** 엔딩송 가사, 하단 중앙 배치, 동시 대사 영역 분리, SEGA 카드의 **KOREAN LOCALIZATION BY GIKAKNO** 표기.
- **UI 수정:** 글자 테두리·잘림·정렬, 숨은 요소 발견 문구와 숫자, 판정 설정의 선택 색상 정리.
- **플레이 편의:** 원작 판정부터 양쪽으로 각각 100ms까지 넓히는 판정 설정과 별도 VMU 저장.

이 릴리스는 현재까지의 수정 사항을 묶은 통합판입니다. 최신 추가 자막의 모든 구간을 새로 재생 검수한 것은 아니므로, 반영 내용과 확인 범위는 [변경 내역](CHANGELOG.md)과 [검증 기록](docs/VERIFICATION.md)으로 구분해 안내합니다.

## 적용 방법

1. [릴리스](https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Part-2-Kr/releases/tag/v1.105)에서 **`DC-Space-Channel-5-Part-2-Kr-v1.105-Patch.zip`**을 받습니다.
2. ZIP을 전부 압축 해제하고 **`SC5Part2KoreanPatch_v1.105.exe`**를 실행합니다.
3. 원본 CUE를 선택합니다. 같은 폴더에 원본 BIN 3개가 있어야 합니다.
4. 원본 폴더 밖의 **아직 없는 새 결과 폴더**를 지정하고 **패치 적용**을 누릅니다.
5. 실기 ODE에서는 출력 형식 **GDI**를 선택합니다. 완료 후 `disc.gdi`, `track01.bin`, `track02.raw`, `track03.bin`을 함께 기기에 넣습니다. CUE 출력은 별도로 선택할 수 있습니다.

적용기는 원본·패치·결과의 해시를 검사합니다. 원본을 덮어쓰지 않으며 결과 이미지용으로 약 2GB 이상의 여유 공간을 권장합니다. 자세한 파일 이름, 오류 대응, 버전 갱신 방법은 [설치 설명](docs/INSTALL.md)을 참고해 주세요.

## 판정 설정 — 꼭 읽어 주세요

옵션 맨 아래의 **판정 설정**은 입력을 성공으로 인정하는 시간 범위입니다. **1이 원작 판정**, 숫자를 올릴수록 빠르거나 늦은 입력을 더 넓게 받아들입니다.

![판정 설정 메뉴](docs/screenshots/04-judgment-level6.png)

### “한 단계마다 20ms”의 정확한 의미

**빠른 쪽과 늦은 쪽에 각각 20ms를 추가**합니다. 한 단계를 올릴 때 전체 판정 폭은 40ms 늘어납니다.

| 단계 | 원작보다 빠른 입력 허용 추가량 | 원작보다 늦은 입력 허용 추가량 | 판정 폭의 전체 증가량 |
| :---: | ---: | ---: | ---: |
| **1 · 기본값** | 0ms | 0ms | 0ms · 원작 그대로 |
| **2** | +20ms | +20ms | +40ms |
| **3** | +40ms | +40ms | +80ms |
| **4** | +60ms | +60ms | +120ms |
| **5** | +80ms | +80ms | +160ms |
| **6** | +100ms | +100ms | +200ms |

이 수치는 **원작 범위에 더하는 값**입니다. 6단계의 전체 판정 폭이 200ms라는 뜻은 아닙니다. 6단계는 원래 범위보다 각각 0.1초 빠르거나 늦은 입력까지 추가로 허용합니다. 실제 내부 값은 게임 템포와 시간 단위에 맞춰 환산합니다.

음악 속도, 정답 버튼과 방향, 원래 점수 계산 흐름은 유지됩니다. 타이밍 허용 범위를 넓히는 기능이며 자동 플레이나 지연 오프셋 보정은 아닙니다.

### 변경과 저장

| 조작 | 동작 |
| --- | --- |
| 위 / 아래 | 옵션 항목 선택 |
| 오른쪽 / A / START | 다음 단계 |
| 왼쪽 | 이전 단계 |
| 마지막 값에서 한 번 더 이동 | 6→1 또는 1→6으로 순환 |

변경 즉시 적용됩니다. 선택한 숫자는 밝게, 나머지는 반투명하게 표시합니다. 판정을 원작으로 되돌릴 때는 **1**을 직접 선택합니다.

설정은 **`SC5P2KR_JDG` / 2블록(1,024바이트)**의 별도 VMU 파일에 자동 저장합니다. 기존 게임 진행 파일 `SC5PART2_DAT`과 분리됩니다. 변경 후 수초 기다렸다가 종료하고 다음 실행에도 같은 VMU를 연결해 주세요. 유효한 저장 설정이 없으면 기본값 1로 시작합니다. VMU가 없거나 공간이 부족하면 현재 실행에는 적용되지만 다음 실행까지 저장되지 않을 수 있습니다.

**[판정 설정 전체 설명: 시간 예시, 메뉴 색상, VMU 복원, 확인 범위](docs/JUDGMENT.md)**

## 스크린샷

한글화 작업 중 저장한 실제 게임 화면 16장입니다. 기존 캡처를 원본 크기 그대로 수록했으며, V1.105의 모든 장면을 새로 촬영한 것은 아닙니다. 최신 후반부·엔딩 변경 사항은 변경 내역을 함께 참고해 주세요.

| 타이틀 · 한글판 표시 | 메인 메뉴 · 의상실과 옵션 안내 |
| :---: | :---: |
| ![타이틀 · 한글판 표시](docs/screenshots/01-title.png) | ![메인 메뉴 · 의상실과 옵션 안내](docs/screenshots/02-main-menu.png) |

| 판정 설정 · 원작 판정인 1단계 | 판정 설정 · 가장 넓은 6단계 |
| :---: | :---: |
| ![판정 설정 · 원작 판정인 1단계](docs/screenshots/03-judgment-level1.png) | ![판정 설정 · 가장 넓은 6단계](docs/screenshots/04-judgment-level6.png) |

| 옵션 · 가사와 판정 설정의 선택 색상 | 리포트 선택 · 한국어 설명과 기록 |
| :---: | :---: |
| ![옵션 · 가사와 판정 설정의 선택 색상](docs/screenshots/05-options-lyrics.png) | ![리포트 선택 · 한국어 설명과 기록](docs/screenshots/06-report-select.png) |

| 의상실 · 의상 이름과 설명 | 의상실 · 마이크 이름과 설명 |
| :---: | :---: |
| ![의상실 · 의상 이름과 설명](docs/screenshots/07-costume.png) | ![의상실 · 마이크 이름과 설명](docs/screenshots/08-item.png) |

| 영상 · 위치 표기와 정렬 | 영상 · 제규어 소개 이름표와 대사 |
| :---: | :---: |
| ![영상 · 위치 표기와 정렬](docs/screenshots/09-location.png) | ![영상 · 제규어 소개 이름표와 대사](docs/screenshots/10-jaguar.png) |

| 영상 · 푸딩 소개 이름표와 대사 | 리포트 2 · 영상 속 안내와 대사 자막 |
| :---: | :---: |
| ![영상 · 푸딩 소개 이름표와 대사](docs/screenshots/11-pudding.png) | ![리포트 2 · 영상 속 안내와 대사 자막](docs/screenshots/12-report2-movie.png) |

| 리포트 3 · 플레이 중 대사 자막 | 리포트 4 · 플레이 중 대사 자막 |
| :---: | :---: |
| ![리포트 3 · 플레이 중 대사 자막](docs/screenshots/13-report3-dialogue.png) | ![리포트 4 · 플레이 중 대사 자막](docs/screenshots/14-report4-dialogue.png) |

| 리포트 5 · 플레이 중 대사 자막 | 결과 화면 · 시청률, 구조율, 숨은 요소 발견 |
| :---: | :---: |
| ![리포트 5 · 플레이 중 대사 자막](docs/screenshots/15-report5-dialogue.png) | ![결과 화면 · 시청률, 구조율, 숨은 요소 발견](docs/screenshots/16-result.png) |

[원본 이미지로 갤러리 보기](docs/GALLERY.md)

## 패치 전후 해시

실제 배포 적용기로 CUE와 GDI를 각각 생성하여 **총 8개 결과 파일**의 SHA-256을 확인했습니다. 아래 표는 CUE 출력 기준이며, GDI의 `track03.bin`도 같은 Track 3 해시입니다. GDI에서는 Track 2의 150섹터 프리갭을 제거하고 설명 파일과 이름을 변환합니다.

**Track 3 · 패치 전 / 일본판 원본**

```text
af9f53094aee1c3cba1cda183b0a60710732ec81c7e32a39e9127d816709a29f
```

**Track 3 · 패치 후 / V1.105**

```text
01f0a66568bcab8a135a9843d78ce808015478f2efd6e1cd4fa17fa3bfb539f5
```

| 파일 | 크기 (바이트) | V1.105 적용 결과 |
| --- | ---: | --- |
| Track 1 BIN | 1,980,384 | 원본과 동일 |
| Track 2 BIN | 2,076,816 | 원본과 동일 |
| Track 3 BIN | 1,185,760,800 | 위 V1.105 해시로 변경 |
| CUE | 384 | 원본과 동일 |

**[원본·CUE·GDI 전체 파일 해시](docs/HASHES.md)** · [기계 판독용 JSON](docs/original-and-output-hashes.json) · [다운로드 파일 SHA256SUMS](docs/SHA256SUMS.txt) · [적용 검사 기록](docs/verification/patch-roundtrip.json)

ZIP과 게임 이미지의 해시는 별개입니다. GDI 설명 파일, 오디오 RAW, 데이터 BIN의 해시를 [전체 해시 표](docs/HASHES.md)에 따로 공개합니다.

## 안내와 제보

- 일반 Flycast 코어에서 기존 판정 메뉴와 VMU 저장·복원 시험 기록을 확보했습니다. 실기·ODE 호환 여부는 별도 확인 대상입니다.
- 이번 V1.105 배포 검사는 최종 패치 적용과 결과 파일 일치 여부를 중심으로 진행했습니다. 상세 범위는 [검증 기록](docs/VERIFICATION.md)에 적었습니다.
- 자막이나 표시 문제는 [Issues](https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Part-2-Kr/issues)에 스테이지, 발생 위치, 직전 대사와 스크린샷을 남겨 주세요. 실행 중인 Track 3 해시도 함께 있으면 버전을 구분하기 좋습니다.
- 이 저장소의 V1.105는 비공식 한글 패치의 배포 버전입니다. SEGA 공식 한국어판을 의미하지 않습니다.

## 크레딧

**KOREAN LOCALIZATION BY GIKAKNO**

원작: SEGA / UGA. 글꼴 제공 및 라이선스는 [출처 안내](THIRD_PARTY_NOTICES.md)에 수록했습니다.

[패치 적용기 소스](src/README.md) · [1편 한국어 패치](https://github.com/OldManCraveGuitars-bit/DC-Space-Channel-5-Kr)
