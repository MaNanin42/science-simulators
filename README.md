# 과학 시뮬레이터

GitHub Pages용 단일 HTML 수업 자료 13종과 별도 저장소의 시뮬레이터 3종을 연결하는 수업 자료 목록입니다.

로컬에서 `docs/index.html`을 열어 목록을 확인합니다. 각 시뮬레이터는 개별 폴더의 `index.html`로도 열 수 있습니다.

## 게시할 때

저장소 이름은 `science-simulators`입니다. 게시 전 실제 전송할 파일과 Git 이력의 개인정보 및 비밀정보를 검사합니다. GitHub Pages에서 브랜치 게시를 선택하고 게시 폴더를 `/docs`로 설정합니다. 새 주소는 `https://mananin42.github.io/science-simulators/<폴더명>/` 형식입니다. 배포된 주소를 확인한 뒤 구글시트에 등록합니다.

## 물질과 에너지 통합 시뮬레이터

- `docs/reaction-pathways/index.html`에서 한 단계 반응과 두 단계 반응를 관리합니다. 기존 `activation-energy`, `two-step-enthalpy` 주소는 각각 해당 모드로 연결됩니다.
- `docs/catalysis-inhibition/`은 기본 탭에서 과산화 수소 분해의 산소 발생량을 비교하고, 심화 탐구 탭에서 반응 속도 곡선과 활성화 에너지를 살펴봅니다. 기존 반응 경로 주소의 `#catalyst`는 새 페이지로 연결됩니다.
- 3단원은 `docs/hess-law/`에서 흑연의 두 연소 경로, 중화열 가상 열량계, 열화학 반응식 조합으로 헤스 법칙을 탐구합니다. `docs/entropy-direction/`에서는 입자 배치와 얼음·물의 자발적 변화 방향을 비교합니다.
- 4단원 `docs/reaction-rate-lab/`에서는 농도 곡선의 두 점으로 평균 반응 속도를 구하고, 초기 속도 자료에서 속도식을 추론하며, 두 농도 곡선에서 1차 반응의 반감기를 읽습니다.
- `docs/molecular-energy/index.html`에서 온도만 바꾸기와 조건 비교를 관리합니다. 두 모드가 K와 kJ/mol을 사용하며 기준선 이상의 예상 개수와 분율을 같은 분포로 계산합니다. 기존 `temperature-energy`, `gas-energy-distribution` 주소는 각각 해당 모드로 연결됩니다.
- 구글시트에는 각 통합 폴더의 주소를 한 행씩 등록합니다. 첫 화면 생성 대상은 통합 시뮬레이터의 기본 모드입니다.

Chem-Screen의 작업 원본은 같은 분류의 `chem-screen-drug-candidate-simulator` 프로젝트에서 관리합니다. 갱신할 때 해당 HTML을 `docs/chem-screen/index.html`에 반영합니다. 아스피린 결합 절단 페이지의 하단 링크는 이 모음의 첫 화면을 가리킵니다.

## COX-2 효소 약물 작용

COX-2 효소 약물 작용은 `docs/cox2-drug-action/index.html`에서 실행합니다. 다섯 약물의 작용과 아라키돈산 → PGG₂ → PGH₂의 결합 변화를 비교합니다. 3D 라이브러리·좌표·계산 자료와 제삼자 라이선스가 포함된 단일 파일이며, 크기는 약 23 MB입니다. 최초 로딩에는 시간이 걸릴 수 있고 3D 표시에 WebGL이 필요합니다.

## 첫 화면 미리보기의 한글

GitHub Actions는 Noto CJK 글꼴을 설치하고 Chrome이 ‘한’, ‘글’, ‘열’을 서로 다른 모양으로 그리는지 확인한 뒤 첫 화면을 캡처합니다. 새 수업 HTML은 기존 게시 폴더에 넣으면 다음 실행에서 함께 처리됩니다. 독립 저장소 세 곳의 첫 화면도 각각의 Pages 게시 폴더에서 읽습니다.

시트에 새로 등록한 소유자 GitHub Pages 주소에 미리보기가 없으면 브라우저 캡처기가 같은 사이트에서 제공하는 [한글 웹폰트](docs/preview-renderer/hangul.woff2)를 사용합니다. 이 파일은 [Noto Sans KR](https://github.com/google/fonts/tree/main/ofl/notosanskr) 가변 글꼴에서 한글 음절과 자모를 추출했습니다. [SIL Open Font License](docs/preview-renderer/OFL.txt)가 적용됩니다.
