[English](README.md) · [한국어](README-KR.md)

# Tupper-Formula

**정확한 비트맵 인코딩, 자기 이미지 구성, 재현 가능한 수학 실험.**

![Tupper-Formula 연구 노트](assets/og-image.png)

영어·한국어 학술형 웹페이지와 별도의 Python 연구 패키지를 함께 제공하는 저장소이다. 유한한 이미지가 Tupper 부등식의 특정 위치에 나타나는 이유를 유도하고, 해당 정수 위치를 구성하며, 정수 연산과 원래 floor/mod 식의 정확한 유리수 계산으로 결과를 확인한다.

> **구현 범위:** `derive`는 **외부 위치 상수 `k`가 필요한 Tupper형 자기 이미지**를 구성한다. 새로운 수학적 발견이나 거대한 상수 자체까지 출력하는 자기완결적 공식을 구현했다고 주장하지 않는다. 더 강한 자기 그래프화 연구는 원저자에게 출처를 귀속하여 별도로 설명한다.

## 구성

| 구성 요소 | 역할 |
|---|---|
| 학술형 웹페이지 | 유도, 문헌 비교, 참고문헌, 원클릭 LaTeX 복사, 반응형 영어·한국어 화면; 라이트 전용, 외부 CDN 없음 |
| 브라우저 실험실 | 픽셀 편집, 비트 위치 검사, 십진수 `k` 복원, 표시 방향 변경, 검증된 JSON·SVG·PBM 교환 |
| Python 연구 패키지 | 정확한 인코딩·복호화, 원식 계산 검증기, 수식 자체의 비트맵 구성, 이미지 입력, CLI, C진 배열 실험 |
| 재현 근거 | 검증된 예제 5종, 작은 마스크 전수 실험, 무작위 검사, 언어 간 공통 데이터, 기계 판독 보고서 |
| 공개 준비 자료 | 1200×630 OG PNG와 벡터 원본, BibTeX, 인용 메타데이터, 이중 언어 문서, CI·Pages 워크플로 |

원형 그림은 논문 스크린샷이 아니라 **Tupper의 2001년 논문에 적힌 정수에서 다시 계산한 비트맵**이다. 이 저장소의 렌더러·인코더·웹페이지는 독자 구현이다. [문헌과 출처](docs/LITERATURE-KR.md)를 참조한다.

## 웹페이지 실행

저장소 루트에서 실행한다.

```sh
python -m http.server 8000
```

**http://localhost:8000/** 에 접속한다. 기본은 영어이며 헤더에서 한국어로 전환하거나 `?lang=ko`를 사용한다. `index.html`을 더블클릭하지 않는다. 실험실은 ES 모듈과 로컬 JSON 요청을 사용하므로 HTTP가 필요하다. 초기 영어 본문과 MathML 수식은 정적 HTML에도 포함되어 있다.

확인용 사이트 실행에는 Node 설치나 빌드가 필요하지 않다. 수식은 네이티브 MathML로 표시하고 운영체제 글꼴을 사용한다. 픽셀은 브라우저 밖으로 전송하지 않는다. 클립보드·SHA-256 기능에는 HTTPS 또는 localhost가 적합하며, 복사는 수동 대체 경로도 제공한다.

## Python 연구 프로그램 실행

**Python 3.11 이상**이 필요하다. 정확한 계산 코어에는 외부 런타임 의존성이 없다.

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .

python -m tupper_formula encode examples/input/letter-a.txt -o output/a
python -m tupper_formula verify output/a/experiment.json --literal
python -m tupper_formula cell output/a/experiment.json --x 1 --j 4
```

제공한 3×5 A의 값은 `N = 16015`, `k = 80075`이다. 결과 디렉터리는 새 경로여야 하며, 기존 실험에 대한 덮어쓰기는 거부한다.

### 부등식 자신의 이미지를 구성하기

다음 명령은 선택한 부등식을 조판하고, 이진화한 픽셀을 `N`에 저장하여 `k = HN`을 구한 뒤, 복원 마스크를 검증한다. 웹페이지를 생성하는 명령이 아니다.

```sh
python -m pip install -e ".[render]"
python -m tupper_formula derive --height 32 --variant tupper -o output/self-h32
python -m tupper_formula verify output/self-h32/experiment.json --literal

