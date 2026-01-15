# 스와이프 가이드 UI 개선 구현 계획 (Glassmorphism & High Visibility)

## 개요
기존의 텍스트와 아이콘만 떠 있던 스와이프 가이드 UI를 개선하여 가독성을 높이고 사용자 주목도를 향상시킵니다.
`Glassmorphism` (유리 형태) 디자인을 적용하여 어떤 카드 배경 위에서도 잘 보이도록 하고, 브랜드 컬러를 활용하여 세련된 느낌을 더합니다.

## 구현 목표
1.  **가독성 확보**: 반투명한 검정 배경(`bg-neutral-900/80`)과 블러 효과(`backdrop-blur-md`)를 추가하여 텍스트와 아이콘을 명확하게 분리합니다.
2.  **시각적 강조**: 아이콘 크기를 키우고(`text-6xl`), 브랜드 컬러(`primary-orange`)를 적용하여 시선을 끕니다.
3.  **세련된 디자인**: 둥근 모서리(`rounded-[40px]`)와 은은한 테두리(`border-white/10`)로 프리미엄한 느낌을 줍니다.

## 수정 대상 파일
- `/apps/Being_geul_Final/templates/main.html`

## 상세 코드 변경 계획

### `templates/main.html`

기존의 단순 div 구조를 스타일이 적용된 컨테이너 구조로 변경합니다.

**변경 전:**
```html
<div id="swipe-guide"
    class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 pointer-events-none opacity-0 flex flex-col items-center justify-center gap-4">

    <div class="flex items-center justify-center drop-shadow-[0_4px_4px_rgba(0,0,0,0.3)]">
        <i class="fa-solid fa-hand-pointer text-5xl text-white" id="hand-icon"></i>
    </div>

    <div class="drop-shadow-[0_2px_4px_rgba(0,0,0,0.6)]">
        <p class="text-lg font-extrabold text-white whitespace-nowrap tracking-wide">
            왼쪽: 넘기기 👈&nbsp;|&nbsp; 👉 오른쪽: 찜 ❤️
        </p>
    </div>

</div>
```

**변경 후:**
```html
<div id="swipe-guide"
    class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 pointer-events-none opacity-0 flex flex-col items-center justify-center
           bg-neutral-900/80 backdrop-blur-md px-12 py-10 rounded-[30px] border border-white/10 shadow-2xl transition-all">

    <!-- 아이콘 영역: 크기 확대 및 브랜드 컬러 적용 -->
    <div class="flex items-center justify-center mb-6">
        <i class="fa-solid fa-hand-pointer text-6xl text-primary-orange drop-shadow-md" id="hand-icon"></i>
    </div>

    <!-- 텍스트 영역: 가독성 개선 -->
    <div class="text-center">
        <p class="text-xl font-bold text-white whitespace-nowrap tracking-wider mb-2">
            카드를 좌우로 밀어보세요
        </p>
        <div class="flex items-center justify-center gap-4 text-gray-300 font-medium text-base">
            <span class="flex items-center gap-1"><i class="fa-solid fa-arrow-left"></i> PASS</span>
            <span class="w-[1px] h-4 bg-gray-600"></span>
            <span class="flex items-center gap-1 text-primary-red font-bold">LIKE <i class="fa-solid fa-heart"></i></span>
        </div>
    </div>
</div>
```

## 작업 순서
1. `templates/main.html` 파일의 `#swipe-guide` 섹션을 위 코드로 교체합니다.
2. 기존 로직(`script.js`)은 ID 기반으로 작동하므로 별도 수정 없이 애니메이션이 정상 작동하는지 확인합니다.
