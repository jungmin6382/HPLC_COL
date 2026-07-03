# 콜대원 HPLC-DAD 아세트아미노펜 함량 분석 자동화

Agilent 1260 Infinity III HPLC-DAD로 측정한 콜대원(감기약) 아세트아미노펜 함량 데이터를 Python으로 자동 분석·시각화하는 프로젝트입니다. 피크 자동 탐색, System Suitability(USP 규정) 검증, 다파장 3D 크로마토그램 시각화를 지원합니다.

## 주요 기능

- **자동 피크 탐색**: 각 DAD 채널(파장)에서 `idxmax()` 기반으로 최대 흡광도 피크를 자동 탐색하여, 머무름 시간에 관계없이 목표 성분(아세트아미노탄)을 식별
- **System Suitability 검증**: USP Tailing Factor, 이론단수(Theoretical Plates) 계산 및 PASS/FAIL 자동 판정
- **다파장 3D 크로마토그램**: 210~273 nm 6개 채널 DAD 데이터를 Retention Time × Wavelength × Absorbance 3차원으로 시각화 (정적 PNG, 회전 mp4, VSCode 인터랙티브 뷰어 지원)
- **정량 분석**: 표준 곡선 기반 함량(mg) 계산 및 결과 요약

## 레포 구조

```
.
├── data/
│   └── raw/                     # Agilent OpenLAB CDS에서 export한 원본 DAD CSV
│       ├── DAD1A.CSV            # 243 nm
│       ├── DAD1B.CSV            # 210 nm
│       ├── DAD1C.CSV            # 225 nm
│       ├── DAD1D.CSV            # 254 nm
│       ├── DAD1E.CSV            # 262 nm
│       └── DAD1F.CSV            # 273 nm
├── src/
│   ├── peak_detection.py        # 자동 피크 탐색 및 정량 계산
│   ├── system_suitability.py    # Tailing Factor / 이론단수 계산
│   └── hplc_3d_viewer.py        # 3D DAD 크로마토그램 뷰어 (정적/회전/인터랙티브)
├── results/                     # 분석 결과 이미지·표
├── requirements.txt
└── README.md
```

> 실제 폴더/파일명은 본인 레포 구조에 맞게 수정해서 사용하세요.

## 설치

```bash
git clone https://github.com/<username>/coldawon-hplc-analysis.git
cd coldawon-hplc-analysis
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3D 회전 애니메이션(mp4) 생성을 위해서는 [FFmpeg](https://ffmpeg.org/download.html)가 시스템에 별도로 설치되어 있어야 합니다.

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows: 공식 사이트에서 다운로드 후 PATH 등록
```

## 데이터 형식

원본 CSV는 Agilent OpenLAB CDS에서 DAD 채널별로 export한 2열(시간, 흡광도) 데이터입니다. 헤더 없이 `time, absorbance(AU)` 순서로 저장되어 있어야 합니다.

## 사용법

### 1. 피크 자동 탐색 및 정량

```bash
python src/peak_detection.py --input data/raw/DAD1F.CSV --wavelength 273
```

### 2. System Suitability 검증

```bash
python src/system_suitability.py --input data/raw/DAD1F.CSV
```

### 3. 3D DAD 크로마토그램 뷰어

```bash
python src/hplc_3d_viewer.py
```

실행 시 matplotlib 창이 뜨며 마우스 드래그로 회전할 수 있습니다. 원격 서버(SSH) 환경에서는 `SAVE_ROTATION_VIDEO = True`로 설정하여 PNG/mp4로 결과를 저장한 뒤 확인하는 것을 권장합니다.

## 분석 조건

| 항목 | 내용 |
|---|---|
| 기기 | Agilent 1260 Infinity III (DAD) |
| 이동상 | H2O : MeOH = 70 : 30 |
| 검출 파장 | 273 nm (정량), 210~262 nm (확인용) |
| 시료 | 콜대원 (아세트아미노펜 함유 감기약) |

## 라이선스

이 프로젝트는 개인/학술 목적의 데이터 분석 예시입니다. 원본 실험 데이터는 별도 라이선스 정책을 따를 수 있습니다.
