[English](WEBSITE.md) · [한국어](WEBSITE-KR.md)

# 웹 구조, 수정과 배포

## 구조

동봉 `index.html`은 바로 제공할 수 있다. `css/style.css`·`css/print.css`는 라이트 전용 논문형 레이아웃이며, `js/core.js`는 독립 BigInt 계산, `js/math.js`는 신뢰된 로컬 데이터의 MathML 구성, `js/app.js`는 실험실·언어 상태를 담당한다. React·Vite 빌드, SPA 라우터, 원격 글꼴, 수식 CDN, 분석 서비스가 없다.

영어·한국어 본문은 `data/content.json`, UI는 `data/ui.json`, MathML·LaTeX 쌍은 `data/formulas.json`, 출처·예제는 각각의 JSON에 있다. HTML 삽입은 저장소의 신뢰된 본문·수식에 한정하며 사용자 입력 JSON을 HTML·코드로 평가하지 않는다.

## 본문 수정

두 언어 레코드를 함께 수정하고 과학적 계약이 바뀌면 Markdown도 갱신한다.

```sh
python scripts/build_site.py
python scripts/validate_repo.py
```

`build_site.py`는 템플릿과 JSON에서 영어 본문·수식을 정적 HTML로 만들고 사이트맵도 갱신한다. 생성된 HTML만 별도로 고쳐 원본과 어긋나게 하지 않는다. 언어 우선순위는 `?lang=ko|en`, localStorage, 영어이다. 이 사이트는 하나의 이중 언어 앱이며 서버에서 렌더링한 언어별 독립 경로 두 개가 아니다. 한국어까지 완전하게 SEO 색인된다고 주장하지 않는다.

표시 수식마다 복사 버튼·LaTeX 원문을 제공하고 칸 검사기도 현재 식을 복사한다. 브라우저 정책이 자동 복사를 거부할 수 있어 텍스트 선택 대화상자를 제공한다. 테스트는 요청된 텍스트를 확인할 수 있지만 사용자의 클립보드 정책을 우회하지 않는다.

## 로컬 미리보기

```sh
python -m http.server 8000
```

`file://`가 아니라 `http://localhost:8000/`을 사용한다. SHA-256 JSON 가져오기·내보내기는 적절한 보안 컨텍스트의 Web Crypto가 필요하다. 외부 네트워크의 HTTP는 본문이 보이더라도 해당 기능이 제한될 수 있으므로 공개 호스팅은 HTTPS를 사용한다.

## GitHub Pages: 한 방식 선택

**브랜치 배포:** 저장소를 푸시한 뒤 Settings → Pages에서 **Deploy from a branch**, `main`, `/(root)`를 선택한다. 동봉 HTML·`.nojekyll`이면 충분하다. Pages에는 Python 런타임이 없으며 Python 실험은 로컬·CI에서 수행한다.

**Actions 배포:** Pages 원본을 **GitHub Actions**로 선택하고 `.github/workflows/pages.yml`을 사용한다. 공개 사이트 파일만 `_site`로 모아 Pages artifact를 업로드하고 배포한다. main 푸시와 수동 실행을 지원하며 CI는 별도이다. 활성화 전에 저장소 Actions 권한을 검토한다. ZIP이 권한을 변경하지 않는다.

로컬 리소스는 상대 경로이므로 저장소 하위 경로에서도 `/css`·`/js` 절대 경로를 재작성할 필요가 없다. 클라이언트 라우팅·임의의 심층 경로가 없으며 본문 이동은 fragment를 사용한다.

## 계정·저장소·OG 설정

첫 공개 또는 저장소 이동 전에 실행한다.

```sh
python scripts/configure_site.py --owner YOUR_ACCOUNT --repo Tupper-Formula
# 선택적 사용자 도메인:
python scripts/configure_site.py --owner YOUR_ACCOUNT --repo Tupper-Formula --base-url https://example.org/research/tupper/
```

사이트 메타데이터·canonical·소셜 이미지 주소·스키마 식별자·인용 저장소 주소를 갱신하지만 GitHub에 연결하거나 무언가를 생성하지 않는다. 기본 계정·저장소는 준비된 대상이지 실제 배포를 확인했다는 뜻이 아니다.

`assets/og-image.png`는 실제 1200×630 PNG이며 `og-image.svg`는 대응 벡터 표현이다. 그림을 복사하지 않고 역사적 이진 마스크를 재계산했다. 렌더링 의존성 설치 후 `python scripts/build_assets.py`로 다시 만들 수 있다. 글꼴 파일은 저장소에 복사하지 않는다. 사용 가능한 글꼴에 따라 재빌드한 글자 치수가 달라질 수 있으며 동봉 PNG가 공개 기준 이미지이다.

HTML 소셜 카드는 절대 HTTPS 주소를 사용한다. 로컬 미리보기만으로 공개 크롤러가 localhost 이미지에 접근할 수는 없다. 공개 후 확인하며 서비스가 오래된 메타데이터를 캐시할 수도 있다. 태그 존재를 실제 수집 성공으로 간주하지 않는다.

## 접근성·브라우저 범위

랜드마크·본문 건너뛰기·LaTeX 주석이 있는 수식·키보드 픽셀 이동·명시적 라벨·포커스·상태 안내·텍스트 격자 대체 입력을 제공한다. 이것이 WCAG 전체 적합성 감사 완료를 의미하지는 않는다. 칸이 작은 큰 마스크는 표준 텍스트 편집기를 사용한다.

네이티브 MathML 모양은 브라우저·수학 글꼴에 영향을 받는다. 기록된 환경에서 Chromium 화면을 확인하였으며 Firefox·WebKit·보조 기술은 후속 시험 대상이다. 인쇄 스타일은 제공하지만 모든 프린터·브라우저의 페이지 나눔을 보증하지 않는다.
