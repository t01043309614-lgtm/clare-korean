# CLAUDE.md — Clare의 한국어 콘텐츠

## 나는 누구인가
- 호칭: Clare. 나를 항상 Clare라고 불러줘.
- 나는 외국인에게 실생활 한국어를 가르치는 한국어 선생님이다.
- Instagram, YouTube Shorts, TikTok, Facebook용 한국어 교육 콘텐츠를 만든다.

## 내 학생과 시청자
- 자연스러운 실제 한국어를 배우고 싶은 외국인 한국어 학습자다.
- 교과서 표현보다 한국인이 일상에서 실제로 쓰는 표현을 알려준다.

## 숏폼 기본 형식
- 항상 다음 순서를 기본으로 한다:
Hook → 한국어 → Romanization → English → Meaning → Example
- Hook은 짧고 호기심이 생기게 영어로 쓴다.
- English는 한국어 표현의 자연스러운 영어 뜻을 짧게 쓴다.
- Meaning은 한국인이 언제, 어떤 상황에서 쓰는지 쉽고 짧게 설명한다.
- Example은 실제 대화에서 바로 쓸 수 있는 자연스러운 예문을 만든다.

## 스타일
- 설명은 짧고 명확하게 쓴다.
- 자연스럽고 실제 한국인이 사용하는 표현을 우선한다.
- 내가 주지 않은 사실이나 숫자를 지어내지 않는다.  

## Clare's Korean 기본 작업 규칙

앞으로 이 프로젝트의 모든 작업에서는 아래 규칙을 기본으로 따른다.

1. 작업 중인 workspace root의 index.html만 수정한다.
   같은 이름의 중복 폴더나 다른 index.html 복사본은 수정하지 않는다.

2. 기존 정상 기능과 디자인은 절대 깨뜨리지 않는다.
   - Flashcards
   - Grammar
   - Reactions
   - Flip all
   - Shuffle
   - 카드 flip
   - 기존 모든 음성
   - 탭 전환
   - 모바일 레이아웃

3. 음성 작업을 요청받으면 항상 한 번에 끝낸다.
   - 프로젝트의 지정된 또는 최근 m4a 파일 찾기
   - 무음 구간 분석
   - 필요한 개수로 자동 분리
   - 적절한 assets/audio 폴더에 저장
   - 기존 파일은 덮어쓰지 않기
   - 해당 카드/예문에 정확히 연결
   - 실제 화면에 🔊 버튼 렌더링
   - 버튼 클릭 시 해당 Clare 음성 재생
   - 기존 UI와 같은 디자인 사용
   - 실제 재생 가능 여부 검증

4. 파일 생성이나 audio 경로 연결만 하고 완료라고 하지 않는다.
   실제 브라우저 UI에서 사용할 수 있는 코드 상태까지 완성해야 한다.

5. 중간 단계에서 문제가 생기면 Clare에게 반복 작업을 요구하지 말고
   가능한 범위에서 원인을 찾아 스스로 수정하고 다시 검증한다.

6. 반복적인 폴더 생성, 파일명 변경, 음성 분리, 연결 작업은
   Clare에게 시키지 말고 Claude Code가 직접 처리한다.

7. 완료 전 반드시 기존 기능 회귀 여부와 JavaScript 오류를 확인한다.

8. 완료 보고는 짧게 한다.
   - 생성 수
   - 연결 수
   - 재생/작동 검증 결과
   - 문제가 있으면 문제만 설명

9. Clare가 브라우저에서 확인할 때 혼동하지 않도록
   작업 완료 후 실제 수정한 index.html의 경로를 알려준다.

## 검색 노출 (SEO)

- 카드 내용은 검색엔진이 읽을 수 있도록 index.html 안에 미리 글자로 들어가 있다(`<!-- prerender:ID -->` 구간).
- 카드/데이터를 추가하거나 수정한 뒤에는 커밋 전에 반드시 `python tools/prerender.py`를 실행해서 이 구간을 갱신한다.
- google82f9c3cf38653beb.html, robots.txt, sitemap.xml은 절대 지우지 말 것. (google82f9c3cf38653beb.html은 Google Search Console 인증 파일이라 이름과 내용도 바꾸지 않는다.)
- 새 코너나 탭을 추가하면 sitemap.xml도 같이 업데이트할 것. (지금은 한 페이지라 URL은 하나이므로, 최소한 `<lastmod>`를 작업한 날짜로 바꾼다.)

## 사이트 공통 규칙

모든 작업(다른 코너, 새 카드, 워크북 포함) 전에 이 섹션을 먼저 읽고 따른다. 사이트(index.html)와 워크북(tools/build_workbook.py로 만드는 PDF) 모두에 적용한다.

