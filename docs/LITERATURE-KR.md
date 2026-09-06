[English](LITERATURE.md) · [한국어](LITERATURE-KR.md)

# 문헌, 출처와 주장 범위

이 문서는 핵심 출처를 정리한 것이며 역사적 우선권의 전수 조사가 아니다. 저장소 구성 시 **2026-09-06** 기준으로 출처를 확인하였다. 모든 자기참조 공식을 망라하거나 각 변형에서 언급한 저자가 최초라고 주장하지 않는다.

## R1 — Tupper (2001)

Jeff Tupper, *Reliable Two-Dimensional Graphing Methods for Mathematical Formulae with Two Free Variables*, SIGGRAPH 2001, pp.77–86. [저자 제공 논문](https://www.dgp.toronto.edu/~mooncake/papers/SIGGRAPH2001_Tupper.pdf). DOI: `10.1145/383259.383267`.

핵심 사례는 신뢰성 있는 그래프 작도를 다룬 논문의 Figure 13(PDF 7쪽, 인쇄 p.83)이다. 이 부등식은 이진 격자 이미지를 열거하며 원문은 격자 크기를 바꾸는 가능성도 언급한다. 유명한 그림은 106×17 창에 나타나고 원문에 543자리 k가 있다. `examples/historical/k.txt`에 그 수를 기록하였다. 복원 마스크의 채워진 칸은 334개이며, 이는 논문에서 추가로 인용한 수치가 아니라 자체 재계산 결과이다.

**범위:** 표시 위치 k에 정보가 들어 있다. 유한한 창의 그림을 재현하는 것과 필요한 모든 상수를 포함하는 전역적 자기완결적 식은 다르다.

## R2 — Trávník (2011 및 후속 수정)

Jakub Trávník, [*Self Referential Formula in Math*](https://jtra.cz/stuff/essays/math-self-reference/index.html). 저자 설명과 구현.

고정된 식의 그림과 거대한 정수의 자릿수 출력을 분리하여 모두 재현한다. 저자는 12,876자리 상수와 재현 프로그램을 제공한다. 해당 페이지의 후속 수정은 Tupper의 이전 자기 출력 구성도 출처로 인정하므로, 이 저장소는 Trávník이 자기완결적 사례를 최초로 만들었다고 주장하지 않는다.

**범위:** 구현을 설명하지만 해당 코드를 복사하거나 실행하지 않았다. 새로운 Tupper k를 선택했다고 같은 수준의 자기완결적 구성이 되는 것은 아니다.

## R3 / R11 — Trávník (2019)

[개요](https://jtra.cz/stuff/essays/math-self-reference-smooth/index.html)와 [상세 설명](https://jtra.cz/stuff/essays/math-self-reference-smooth/detailed-explanation.html).

후속 구성은 고정된 이진 픽셀 대신 베지어 글리프 외곽선과 내부·외부 판정을 사용한다. 식 본문과 숫자 출력기를 분리하는 구성이 중요하다. “Smooth”는 글리프 표현을 가리키며 소속 판정의 모든 경계·극한 문제가 없다는 뜻이 아니다.

**범위:** 이 저장소의 SVG는 **정사각형 픽셀**을 정확히 담는 벡터 컨테이너이다. 매끄러운 곡선 기반 자기참조 공식의 재현이 아니며, 5만 자리급 자기완결 예제를 구현했다고 주장하지 않는다.

## R4 — Somu와 Mishra (2021 / 2023)

Sai Teja Somu·Vidyanshu Mishra, [*On a Generalization of Tupper's Formula for m Colours and n Dimensions*](https://arxiv.org/abs/2109.11013), arXiv:2109.11013; *Discrete Mathematics*, article 113600(2023). DOI: `10.1016/j.disc.2023.113600`.

여러 색과 다차원 배열에 대한 확장을 구성한다. Tupper의 원리를 흑백 2차원 이상의 배열 표현으로 보는 근거이다.

**범위:** `radix.py`는 형상이 명시된 배열을 C진수로 저장하는 기초적 독자 구현이다. 논문의 n변수 부등식을 포팅·검증·전면 재현한 것은 아니다.

## R5 — Alexander (2025)

Samuel Allen Alexander, [*Self-graphing equations*](https://arxiv.org/html/2504.00006v1), arXiv:2504.00006, 확인한 버전의 문서 날짜 2025-03-18.

수학적 그래프와 글리프 렌더링을 구분하고 두 결과가 고정점으로 일치하는 충분조건을 연구한다. 사용하는 언어와 허용 연산이 중요하다. 표현력이 높은 체계에서의 존재 충분조건은 임의의 제한 아래 짧은 초등 함수식을 보장하지 않는다.

**범위:** 증명 보조기 형식화, 해당 정리 구성의 전체 구현, 제한 없는 최단 공식 탐색은 포함하지 않는다.

## 구현 문서

[R6: Python 정수 변환 제한](https://docs.python.org/3/library/stdtypes.html#integer-string-conversion-length-limitation)은 거대한 십진수 처리의 주의점을 설명한다. 패키지는 9자리 단위 제한 변환을 사용하며 인터프리터 전역 보호를 해제하지 않는다.

[R7: MathML](https://developer.mozilla.org/en-US/docs/Web/MathML), [R8: BigInt](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt)는 브라우저 기술 문서이다. [R9: Matplotlib Mathtext](https://matplotlib.org/stable/users/explain/text/mathtext.html)는 선택적 수식 조판기를, [R10: GitHub Pages 배포 원본](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)은 배포 설정을 설명한다.

출처는 [`data/references.json`](../data/references.json)과 [`references.bib`](../references.bib)로도 제공한다. 인터넷 문서는 동봉하지 않으며 영구적인 접근 가능성을 보장하지 않는다. 이론적 확장은 출처를 표시하고 수치 실험 결과는 저장소 자체 측정임을 명시한다.
