[English](PYTHON-GUIDE.md) · [한국어](PYTHON-GUIDE-KR.md)

# Python 패키지, CLI와 데이터 교환

## 설치 환경

Python 3.11 이상과 가상환경을 사용한다. `python -m pip install -e .`은 외부 의존성이 없는 계산 코어를, `python -m pip install -e ".[render]"`는 Pillow·Matplotlib을 추가 설치한다. 패키지는 시스템 TeX 실행 파일, 클라우드 모델, 이미지 인식 API, 네트워크 서비스를 사용하지 않는다.

기록된 렌더러 버전은 `python -m pip install -r requirements-render.txt`로 설치한다. 패키지 설치 자체는 인덱스에 접근할 수 있다. 버전 고정은 재현성을 높이지만 운영체제 간 안티앨리어싱까지 동일하다고 보장하지 않는다.

## 자기 이미지 구성

```sh
python -m tupper_formula derive --height 32 --variant tupper -o output/self-h32
python -m tupper_formula verify output/self-h32/experiment.json --literal
```

과정은 식에 H 대입 → Mathtext 조판 → 자르기·여백 → 높이 H로 변경 → 이진화 → 정확한 이진 마스크 → N 인코딩 → H 곱하기 → 복호화 → 비교이다. `--variant bit`는 나눗셈·내림 후 mod를 적용하는 동치 형태이다. 조판이 달라지면 표현 문자열과 비트맵이 달라진다. 여기서의 자기 재현은 외부 위치가 지정된 자기 이미지로 한정한다.

H는 16…96, 임계값은 0…255(모든 수식 픽셀을 지우는 값은 거부)를 허용한다. 작거나 가는 글리프는 산술적으로 정확히 재현되어도 읽기 어려울 수 있다. 식의 가독성을 주장하기 전에 `plot.png`를 확인한다.

## 사용자 마스크·이미지 인코딩

```sh
python -m tupper_formula encode examples/input/asymmetric.txt -o output/asymmetric
python -m tupper_formula encode drawing.png --image --width 106 --height 17 --threshold 160 -o output/drawing
```

`--image`가 없으면 직사각형 `0/1`·`./#` 텍스트와 주석을 허용하는 P1 PBM을 읽는다. 이진 P4 PBM은 지원하지 않는다. 이미지 크기 변경에는 너비·높이를 함께 제공하고, 둘 다 생략하면 제한 내에서 원본 크기를 유지한다. EXIF 방향을 적용하고 투명 영역을 흰색에 합성한다. 임계값보다 작은 값은 1이다. 크기 변경·이진화에서는 정보가 손실될 수 있고 그 이후의 마스크에 대해 정확성을 보장한다.

## 복호화·칸 검사

```sh
python -m tupper_formula decode --k-file examples/historical/k.txt --width 106 --height 17 --orientation historical -o output/historical.svg
python -m tupper_formula decode --k-file examples/letter-a/k.txt --width 3 --height 5 -o output/a.pbm
python -m tupper_formula cell examples/letter-a/experiment.json --x 1 --j 4
```

`decode`는 정렬된 비표준 반복 위치도 허용한다. `--orientation historical`은 SVG 표시에만 적용하며 PBM·텍스트는 위→아래의 표준 데이터이다. `cell`은 수학적 칸·화면 행·비트 인덱스·몫·비트를 출력한다. 거대한 절대 y를 부동소수점으로 근사하지 않는다.

종료 코드는 정상 0, 계산된 검증 실패 1, 잘못된 입력·처리 가능한 오류 2이다. 기존 파일·결과 폴더는 조용히 덮어쓰지 않는다. 구조화 결과는 필요한 경우 JSON으로 출력한다.

## 코어 API

```python
from fractions import Fraction
from tupper_formula import Bitmap, encode, decode, evaluate, evaluate_literal
from tupper_formula.manifest import make_manifest, verify_manifest

image = Bitmap(("010", "101", "111", "101", "101"))
N, k = encode(image)
assert decode(k, image.width, image.height) == image
assert evaluate(Fraction(3, 2), Fraction(2*(k+4)+1, 2), 5) == 1
assert evaluate_literal(Fraction(3, 2), Fraction(2*(k+4)+1, 2), 5) == 1
report = verify_manifest(make_manifest(image), literal=True)
assert report["passed"]
```

`evaluate`는 시프트를 이용해 우변 비트를 반환한다. `evaluate_literal`은 `floor(mod(q/2**n,2))`를 `Fraction`으로 계산한다. 좌표는 음이 아닌 `int`·`Fraction`만 허용하고 실수·불리언은 거부한다. 이는 구현 범위이며 음의 좌표 확장이 불가능하다는 뜻이 아니다.

`radix.encode_array(values, shape, base)`와 `radix.decode_array(N, shape, base)`는 형상이 알려진 평탄 배열을 처리한다. 마지막 축이 가장 빠르게 변하며 비트맵의 특별한 열 우선 약속과 다르다. 예제·테스트에서 이를 구별한다.

## JSON 계약

[`experiment.schema.json`](../schemas/experiment.schema.json)을 참조한다. `N`·`k`는 JSON 수치가 아니라 **십진 문자열**이다. 의미 검증은 크기·이진 행·표준 `k=HN`·방향·수식 형태와 H·반열린 영역·비트맵 해시를 재계산한다. `source`·`generator`는 출처 객체이며 신뢰할 수 있는 증명 인증서가 아니다. 알 수 없는 최상위 필드는 JSON Schema 검증에서 실패하며 산술 검증은 필수 의미 불변량에 집중한다.

표준 해시 입력은 다음 ASCII 구조이다.

```text
tupper-bitmap-v1
W H
first top row
...
last bottom row
```

마지막 행을 포함한 모든 줄은 `\n`으로 끝난다. `W H`는 공백 하나로 구분한 실제 십진 크기이다. 표시 방향·출처는 비트맵 해시에 포함하지 않고 별도로 검사·기록한다. 일치하는 해시는 오류 검출 수단이지 작성자 인증이 아니다.

Python·브라우저는 **두 구현의 자원 제한이 겹치는 범위**에서 같은 manifest를 교환한다. 브라우저 JSON은 Web Crypto SHA-256을 사용하므로 HTTPS·localhost 같은 적절한 보안 컨텍스트가 필요하다. 연구 근거로 활용하기 전에 내보낸 JSON을 Python에서 독립 검증한다.

## 자원 제한

| 계층 | 제한 |
|---|---|
| Python 비트맵 | 한 변 ≤4096, 전체 ≤65,536칸 |
| Python 십진 텍스트 | ASCII 숫자 ≤25,000자리, 제한된 청크 변환 |
| Python 평가 정수 | ≤84,000비트, 비트 인덱스 <65,536 |
| 파일 입력 | 텍스트·manifest ≤2 MB, 이미지 ≤20 MB·원본 1,600만 픽셀 |
| 브라우저 | W≤512, H≤128, 전체≤16,384칸, 십진수≤5,500자리, JSON≤1 MB |

이는 보수적인 정책이며 Python·JavaScript의 성능 한계 측정값이 아니다. 코어는 `eval`, 입력 LaTeX 실행, manifest 플러그인 로딩, Python 전역 정수 문자열 보호 해제를 사용하지 않는다.