# 대수적으로 같지만 조판과 k가 다른 형태:
python -m tupper_formula derive --height 32 --variant bit -o output/bit-h32
```

동봉된 `formula-h32` 실험은 353×32 마스크이며 `k`는 십진수 3,380자리이다. 최종 이진 마스크가 기준이다. 렌더러·글꼴 버전·임계값이 달라지면 다른 마스크와 정수가 나올 수 있다. `requirements-render.txt`에는 동봉 렌더링에 사용한 버전을 기록하였다. TeX 설치나 글꼴 다운로드는 필요하지 않으며 글꼴 파일은 배포하지 않는다.

각 실험은 `experiment.json`, `verification.json`, `N.txt`, `k.txt`, `formula.tex`, `target.pbm`, `decoded.pbm`, `plot.svg`를 포함한다. 수식 구성에는 `plot.png`도 추가한다.

## 수학적 약속

W×H 이진 이미지에서 수학 좌표 `i`는 오른쪽, `j`는 위쪽으로 증가한다.

$$
N=\sum_{i=0}^{W-1}\sum_{j=0}^{H-1} b_{i,j}2^{Hi+j},\qquad k=HN.
$$

`N`의 비트에 이미지가 들어 있다. 부등식은 `0 ≤ x < W`, `k ≤ y < k+H`에서 단위 정사각형마다 비트 하나를 읽는다. 파일의 행은 **위→아래** 순서이며 좌표 변환을 명시한다. `historical` 표시는 화면의 두 축을 모두 반전하지만 저장 데이터는 조용히 변경하지 않는다. 너비는 별도 메타데이터이며 일반적으로 `N`만으로 복원할 수 없다.

반열린 칸의 경계, floor/mod 항등식, 반복 위치, 정보량의 한계는 [유도 문서](docs/THEORY-KR.md)를 참조한다.

## 테스트와 기록된 근거

```sh
python -m unittest discover -s tests -v
python experiments/run_suite.py
npm test
python scripts/validate_repo.py
```

`npm test`에는 Node 20 이상이 필요하지만 패키지를 설치하지 않는다. 동봉 산술 보고서는 **전수 마스크 658개**, **시드 고정 무작위 마스크 300개**, **정확한 유리수 중점 검사 5,442회**, **불일치 0건**을 기록한다. 중점 검사 수는 전수 실험의 수치이며 저장소 전체 검사를 통합한 수치가 아니다. Python·JavaScript 단위 테스트와 브라우저 검사의 범위는 [validation.json](reports/validation.json)과 [실험 재현](docs/EXPERIMENTS-KR.md)에 기록한다.

테스트 결과가 모든 입력에 대한 증명을 대신하지는 않는다. 대수적 유도가 일반 항등식을 보장하고 유한 실험은 구현을 검사한다. 동봉 결과는 GitHub 실제 배포, 모든 브라우저 엔진, 모든 운영체제를 시험했다는 의미가 아니다.

## 저장소 구성

```text
Tupper-Formula/
├── index.html                 # 바로 제공할 수 있는 영어 본문
├── css/                       # 논문형 레이아웃·인쇄 스타일
├── js/                        # 독립 BigInt 코어·MathML·UI
├── data/                      # EN/KO 본문·수식·예제·출처
├── assets/                    # 재계산 그림·OG PNG/SVG·파비콘
├── src/tupper_formula/        # 웹 코드와 구별된 Python 연구 패키지
├── examples/                  # 표준 실험 산출물
├── experiments/               # 전수·시드 고정 재현 실험
├── tests/                     # Python·네이티브 Node 테스트
├── schemas/                   # 교환 JSON 스키마
├── scripts/                   # 사이트·이미지 빌드·QA·배포 도구
├── docs/                      # 영어 문서와 대응하는 -KR.md
├── reports/                   # 실제 기계 판독 검증 결과
└── .github/workflows/         # CI·선택적 GitHub Pages 배포
```

## 문서

[유도](docs/THEORY-KR.md) · [문헌](docs/LITERATURE-KR.md) · [Python API·CLI](docs/PYTHON-GUIDE-KR.md) · [실험](docs/EXPERIMENTS-KR.md) · [웹페이지·배포](docs/WEBSITE-KR.md) · [연구 방향](docs/RESEARCH-KR.md) · [한계](docs/LIMITATIONS-KR.md)

모든 Markdown 문서는 한국어 대응본을 포함한다. 기술적 계약의 기준 문서는 영어이며 번역도 동일한 계약을 유지해야 한다.

## GitHub Pages 공개

설정된 대상은 `https://jtech-co.github.io/Tupper-Formula/`이다. 이는 설정일 뿐 **실제 사이트가 이미 공개되었다는 주장이 아니다**. 다른 계정·저장소에 공개할 때는 먼저 변경한다.

```sh
python scripts/configure_site.py --owner YOUR_ACCOUNT --repo Tupper-Formula
```

Pages 설정에서 `main / (root)`를 선택하거나, **GitHub Actions**를 선택하고 동봉 `pages.yml` 워크플로를 실행한다. 배포 원본은 한 방식만 사용한다. 하위 경로·OG 설정은 [배포 문서](docs/WEBSITE-KR.md)에 설명하였다. 이 ZIP은 저장소를 푸시하거나 호스팅을 생성하지 않는다.

## 출처와 라이선스

이 프로젝트의 독자 코드·본문·생성 이미지는 [MIT](LICENSE)로 제공한다. 참고 논문과 원저자의 구현 및 권리는 별개이다. 원형 정수에서 만든 예제는 출처를 표시하였으며, 논문 PDF나 제3자 소스코드를 동봉하지 않았다.

소프트웨어 인용에는 [CITATION.cff](CITATION.cff), 과학 문헌 인용에는 [references.bib](references.bib)를 사용한다. 재현·구성 예제·새 정리를 구분하여 인용한다.
