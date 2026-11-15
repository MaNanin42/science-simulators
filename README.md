# 과학 시뮬레이터

GitHub Pages용 단일 HTML 수업 자료 12종과 별도 저장소의 시뮬레이터 3종을 연결하는 수업 자료 목록입니다.

로컬에서 `docs/index.html`을 열어 목록을 확인합니다. 각 시뮬레이터는 개별 폴더의 `index.html`로도 열 수 있습니다.

## 게시할 때

저장소 이름은 `science-simulators`입니다. 게시 전 실제 전송할 파일과 Git 이력의 개인정보 및 비밀정보를 검사합니다. GitHub Pages에서 브랜치 게시를 선택하고 게시 폴더를 `/docs`로 설정합니다. 새 주소는 `https://mananin42.github.io/science-simulators/<폴더명>/` 형식입니다. 배포된 주소를 확인한 뒤 구글시트에 등록합니다.

## 물질과 에너지 통합 시뮬레이터

- `docs/reaction-pathways/index.html`에서 한 단계 반응과 두 단계 반응를 관리합니다. 기존 `activation-energy`, `two-step-enthalpy` 주소는 각각 해당 모드로 연결됩니다.
- `docs/catalysis-inhibition/`은 정촉매의 대체 경로, 반응물 결합형 억제, 촉매 활성점 차단을 같은 초기 조건에서 비교합니다. 기존 반응 경로 주소의 `#catalyst`는 새 페이지로 연결됩니다.
- 3단원은 `docs/hess-law/`에서 흑연·CO 및 액체 물·수증기 과제에서 상태·계수·예측 엔탈피를 검증하고 여러 경로의 합을, `docs/entropy-direction/`에서 입자 배치와 얼음·물의 자발적 변화 방향을 탐구합니다.
- 4단원 `docs/reaction-rate-lab/`에서는 모형 실험 자료로 속도식을 추론하고 두 농도 곡선에서 1차 반응의 반감기를 읽습니다.
- `docs/molecular-energy/index.html`에서 온도만 바꾸기와 조건 비교를 관리합니다. 두 모드가 K와 kJ/mol을 사용하며 기준선 이상의 예상 개수와 분율을 같은 분포로 계산합니다. 기존 `temperature-energy`, `gas-energy-distribution` 주소는 각각 해당 모드로 연결됩니다.
- 구글시트에는 각 통합 폴더의 주소를 한 행씩 등록합니다. 첫 화면 생성 대상은 통합 시뮬레이터의 기본 모드입니다.

Chem-Screen의 작업 원본은 같은 분류의 `chem-screen-drug-candidate-simulator` 프로젝트에서 관리합니다. 갱신할 때 해당 HTML을 `docs/chem-screen/index.html`에 반영합니다. 아스피린 결합 절단 페이지의 하단 링크는 이 모음의 첫 화면을 가리킵니다.
