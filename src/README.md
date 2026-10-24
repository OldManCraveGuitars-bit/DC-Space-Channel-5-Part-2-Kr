# 패치 적용기 소스

`PatchApplier.cs`는 V1.105에 고정된 SHA-256과 패치 길이를 가진 Windows Forms 적용기입니다. 원본 파일을 읽기 전용으로 열고, 별도 결과의 전체 해시가 모두 맞을 때 결과 폴더를 확정합니다. 게임 원본과 번역 작업용 전체 빌드 환경은 이 저장소에 포함하지 않습니다.

## 빌드

.NET Framework 4.x C# 컴파일러가 있는 Windows에서:

```powershell
& "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:winexe /optimize+ /platform:anycpu /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll /out:SC5Part2KoreanPatch_v1.105.exe PatchApplier.cs
```

공개 해시는 릴리스에 첨부한 실제 EXE 기준입니다. 다시 컴파일한 EXE는 빌드 환경 등의 차이로 파일 해시가 달라질 수 있습니다.

## 명령줄 적용

```text
SC5Part2KoreanPatch_v1.105.exe --apply <patch.gz> <original-folder> <new-output-folder> <new-report.json> [gdi|cue]
```

경로에 공백이 있으면 따옴표로 감싸세요. 결과 폴더와 보고서 파일은 존재하지 않는 경로를 사용하며, 보고서는 원본·결과 폴더 밖에 둡니다. 종료 코드 0은 성공, 1은 실패입니다. 보고서에는 사용자가 지정한 로컬 경로가 기록되므로 공개 제보 시 개인정보를 확인해 주세요.

GUI 기본 출력은 GDI입니다. 기존 명령줄 호환성을 위해 형식 인자를 생략한 CLI는 CUE로 출력합니다. ODE용은 마지막 인자에 `gdi`를 지정하세요.

`hardware-v1101/`에는 유지된 초기 캐시 진입 수정의 SH-4 원천과 링크 스크립트를 수록했습니다. V1.102의 초기화 변경은 [hardware-v1102](hardware-v1102/README.md)에 있습니다. 전체 ROM 재빌드 입력은 포함하지 않습니다. [변경 명세와 검사](../docs/HARDWARE-BOOT.md)를 참고하세요.

V1.103의 초기화 시점 변경은 [hardware-v1103](hardware-v1103/README.md)에 있습니다.

V1.104의 디스크 배치 수정은 [hardware-v1104](hardware-v1104/README.md)에 있습니다.

V1.105의 자막 수정은 [translation-v1105](translation-v1105/README.md)에 있습니다.