1. 번역 방지: 모든 카드의 한국어, 로마자, 영어 뜻에는 translate="no"가 있어야 하고, <head>에 <meta name="google" content="notranslate">가 있어야 한다. <html>은 lang="en"을 유지한다. index.html을 수정하거나 tools/prerender.py를 실행한 뒤에는 반드시 확인한다.
   - 카드 컨테이너(tabs, cardsGrid, grammarList, reactionsList, situationalTabs, situationalList, pairsGroups, quizList)의 `translate="no"`를 지우지 않는다.
   - 카드를 만드는 JS 함수에서 `card.className = ...` 바로 다음 줄의 `card.setAttribute("translate", "no");`를 지우지 않는다. 새 카드 종류를 만들면 같은 줄을 넣는다.
   - 워크북 HTML에도 notranslate 메타와 `translate="no"`가 들어간다(build_workbook.py가 자동으로 넣는다).

2. 로마자는 국립국어원 로마자 표기법(소리 나는 대로)을 따른다. 예: 얇다 yalda, 넓다 neolda, 짧다 jjalda. 하이픈은 쓰지 않는다(eommaneun).
   - 표준 발음대로 적는다: 필요 [피료] piryo, 적립 [정닙] jeongnip, 거짓말 [거진말] geojinmal, 웬일 [웬닐] wennil, 별말씀을요 byeolmalsseumeuryo.
   - 모음 앞의 ㄹ은 r, 받침 ㄹ은 l. 겹받침은 발음되는 것만 적는다.
   - 명사(체언) 뒤의 ㅎ은 밝혀 적는다: 시작해요 sijakhaeyo, 도착했어요 dochakhaesseoyo. 용언은 거센소리를 반영한다: 어떡해 eotteokae, 어떻게 eotteoke.
   - 된소리되기는 적지 않는다: 할게요 halgeyo, 독감 dokgam.
   - 하이픈 예: eommaneun (O) / eomma-neun (X), angyeongeul (O) / angyeong-eul (X). 영어 약어도 소리대로 적는다: TV를 → tibireul.

3. 카드 추가 시 먼저 중복 카드를 검색하고, 있으면 건너뛰고 보고한다.

4. 새 카드 형식: 이모지 / 한국어 / 로마자 / 영어 뜻 / Meaning 줄 / 예문(오디오) / 예문 로마자 / 예문 영어 뜻. 기존 카드 모양은 건드리지 않는다.
   - Flashcards: `meaning`과 `example.rr` 필드가 있는 카드에만 Meaning 줄과 예문 로마자가 보인다(`has-meaning`). 기존 카드에는 영향이 없다.

5. 배포 전 점검: 로마자 표기, translate="no", 오디오 조각 수를 확인하고 이상이 있으면 push 전에 보고한다.
   - `python tools/prerender.py`는 끝에 번역 방지와 로마자 하이픈을 자동으로 검사한다. 브라우저 없이 검사만 하려면 `python tools/prerender.py --check`. WARNING이 나오면 커밋하지 말고 먼저 고친다.
   - 오디오: 무음 기준으로 나눈 조각 수가 카드 수(단어 + 예문)와 다르면 임의로 맞추지 않고 보고한다.

6. 사용자가 명시하지 않은 파일(예: Topic4.m4a, Topic5.m4a)은 커밋하지 않는다.

7. 카드나 코너를 추가하면 sitemap.xml의 lastmod를 오늘 날짜로 갱신한다.

8. 새 규칙이나 수정 사항이 생기면 이 섹션에 추가한다.
   - 워크북 로마자는 index.html 카드 데이터에서 가져오므로, index.html을 고친 뒤 `python tools/build_workbook.py`로 PDF를 다시 만든다. 로마자에 하이픈이 있으면 빌드가 멈춘다.
   - 워크북 Level 1의 Everyday Korean은 처음 18장만 쓴다(`LEVEL1_EVERYDAY_COUNT`). 새 카드를 워크북에 넣는 건 Clare가 따로 지시할 때만.
   - 워크북 Level 2는 `python tools/build_workbook.py --level 2`로 만든다(assets/workbook/level2-everyday-korean.pdf). Level 1은 옵션 없이 실행할 때만 다시 만들어지므로, Level 2 작업 중에는 Level 1 PDF가 바뀌지 않는다. Level 2는 페이지 넘침이 있으면 PDF를 만들지 않고 멈춘다.
   - Mini Dialogues 대사는 index.html의 `dialoguesData`에 있고, 워크북 Level 2가 여기서 한국어·로마자·영어를 가져온다. 음성은 assets/audio/dialogues/dialogue{N}_line{M}.mp3.

## 배포

- 사이트 주소: https://clare-korean-flashcards.netlify.app/
- Netlify가 GitHub 저장소(origin/main)에 연결되어 있어서, 커밋 후 `git push origin main`을 하면 자동으로 재배포된다.
- "재배포" 요청 시: 커밋 → push → 위 주소에서 새 index.html과 새 음성 파일이 실제로 반영됐는지 확인까지 한다.