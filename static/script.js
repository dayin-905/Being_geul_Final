// ============================================================
// [0] GSAP & 플러그인 안전 등록
// ============================================================
if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
} else {
    console.warn("GSAP or ScrollTrigger not loaded.");
}

// ============================================================
// [1] 데이터 & 유틸리티 (전역 함수로 분리 - 페이지별 이동 용이)
// ============================================================

// [수정 1] 가짜 데이터 생성 함수(generatePolicyData) 삭제함.
// HTML에서 window 객체에 넣어준 DB 데이터만 사용. 없으면 빈 배열([]).
const tinderData = window.tinderData || [];
const allSlideData = window.allSlideData || [];

// [NEW] 사용자 프로필 및 활동 지수 로드 함수 (전역 등록 for 실시간 연동)
window.loadUserProfile = function () {
    const userEmail = localStorage.getItem('userEmail');
    if (!userEmail) return;

    fetch(`/api/mypage/profile?user_email=${userEmail}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }

            // 1) 이름 & 이메일
            const nameEl = document.getElementById('user-profile-name');
            const emailEl = document.getElementById('user-profile-email');
            if (nameEl) nameEl.innerText = `${data.name} 님`;
            if (emailEl) emailEl.innerText = data.email;

            // 2) 뱃지
            const badgesEl = document.getElementById('user-profile-badges');
            if (badgesEl) {
                let html = '';
                if (data.region_badge) {
                    html += `<span class="px-3 py-1 bg-gray-100 text-gray-600 text-xs font-bold rounded-lg">${data.region_badge}</span>`;
                }
                if (data.level_badge) {
                    html += `<span class="px-3 py-1 bg-orange-100 text-primary-orange text-xs font-bold rounded-lg">${data.level_badge}</span>`;
                }
                badgesEl.innerHTML = html;
            }

            // 3) 활동 지수
            const scoreTextEl = document.getElementById('activity-score-text');
            const progressBarEl = document.getElementById('activity-progress-bar');

            if (scoreTextEl) {
                scoreTextEl.innerHTML = `${data.activity_index}% <span class="text-base font-bold text-gray-500">${data.level_badge}</span>`;
            }
            if (progressBarEl) {
                const width = Math.min(data.activity_index, 100);
                progressBarEl.style.width = `${width}%`;
            }

            // 4) 카운트
            const likeCountEl = document.getElementById('user-like-count');
            const closingCountEl = document.getElementById('user-closing-count');

            if (likeCountEl) likeCountEl.innerText = data.like_count;
            if (closingCountEl) closingCountEl.innerText = data.closing_soon_count || 0;

            // 5) 프로필 아이콘
            const profileImg = document.getElementById('user-profile-img');
            if (profileImg) {
                // 직접 이미지 경로 설정
                const iconName = data.profile_icon || "avatar_1";
                profileImg.src = `/static/images/avatars/${iconName}.png`;
            }

            // [NEW] MBTI 데이터 저장 (전역 변수 활용)
            if (data.mbti) {
                window.userMbtiData = data.mbti;
                // 마이페이지 MBTI 카드의 텍스트 업데이트 (선택 사항)
                const mbtiCardTitle = document.querySelector('#mbti-card-title'); // id 필요 시 html 수정
                if (mbtiCardTitle) mbtiCardTitle.innerText = data.mbti.type_name;
            } else {
                window.userMbtiData = null;
            }
        })
        .catch(err => {
            console.error("Profile Load Error:", err);
        });
};

// [NEW] 카테고리별 색상 매핑 (all.html과 동일하게 유지)
const GENRE_COLORS = {
    "취업": { main: "#4A9EA8", bg: "#F0FDFA" },
    "취업/직무": { main: "#4A9EA8", bg: "#F0FDFA" },

    "주거": { main: "#F48245", bg: "#FFF7ED" },
    "주거/자립": { main: "#F48245", bg: "#FFF7ED" },

    "금융": { main: "#D9B36C", bg: "#FEFCE8" },
    "금융/생활비": { main: "#D9B36C", bg: "#FEFCE8" },

    "창업": { main: "#FF5A5F", bg: "#FEF2F2" },
    "창업/사업": { main: "#FF5A5F", bg: "#FEF2F2" },

    "복지": { main: "#A855F7", bg: "#FAF5FF" },
    "복지/문화": { main: "#A855F7", bg: "#FAF5FF" },

    "교육": { main: "#3B82F6", bg: "#EFF6FF" },
    "교육/자격증": { main: "#3B82F6", bg: "#EFF6FF" },

    "default": { main: "#777777", bg: "#F3F4F6" }
};

// [신규] DB 장르(genre)에 따라 이미지를 자동으로 매칭해주는 함수
function getCategoryImage(genre) {
    const map = {
        "취업/직무": "job",
        "창업/사업": "startup",
        "주거/자립": "housing",
        "금융/생활비": "finance",
        "교육/자격증": "growth",
        "복지/문화": "welfare"
    };
    // 매칭되는 영문명이 없으면 기본값 'welfare' 사용
    const prefix = map[genre] || "welfare";

    // 이미지 번호 랜덤 (1~5번) 또는 고정 가능. 현재는 랜덤.
    const imgIndex = Math.floor(Math.random() * 5) + 1;
    return `/static/images/card_images/${prefix}_${imgIndex}.webp`;
}

// 카드 HTML 생성 함수 (수정됨: DB 컬럼 반영)
function createCardHTML(item, isTinder = false) {
    // 1. DB 데이터 매핑 (undefined 방지 처리)
    const displayGenre = item.genre || "기타";       // DB 컬럼: genre
    const displayTitle = item.title || "제목 없음";  // DB 컬럼: title
    const displayDesc = item.summary || "";         // DB 컬럼: summary
    const displayDate = item.period || "상시";      // DB 컬럼: period
    const displayLink = item.link || "";            // DB 컬럼: link (원문 연결용)
    const displayRegion = item.region || "";        // [NEW] DB 컬럼: region

    // 2. 장르 기반 이미지 자동 생성
    const displayImage = getCategoryImage(displayGenre);

    // [NEW] 장르 색상 가져오기
    const colors = GENRE_COLORS[displayGenre] || GENRE_COLORS['default'];
    // Inline styles for dynamic colors to ensure application without rebuild
    const badgeStyle = `background-color: ${colors.bg}; color: ${colors.main}; border-color: ${colors.bg};`;
    // Tailwind arbitrary values for hover/text (will work with CDN)
    const textMainClass = `text-[${colors.main}]`;
    const hoverTextClass = `hover:text-[${colors.main}]`;
    const hoverGroupTextClass = `group-hover:text-[${colors.main}]`;

    // 3. 모달에 넘겨줄 데이터 객체 생성 (이미지 경로 포함)
    const modalData = {
        id: item.id, // [중요] 찜하기 기능 연동을 위해 ID 필수
        title: displayTitle,
        genre: displayGenre,
        desc: displayDesc,
        date: displayDate,
        image: displayImage,
        date: displayDate,
        image: displayImage,
        link: displayLink,
        region: displayRegion // [NEW] 모달에 지역 정보 전달
    };

    // [중요] JSON 변환 (따옴표 깨짐 방지)
    const jsonString = JSON.stringify(modalData).replace(/"/g, '&quot;');

    if (isTinder) {
        // [Tinder Card Design]
        const swipeIcons = `
            <div class="swipe-feedback pass absolute top-10 right-10 z-30 opacity-0 transition-none pointer-events-none transform rotate-[15deg]">
                <div class="border-4 border-gray-500 rounded-xl px-4 py-2 bg-white/90 backdrop-blur-sm shadow-xl">
                    <span class="text-4xl font-extrabold text-gray-500 tracking-widest">NOPE</span>
                </div>
            </div>
            <div class="swipe-feedback like absolute top-10 left-10 z-30 opacity-0 transition-none pointer-events-none transform -rotate-[15deg]">
                <div class="border-4 border-primary-orange rounded-xl px-4 py-2 bg-white/90 backdrop-blur-sm shadow-xl">
                    <span class="text-4xl font-extrabold text-primary-orange tracking-widest">LIKE</span>
                </div>
            </div>
        `;
        return `
            <div class="policy-card tinder-card absolute top-0 left-0 w-full h-full flex flex-col bg-white overflow-hidden shadow-xl rounded-[30px] cursor-grab" data-id="${item.id}">
                ${swipeIcons}
                <div class="card-image w-full h-[320px] bg-gray-50 relative shrink-0">
                    <img src="${displayImage}" alt="${displayTitle}" class="w-full h-full object-cover pointer-events-none">
                    <div class="absolute bottom-0 w-full h-20 bg-gradient-to-t from-white to-transparent"></div>
                </div>
                <div class="card-content flex flex-col justify-between flex-grow p-8 text-left bg-white relative z-10">
                    <div>
                        <div class="flex items-center gap-1 mb-3">
                            <span class="inline-block py-1 px-3 rounded-full text-sm font-bold border" style="${badgeStyle}">${displayGenre}</span>
                            ${displayRegion ? `<span class="bg-gray-100 text-gray-600 font-bold px-2 py-1 rounded-full text-sm">${displayRegion}</span>` : ''}
                        </div>
                        <h3 class="card-title text-2xl font-extrabold text-gray-900 leading-tight mb-3 line-clamp-2">${displayTitle}</h3>
                        <p class="card-desc text-base text-gray-500 font-medium line-clamp-3 leading-relaxed">${displayDesc}</p>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
                        <span class="card-date text-sm text-gray-400 font-bold"><i class="fa-regular fa-clock mr-1"></i> ${displayDate}</span>
                        
                        <button class="relative z-50 text-sm font-bold text-gray-900 underline decoration-gray-300 underline-offset-4 p-2 transition-colors ${hoverTextClass}" 
                                data-json="${jsonString}"
                                onclick="openCardModal(this); event.stopPropagation();">
                            자세히 보기
                        </button>
                    </div>
                </div>
            </div>`;
    } else {
        // [Slide Card Design]
        return `
            <div class="policy-card relative flex flex-col overflow-hidden rounded-[20px] bg-[#F6F6F7] shadow-sm cursor-pointer hover:shadow-xl transition-all group hover:-translate-y-2 hover:bg-white" 
                 data-json="${jsonString}"
                 data-id="${item.id}"
                 onclick="openCardModal(this)">
                
                <div class="card-image w-full h-[180px] flex items-end justify-center overflow-hidden bg-white">
                    <img src="${displayImage}" alt="${displayTitle}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110">
                </div>
                <div class="card-content p-6 flex flex-col gap-2">
                    <div class="flex items-center gap-1">
                        <span class="text-xs font-bold px-2 py-1 rounded-md" style="${badgeStyle}">${displayGenre}</span>
                        ${displayRegion ? `<span class="bg-white text-gray-600 font-bold px-2 py-1 rounded-md text-xs group-hover:bg-gray-100 transition-colors">${displayRegion}</span>` : ''}
                    </div>
                    <h3 class="card-title text-xl font-extrabold text-[#222] line-clamp-2 transition-colors ${hoverGroupTextClass}">${displayTitle}</h3>
                    <p class="card-desc text-sm text-[#666] font-medium line-clamp-2">${displayDesc}</p>
                    <span class="card-date text-xs text-[#888] mt-2">${displayDate}</span>
                </div>
            </div>`;
    }
}

// 틴더 스와이프 클래스
class CardSwiper {
    constructor(container, data) {
        this.container = container;
        this.data = data;
        this.init();
    }
    init() {
        if (!this.container) return;
        // [수정 2] 데이터 없음 처리 추가
        if (!this.data || this.data.length === 0) {
            this.container.innerHTML = '<div class="flex flex-col items-center justify-center h-full text-gray-400"><p class="text-xl font-bold">표시할 정책이 없습니다.</p><p class="text-sm mt-2">조건을 변경하거나 나중에 다시 시도해주세요.</p></div>';
            return;
        }

        this.container.innerHTML = '<div class="no-more-cards">모든 카드를 확인했습니다! 🎉</div>';
        [...this.data].reverse().forEach(item => {
            this.container.insertAdjacentHTML('beforeend', createCardHTML(item, true));
        });
        this.cards = document.querySelectorAll('.tinder-card');
        this.setupEvents();
        if (typeof gsap !== 'undefined') {
            // [최적화] 모든 카드를 애니메이션하면 렉이 걸리므로, 상위 5개만 움직이게 설정
            gsap.from(".tinder-card:nth-last-child(-n+5)", { y: 100, opacity: 0, duration: 0.8, stagger: 0.1, ease: "back.out(1.7)" });
        }
    }
    setupEvents() {
        this.cards.forEach((card) => { this.addListeners(card); });

        // [NEW] 키보드 이벤트 리스너 추가 (왼쪽/오른쪽 화살표)
        document.addEventListener('keydown', (e) => {
            // 현재 남아있는 카드 중 가장 위에 있는(DOM상 마지막) 카드 선택
            const currentCards = document.querySelectorAll('.tinder-card');
            if (currentCards.length === 0) return;
            const topCard = currentCards[currentCards.length - 1]; // 맨 위 카드

            if (e.key === 'ArrowLeft') {
                this.swipeCard(topCard, 'left');
            } else if (e.key === 'ArrowRight') {
                this.swipeCard(topCard, 'right');
            }
        });
    }
    addListeners(card) {
        let isDragging = false, startX = 0, currentX = 0;
        const likeBadge = card.querySelector('.swipe-feedback.like');
        const passBadge = card.querySelector('.swipe-feedback.pass');
        const startDrag = (e) => { isDragging = true; startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX; card.style.transition = 'none'; };
        const moveDrag = (e) => {
            if (!isDragging) return;
            const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            currentX = clientX - startX;
            const rotate = currentX * 0.05;
            card.style.transform = `translateX(${currentX}px) rotate(${rotate}deg)`;
            const opacity = Math.min(Math.abs(currentX) / 100, 1);
            if (currentX > 0) { if (likeBadge) likeBadge.style.opacity = opacity; if (passBadge) passBadge.style.opacity = 0; }
            else { if (passBadge) passBadge.style.opacity = opacity; if (likeBadge) likeBadge.style.opacity = 0; }
        };
        const endDrag = () => {
            if (!isDragging) return;
            isDragging = false;
            card.style.transition = 'transform 0.3s ease';
            if (likeBadge) likeBadge.style.opacity = 0;
            if (passBadge) passBadge.style.opacity = 0;
            if (currentX > 150) this.swipeCard(card, 'right');
            else if (currentX < -150) this.swipeCard(card, 'left');
            else card.style.transform = 'translateX(0) rotate(0)';
            currentX = 0;
        };
        card.addEventListener('mousedown', startDrag);
        document.addEventListener('mousemove', moveDrag);
        document.addEventListener('mouseup', endDrag);
        card.addEventListener('touchstart', startDrag);
        document.addEventListener('touchmove', moveDrag, { passive: false });
        document.addEventListener('touchend', endDrag);
    }
    swipeCard(card, direction) {
        const moveX = direction === 'right' ? 1000 : -1000;
        const rotate = direction === 'right' ? 30 : -30;
        card.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
        card.style.transform = `translateX(${moveX}px) rotate(${rotate}deg)`;
        card.style.opacity = '0';
        setTimeout(() => {
            card.remove();

            // [NEW] API 호출 (로그인 상태일 때만)
            const userEmail = localStorage.getItem('userEmail');
            if (userEmail) {
                const actionType = direction === 'right' ? 'like' : 'pass';
                const policyId = card.getAttribute('data-id'); // data-id 속성 필요

                fetch('/api/mypage/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_email: userEmail,
                        policy_id: parseInt(policyId),
                        type: actionType
                    })
                }).catch(err => console.error("Action Save Error:", err));
            }
        }, 500);
    }
}

// [수정 3] 정책 상세 모달 열기 (기존 window.openModal 대체 및 기능 강화)
// [삭제됨] window.openCardModal은 이제 static/policy_modal.js에서 통합 관리합니다.

// ============================================================
// [2] Controllers (Auth & Share) - ★ 진짜 서버 통신용 코드 ★
// ============================================================

const AuthController = {
    // [상태 관리]
    currentRegion: null,
    pendingCallback: null,

    // 1. 초기화: 이벤트 위임 (버튼이 늦게 생겨도 무조건 클릭 감지)
    init: function () {
        // [NEW] 엔터키 지원
        const addEnter = (id, fn) => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    fn.call(this);
                }
            });
        };
        addEnter('login-id', this.handleLogin);
        addEnter('login-pw', this.handleLogin);
        addEnter('signup-name', this.handleSignup);
        addEnter('signup-id', this.handleSignup);
        addEnter('signup-pw', this.handleSignup);

        document.addEventListener('click', (e) => {
            // [수정] 클릭한 요소가 버튼 안의 아이콘(SVG)일 수도 있으니, 가장 가까운 ID 가진 요소를 찾습니다.
            const target = e.target.closest('[id]');
            if (!target) return; // ID 없는 빈 공간 클릭은 무시

            // (1) 가입 완료 버튼
            if (target.id === 'btn-signup-submit') {
                e.preventDefault();
                this.handleSignup();
            }

            // (2) 로그인 완료 버튼
            if (target.id === 'btn-login-submit') {
                e.preventDefault();
                this.handleLogin();
            }

            // (3) 모달 닫기 버튼들 (이제 아이콘 눌러도 닫힘!)
            if (target.id === 'btn-modal-close-icon') {
                this.closeModal();
            }
            if (target.id === 'btn-modal-browse') {
                this.closeModal();
                // 💡 [핵심] 모달 닫은 뒤, 원래 하려던 동작(페이지 이동) 계속 진행
                if (this.pendingCallback) {
                    this.pendingCallback();
                }
            }

            // (4) 뷰 전환 버튼들
            if (['btn-promo-login', 'btn-goto-login'].includes(target.id)) this.switchView('login');
            if (['btn-promo-signup', 'btn-goto-signup'].includes(target.id)) this.switchView('signup');

            // (5) 로그인 트리거 (class로 찾기)
            const trigger = e.target.closest('.js-login-trigger');
            if (trigger) {
                const mode = trigger.dataset.mode || 'login';
                this.open(mode);
            }
        });
    },

    // 2. 모달 열기
    open: function (mode = 'promo', regionName = null, count = 0, callback = null) {
        const modal = document.getElementById('auth-modal');
        const modalContent = document.getElementById('auth-modal-content');
        if (!modal) return;

        this.currentRegion = regionName;
        this.pendingCallback = callback;

        // UI 텍스트 업데이트
        const elements = {
            badgeContainer: document.getElementById('signup-region-badge-container'),
            badgeText: document.getElementById('signup-region-badge'),
            title: document.getElementById('auth-promo-title'),
            desc: document.getElementById('auth-promo-desc')
        };

        if (regionName) {
            if (elements.badgeText) elements.badgeText.innerText = regionName;
            if (elements.badgeContainer) elements.badgeContainer.style.display = 'inline-flex';
            if (elements.title) elements.title.innerHTML = `<span class="text-[#4A9EA8]">${regionName}</span> 소식을<br>받아보시겠습니까?`;
            if (elements.desc) elements.desc.innerHTML = `총 ${count ? count.toLocaleString() : 0}건의 청년 정책을<br>놓치지 말고 확인하세요.`;
        } else {
            if (elements.badgeContainer) elements.badgeContainer.style.display = 'none';
        }

        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false'); // [FIX] 접근성 경고 해결
        setTimeout(() => {
            modal.classList.remove('opacity-0');
            if (modalContent) {
                modalContent.classList.remove('scale-95');
                modalContent.classList.add('scale-100');
            }
        }, 10);

        this.switchView(mode);
    },

    // 3. 모달 닫기
    closeModal: function () {
        const modal = document.getElementById('auth-modal');
        const modalContent = document.getElementById('auth-modal-content');
        if (!modal) return;

        modal.classList.add('opacity-0');
        if (modalContent) {
            modalContent.classList.remove('scale-100');
            modalContent.classList.add('scale-95');
        }
        setTimeout(() => {
            modal.classList.add('hidden');
            modal.setAttribute('aria-hidden', 'true'); // [FIX] 접근성 경고 해결
            document.querySelectorAll('.auth-input').forEach(input => input.value = '');
        }, 300);
    },

    // 4. 화면 전환
    switchView: function (viewName) {
        ['promo', 'signup', 'login'].forEach(v => {
            const el = document.getElementById(`auth-view-${v}`);
            if (el) {
                el.classList.add('hidden');
                el.classList.remove('flex');
            }
        });
        const target = document.getElementById(`auth-view-${viewName}`);
        if (target) {
            target.classList.remove('hidden');
            target.classList.add('flex');
        }
    },

    // 5. [API] 회원가입 처리 (★ 여기가 진짜 핵심입니다!)
    handleSignup: async function () {
        const email = document.getElementById('signup-id').value;
        const password = document.getElementById('signup-pw').value;
        const name = document.getElementById('signup-name').value;

        if (!email || !password || !name) {
            alert("모든 정보를 입력해주세요.");
            return;
        }

        // [DEBUG] 회원가입 데이터 확인
        console.log("Signup Payload:", { email, name, region: this.currentRegion });

        try {
            // 진짜 서버로 데이터 전송!
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    name: name,
                    region: this.currentRegion
                })
            });

            const result = await response.json();

            if (response.ok) {
                alert(`✅ 가입 성공: ${result.message}\n로그인 해주세요!`);
                this.switchView('login');
            } else {
                alert(`❌ 가입 실패: ${result.detail}`);
            }
        } catch (error) {
            console.error("통신 에러:", error);
            alert("서버 연결 중 오류가 발생했습니다.");
        }
    },

    // 6. [API] 로그인 처리 (★ 여기도 진짜!)
    handleLogin: async function () {
        const email = document.getElementById('login-id').value;
        const password = document.getElementById('login-pw').value;

        if (!email || !password) {
            alert("아이디와 비밀번호를 입력해주세요.");
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, password: password })
            });

            const result = await response.json();

            if (response.ok) {
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userEmail', result.user.email);
                localStorage.setItem('userName', result.user.name);

                alert(`${result.user.name}님 환영합니다!`);
                this.closeModal();
                checkLoginState();

                if (this.pendingCallback) {
                    this.pendingCallback();
                } else {
                    location.reload();
                }
            } else {
                alert(`로그인 실패: ${result.detail}`);
            }
        } catch (error) {
            console.error(error);
            alert("서버 연결 중 오류가 발생했습니다.");
        }
    }
};

// ShareController는 님이 올리신 코드 그대로 쓰셔도 됩니다.
const ShareController = {
    // ... (기존 코드 유지)
    el: document.getElementById('share-modal'),
    input: document.getElementById('share-url-input'),
    btnClose: document.getElementById('btn-share-close'),
    btnCopy: document.getElementById('btn-copy-url'),

    init: function () { if (!this.el) return; this.bindEvents(); },
    show: function () {
        this.el.classList.remove('hidden');
        if (this.input) this.input.value = window.location.href;
        if (typeof gsap !== 'undefined') {
            gsap.to(this.el, { opacity: 1, duration: 0.3 });
            const content = this.el.querySelector('div');
            if (content) gsap.to(content, { scale: 1, duration: 0.3, ease: 'back.out(1.2)' });
        }
    },
    hide: function () {
        if (typeof gsap !== 'undefined') {
            const content = this.el.querySelector('div');
            gsap.to(this.el, { opacity: 0, duration: 0.2 });
            if (content) {
                gsap.to(content, { scale: 0.95, duration: 0.2, onComplete: () => { this.el.classList.add('hidden'); } });
            } else { setTimeout(() => this.el.classList.add('hidden'), 200); }
        } else { this.el.classList.add('hidden'); }
    },
    copy: function () {
        if (this.input) {
            this.input.select();
            navigator.clipboard.writeText(this.input.value).then(() => {
                alert("URL이 복사되었습니다! 🎉"); this.hide();
            }).catch(() => { alert("복사 실패."); });
        }
    },
    bindEvents: function () {
        if (this.btnClose) this.btnClose.onclick = () => this.hide();
        if (this.btnCopy) this.btnCopy.onclick = () => this.copy();
        this.el.addEventListener('click', (e) => { if (e.target === this.el) this.hide(); });
    }
};

window.openAuthModal = function (mode, regionName, count, callback) { AuthController.open(mode, regionName, count, callback); };

// [NEW] Social Login Trigger (Global)
window.socialLogin = function (provider) {
    if (!['google', 'naver'].includes(provider)) return;
    // 백엔드 EndPoint로 이동 -> 리다이렉트 -> 로그인 -> Callback -> 메인으로 복귀
    window.location.href = `/api/auth/${provider}/login`;
};

// ============================================================
// [3] 초기화 및 메인 로직
// ============================================================

async function checkLoginState() {
    // [NEW] 0. OAuth 리다이렉트 복귀 처리 (URL 파라미터 확인)
    const urlParams = new URLSearchParams(window.location.search);
    const socialLogin = urlParams.get('social_login'); // success

    if (socialLogin === 'success') {
        const email = urlParams.get('email');
        const name = urlParams.get('name');

        if (email && name) {
            // 로컬 스토리지 저장 (로그인 처리)
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userName', name);

            // 깔끔한 URL을 위해 파라미터 제거 (선택 사항)
            window.history.replaceState({}, document.title, window.location.pathname);

            alert(`${name}님, 소셜 로그인 성공! 환영합니다.`);

            // [NEW] 메인 페이지로 이동
            window.location.href = '/main.html';
        }
    }

    // 1. 서버에 "나 로그인 맞아?" 물어보기
    try {
        const res = await fetch('/api/auth/verify');
        if (!res.ok) {
            // 서버가 "너 아닌데?"(401)라고 하면 청소!
            localStorage.clear();
            return; // 함수 종료
        }
    } catch (e) {
        localStorage.clear();
        return;
    }

    // [수정] 변수 선언 및 로컬 스토리지 값 로드 (ReferenceError 해결)
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const userEmail = localStorage.getItem('userEmail');

    if (isLoggedIn && userEmail) {
        // [FIX] nav.html의 자체 스크립트가 UI를 제어하므로, 여기서 강제 innerHTML 주입을 하지 않습니다.
        // 기존 코드가 nav.html의 변경사항(로그아웃 버튼 등)을 덮어쓰는 문제를 해결했습니다.
        /*
        const pcNavList = document.getElementById('pc-nav-list');
        if (pcNavList) {
            pcNavList.innerHTML = `...`;
        }
        const mobileProfile = document.getElementById('mobile-profile-section');
        if (mobileProfile) {
            mobileProfile.innerHTML = `...`;
        }
        */
        const mobileLogout = document.getElementById('mobile-logout-area');
        if (mobileLogout) mobileLogout.classList.remove('hidden');

        const introLoginBtn = document.getElementById('btn-intro-login');
        if (introLoginBtn) introLoginBtn.style.display = 'none';
    }
}

window.handleLogout = function () {
    localStorage.removeItem('virtualUser');
    localStorage.removeItem('isLoggedIn');
    alert('로그아웃 되었습니다.');
    location.reload();
};

document.addEventListener("DOMContentLoaded", () => {
    AuthController.init();
    ShareController.init();
    checkLoginState();

    // 햄버거 메뉴
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const closeBtn = document.getElementById('close-btn');
    const menuOverlay = document.getElementById('mobile-menu-overlay');
    const menuPanel = document.getElementById('mobile-menu-panel');
    const openMenu = () => { if (!menuOverlay) return; menuOverlay.classList.remove('hidden'); setTimeout(() => { menuOverlay.classList.remove('opacity-0'); menuPanel.classList.remove('translate-x-full'); }, 10); document.body.classList.add('menu-open'); };
    const closeMenu = () => { if (!menuOverlay) return; menuOverlay.classList.add('opacity-0'); menuPanel.classList.add('translate-x-full'); document.body.classList.remove('menu-open'); setTimeout(() => { menuOverlay.classList.add('hidden'); }, 300); };

    if (hamburgerBtn) hamburgerBtn.addEventListener('click', openMenu);
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
    if (menuOverlay) menuOverlay.addEventListener('click', (e) => { if (e.target === menuOverlay) closeMenu(); });

    const mobileLogoutBtn = document.getElementById('logout-btn-mobile');
    if (mobileLogoutBtn) mobileLogoutBtn.addEventListener('click', window.handleLogout);

    const btnShare = document.getElementById('btn-share');
    if (btnShare) btnShare.addEventListener('click', () => ShareController.show());

    // --------------------------------------------------------
    // [MAIN PAGE] Animation Logic
    // --------------------------------------------------------
    if (window.location.pathname.includes('main.html') || document.querySelector('.header-text')) {

        window.initHeaderAnimation = () => {
            const headerTitle = document.querySelector('.header-text h1');
            const headerDesc = document.querySelector('.header-text p');
            const headerVideo = document.querySelector('.header-image');
            if (headerTitle && headerDesc && typeof gsap !== 'undefined') {
                gsap.set([headerTitle, headerDesc], { autoAlpha: 0, y: 50 });
                if (headerVideo) gsap.set(headerVideo, { autoAlpha: 0, x: 50 });
            }
        };
        window.playHeaderAnimation = () => {
            const headerTitle = document.querySelector('.header-text h1');
            const headerDesc = document.querySelector('.header-text p');
            const headerVideo = document.querySelector('.header-image');
            if (headerTitle && headerDesc && typeof gsap !== 'undefined') {
                const tl = gsap.timeline();
                tl.to([headerTitle, headerDesc], { autoAlpha: 1, y: 0, duration: 1, ease: "power3.out", stagger: 0.2 });
                if (headerVideo) tl.to(headerVideo, { autoAlpha: 1, x: 0, duration: 1, ease: "power3.out" }, "<0.2");
            }
        };
        window.initHeaderAnimation();

        // Lottie
        const lottieContainer = document.getElementById('lottie-container');
        if (lottieContainer && typeof lottie !== 'undefined') {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('anim') === '1') {
                try {
                    const animation = lottie.loadAnimation({ container: lottieContainer, renderer: 'svg', loop: false, autoplay: true, path: '/static/images/intro_animation.json' });
                    const finishLoading = () => {
                        const pl = document.getElementById("preloader");
                        if (pl && typeof gsap !== 'undefined') { gsap.to(pl, { opacity: 0, duration: 0.5, onComplete: () => { pl.style.display = "none"; window.playHeaderAnimation(); } }); }
                        else if (pl) { pl.style.display = "none"; }
                    };
                    animation.addEventListener('complete', finishLoading);
                    animation.addEventListener('data_failed', finishLoading);
                } catch (e) { console.log("Lottie Error"); }
            } else { if (document.getElementById("preloader")) document.getElementById("preloader").style.display = "none"; window.playHeaderAnimation(); }
        } else { if (document.getElementById("preloader")) document.getElementById("preloader").style.display = "none"; window.playHeaderAnimation(); }

        // [애플 배너 복구]
        const icons = document.querySelectorAll('.cycling-icon');
        const keywordSpan = document.getElementById('banner-keyword');
        if (icons.length > 0 && keywordSpan && typeof gsap !== 'undefined') {
            let iconTl = gsap.timeline({ repeat: -1 });
            icons.forEach((icon, index) => {
                const newText = icon.getAttribute('data-text');
                iconTl.to(icon, { opacity: 1, scale: 1.2, duration: 0.5, ease: "back.out(1.7)" }, "start" + index)
                    .to(keywordSpan, { opacity: 0, y: 10, duration: 0.2, onComplete: () => { keywordSpan.innerText = newText; } }, "start" + index)
                    .to(keywordSpan, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, ">")
                    .to(icon, { opacity: 0, scale: 0.8, duration: 0.3, delay: 1.5, ease: "power2.in" }, "end" + index);
            });
        }

        // Swipe Guide
        const guideEl = document.getElementById('swipe-guide');
        const handIcon = document.getElementById('hand-icon');
        if (guideEl && handIcon && typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
            gsap.to(handIcon, { x: -15, y: 10, rotation: -10, duration: 0.8, yoyo: true, repeat: -1, ease: "power1.inOut" });
            ScrollTrigger.create({ trigger: ".tinder-section", start: "top 60%", once: true, onEnter: () => { if (guideEl.style.display !== 'none') gsap.to(guideEl, { autoAlpha: 1, duration: 0.5 }); } });
            const hideGuide = () => { gsap.to(guideEl, { autoAlpha: 0, duration: 0.3, onComplete: () => { guideEl.style.display = 'none'; } }); };
            if (document.getElementById('tinder-list')) {
                document.getElementById('tinder-list').addEventListener('mousedown', hideGuide, { once: true });
                document.getElementById('tinder-list').addEventListener('touchstart', hideGuide, { once: true });
            }
        }
    }

    // --------------------------------------------------------
    // [ABOUT PAGE] Animation Logic
    // --------------------------------------------------------
    if (typeof gsap !== 'undefined') {
        if (document.querySelector('.about-title')) {
            gsap.from(".about-title", { y: 50, opacity: 0, duration: 1, ease: "power3.out", delay: 0.2 });
        }
        if (document.querySelector('.team-card') && typeof ScrollTrigger !== 'undefined') {
            gsap.from(".team-card", {
                y: 100, opacity: 0, duration: 0.8, stagger: 0.2,
                scrollTrigger: { trigger: ".team-grid", start: "top 80%" }
            });
        }
    }

    // --------------------------------------------------------
    // [RENDERERS] Cards & MyPage
    // --------------------------------------------------------

    // [수정 완료] 메인 슬라이드 2줄 렌더링
    const slideRow1 = document.getElementById('slide-row-1');
    const slideRow2 = document.getElementById('slide-row-2');

    // [수정 4] 데이터 없음 처리 및 렌더링
    if (allSlideData.length > 0) {
        // 무한 스크롤 느낌을 위해 데이터 복제
        const infiniteData = [...allSlideData, ...allSlideData];

        if (slideRow1) {
            slideRow1.innerHTML = infiniteData.map(item => createCardHTML(item, false)).join('');
        }
        if (slideRow2) {
            slideRow2.innerHTML = infiniteData.map(item => createCardHTML(item, false)).join('');
        }
    } else {
        // 데이터가 없을 때 표시할 UI
        const emptyMsg = '<div class="w-full text-center py-10 text-gray-500">등록된 정책이 없습니다.</div>';
        if (slideRow1) slideRow1.innerHTML = emptyMsg;
        if (slideRow2) slideRow2.innerHTML = '';
    }

    // 틴더 카드
    const tinderList = document.getElementById('tinder-list');
    if (tinderList) new CardSwiper(tinderList, tinderData);

    // 마이페이지
    // 마이페이지 (API 연동 버전)
    const mypageList = document.getElementById('mypage-list');
    if (mypageList) {
        const userEmail = localStorage.getItem('userEmail');

        if (!userEmail) {
            mypageList.innerHTML = `<div class="empty-state"><p>로그인이 필요한 서비스입니다.</p></div>`;
        } else {


            // [NEW] 1.5. 사용자 프로필 및 활동 지수 가져오기 (함수 호출로 대체)
            if (typeof window.loadUserProfile === 'function') {
                window.loadUserProfile();
            }

            // 2. 차트 데이터 가져오기

            // 차트 업데이트 함수 (전역 등록)
            window.updateMyPageChart = function () {
                const ctx = document.getElementById('myChart');
                const currentUserEmail = localStorage.getItem('userEmail');
                // Chart.js가 로드되지 않았거나 필수 요소가 없으면 중단
                if (!ctx || typeof Chart === 'undefined' || !currentUserEmail) return;

                fetch(`/api/mypage/stats?user_email=${currentUserEmail}`)
                    .then(res => res.json())
                    .then(stats => {
                        // [FIX] 기존 차트 파괴 로직 강화 (v2, v3, v4 호환)
                        const existingChart = Chart.getChart ? Chart.getChart(ctx) : null;
                        if (existingChart) {
                            existingChart.destroy();
                        } else if (window.myRadarChart instanceof Chart) {
                            window.myRadarChart.destroy();
                        }

                        // [데이터 검증] 모든 값이 0인지 확인 (디버깅용)
                        const allZero = stats.data.every(val => val === 0);

                        // [NEW] 데이터가 없으면 그래프 대신 안내 메시지 표시
                        if (allZero) {
                            if (existingChart) existingChart.destroy();
                            if (window.myRadarChart instanceof Chart) window.myRadarChart.destroy();

                            // 캔버스 숨기고 메시지 표시
                            ctx.style.display = 'none';
                            let msgEl = document.getElementById('chart-empty-msg');
                            if (!msgEl) {
                                msgEl = document.createElement('div');
                                msgEl.id = 'chart-empty-msg';
                                msgEl.className = 'absolute inset-0 flex flex-col items-center justify-center text-gray-400';
                                msgEl.innerHTML = '<i class="fa-solid fa-chart-pie text-4xl mb-2 opacity-50"></i><span class="text-xs font-bold mt-2">아직 데이터가 부족해요</span>';
                                ctx.parentElement.appendChild(msgEl);
                                ctx.parentElement.style.position = 'relative';
                            } else {
                                msgEl.style.display = 'flex';
                            }
                            return;
                        } else {
                            // 데이터 있으면 메시지 숨기고 캔버스 보이기
                            ctx.style.display = 'block';
                            const msgEl = document.getElementById('chart-empty-msg');
                            if (msgEl) msgEl.style.display = 'none';
                        }

                        // 차트 생성
                        window.myRadarChart = new Chart(ctx, {
                            type: 'radar',
                            data: {
                                labels: stats.labels,
                                datasets: [{
                                    label: '나의 관심도',
                                    data: stats.data,
                                    backgroundColor: 'rgba(244, 130, 69, 0.2)',
                                    borderColor: '#F48245',
                                    pointBackgroundColor: '#F48245',
                                    pointBorderColor: '#fff',
                                    pointHoverBackgroundColor: '#fff',
                                    pointHoverBorderColor: '#F48245',
                                    borderWidth: 2
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                // [중요] Chart.js 버전에 따른 스케일 옵션 호환성 처리
                                // v3, v4: scales.r 사용
                                scales: {
                                    r: {
                                        min: 0,
                                        max: 120, // [FIX] 120점까지 확장 (재미 요소)
                                        beginAtZero: true,
                                        angleLines: { display: true, color: '#f3f4f6' },
                                        grid: { circular: false, color: '#f3f4f6' },
                                        pointLabels: {
                                            font: { size: 12, family: 'Pretendard', weight: 'bold' },
                                            color: '#6b7280'
                                        },
                                        ticks: {
                                            display: false,
                                            stepSize: 20,
                                            count: 7 // 0, 20, 40, 60, 80, 100, 120
                                        }
                                    }
                                },
                                // v2: scale 사용 (구버전 호환)
                                scale: {
                                    ticks: {
                                        beginAtZero: true,
                                        min: 0,
                                        max: 120,
                                        stepSize: 20,
                                        display: false
                                    },
                                    pointLabels: { fontSize: 12, fontColor: '#6b7280' },
                                    gridLines: { color: '#f3f4f6' }
                                },
                                plugins: {
                                    legend: { display: false },
                                    tooltip: {
                                        backgroundColor: 'rgba(17, 24, 39, 0.9)',
                                        titleFont: { family: 'Pretendard' },
                                        bodyFont: { family: 'Pretendard' },
                                        padding: 10,
                                        cornerRadius: 8,
                                        callbacks: {
                                            label: function (context) {
                                                return ` 나의 관심도: ${context.raw}`;
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    })
                    .catch(err => console.error("Stats Update Error:", err));
            };

            // 최초 실행
            // 최초 실행
            window.updateMyPageChart();
        }
    }

    // --------------------------------------------------------
    // [MODAL] Profile Avatar Selection
    // --------------------------------------------------------
    const avatarModal = document.getElementById('avatar-modal');
    const btnEditProfile = document.getElementById('btn-edit-profile');
    const btnCloseModal = document.getElementById('close-avatar-modal');
    const btnSaveAvatar = document.getElementById('save-avatar-btn');
    const avatarOptions = document.querySelectorAll('.avatar-option');

    let selectedAvatar = null;

    if (avatarModal && btnEditProfile) {
        // Open Modal
        btnEditProfile.addEventListener('click', () => {
            avatarModal.classList.remove('hidden', 'pointer-events-none');
            // Slight delay for animation
            setTimeout(() => {
                avatarModal.classList.remove('opacity-0');
            }, 10);
        });

        // Close Modal
        function closeAvatarModal() {
            avatarModal.classList.add('opacity-0');
            setTimeout(() => {
                avatarModal.classList.add('hidden', 'pointer-events-none');
            }, 300);
        }

        if (btnCloseModal) btnCloseModal.addEventListener('click', closeAvatarModal);

        // Select logic
        avatarOptions.forEach(opt => {
            opt.addEventListener('click', () => {
                // UI Reset
                avatarOptions.forEach(o => {
                    o.classList.remove('ring-4', 'ring-orange-200', 'bg-orange-50');
                    const indicator = o.querySelector('.active-indicator');
                    if (indicator) {
                        indicator.classList.add('hidden');
                        indicator.classList.remove('flex');
                    }
                });

                // Active State
                opt.classList.add('ring-4', 'ring-orange-200', 'bg-orange-50');
                const activeIndicator = opt.querySelector('.active-indicator');
                if (activeIndicator) {
                    activeIndicator.classList.remove('hidden');
                    activeIndicator.classList.add('flex');
                }

                selectedAvatar = opt.getAttribute('data-icon');
            });
        });

        // Save Logic
        if (btnSaveAvatar) {
            btnSaveAvatar.addEventListener('click', () => {
                if (!selectedAvatar) {
                    alert('캐릭터를 선택해주세요!');
                    return;
                }

                const userEmail = localStorage.getItem('userEmail');
                if (!userEmail) return;

                fetch('/api/mypage/profile/icon', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_email: userEmail,
                        icon_name: selectedAvatar
                    })
                })
                    .then(res => {
                        if (res.ok) {
                            closeAvatarModal();
                            // Refresh Profile
                            if (typeof window.loadUserProfile === 'function') {
                                window.loadUserProfile();
                            }
                        } else {
                            alert('저장에 실패했습니다.');
                        }
                    })
                    .catch(err => console.error(err));
            });
        }
    }

    // --------------------------------------------------------
    // [NEW] MyPage Manager (찜한 정책 관리 + 필터링)
    // --------------------------------------------------------
    const MyPageManager = {
        isEditMode: false,
        currentPage: 1,
        itemsPerPage: 12,

        // [NEW] Filter States
        currentKeyword: '',
        currentCategory: null,
        currentRegion: null,
        currentSort: 'latest',

        // Core Elements
        btnManage: document.getElementById('btn-manage-likes'),
        editControls: document.getElementById('edit-controls'),
        checkAll: document.getElementById('check-all-likes'),
        btnDelete: document.getElementById('btn-delete-likes'),
        listContainer: document.getElementById('mypage-list'),
        paginationContainer: document.getElementById('pagination-container'),

        // [NEW] Search & Filter Elements
        btnToggleSearch: document.getElementById('btn-toggle-search'),
        searchBar: document.getElementById('mypage-search-bar'),
        inputSearch: document.getElementById('mypage-search-input'),

        btnCategory: document.getElementById('btn-filter-category'),
        dropdownCategory: document.getElementById('dropdown-category'),
        labelCategory: document.getElementById('label-category'),

        btnRegion: document.getElementById('btn-filter-region'),
        labelRegion: document.getElementById('label-region'),

        btnSort: document.getElementById('btn-filter-sort'),
        dropdownSort: document.getElementById('dropdown-sort'),
        labelSort: document.getElementById('label-sort'),

        init: function () {
            // 초기 로드
            if (this.listContainer) {
                this.fetchLikes(1);
            }

            this.bindEvents(); // 기존 편집 모드 이벤트
            this.bindFilterEvents(); // 신규 필터 이벤트
        },

        bindEvents: function () {
            // Toggle Edit Mode
            if (this.btnManage) {
                this.btnManage.addEventListener('click', () => this.toggleEditMode());
            }

            // Select All
            if (this.checkAll) {
                this.checkAll.addEventListener('change', (e) => {
                    const checkboxes = document.querySelectorAll('.policy-check');
                    checkboxes.forEach(cb => cb.checked = e.target.checked);
                });
            }

            // Delete Action
            if (this.btnDelete) {
                this.btnDelete.addEventListener('click', () => this.deleteSelected());
            }
        },

        bindFilterEvents: function () {
            // 1. Toggle Search Bar
            if (this.btnToggleSearch) {
                this.btnToggleSearch.addEventListener('click', () => {
                    this.searchBar.classList.toggle('hidden');
                });
            }

            // 2. Search Input (Enter Key)
            if (this.inputSearch) {
                this.inputSearch.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.currentKeyword = e.target.value;
                        this.fetchLikes(1);
                    }
                });
            }

            // 3. Category Dropdown
            if (this.btnCategory) {
                this.btnCategory.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.dropdownCategory.classList.toggle('hidden');
                    this.dropdownSort?.classList.add('hidden');
                });
            }

            // 4. Sort Dropdown
            if (this.btnSort) {
                this.btnSort.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.dropdownSort.classList.toggle('hidden');
                    this.dropdownCategory?.classList.add('hidden');
                });
            }

            // 5. Region Modal Open
            if (this.btnRegion) {
                this.btnRegion.addEventListener('click', () => {
                    const modal = document.getElementById('region-modal');
                    if (modal) {
                        modal.classList.remove('hidden');
                        setTimeout(() => modal.classList.remove('opacity-0'), 10);
                    }
                });
            }

            // 6. Region Modal Close
            const regionCloseBtn = document.getElementById('region-modal-close');
            if (regionCloseBtn) {
                regionCloseBtn.addEventListener('click', () => {
                    const modal = document.getElementById('region-modal');
                    if (modal) {
                        modal.classList.add('opacity-0');
                        setTimeout(() => modal.classList.add('hidden'), 300);
                    }
                });
            }

            // 7. Region Selection (Button inside Modal)
            const regionModal = document.getElementById('region-modal');
            if (regionModal) {
                regionModal.addEventListener('click', (e) => {
                    // button or button child clicked
                    const btn = e.target.closest('.region-option-btn');
                    if (btn) {
                        const region = btn.dataset.region;
                        this.selectRegion(region);

                        // Close modal
                        regionModal.classList.add('opacity-0');
                        setTimeout(() => regionModal.classList.add('hidden'), 300);
                    }
                });
            }

            // 8. Global Click (Close Dropdowns)
            document.addEventListener('click', (e) => {
                if (this.dropdownCategory && !this.dropdownCategory.contains(e.target) && !this.btnCategory.contains(e.target)) {
                    this.dropdownCategory.classList.add('hidden');
                }
                if (this.dropdownSort && !this.dropdownSort.contains(e.target) && !this.btnSort.contains(e.target)) {
                    this.dropdownSort.classList.add('hidden');
                }
            });

            // 9. Global Helper Functions for HTML inline usage
            // (onclick="selectCategory...") needs to access MyPageManager instance methods.
            // Since MyPageManager is const, we can expose it or attach handlers to window.
            window.selectCategory = (cat) => {
                this.currentCategory = cat === '전체' ? null : cat;
                if (this.labelCategory) this.labelCategory.innerText = cat;
                this.dropdownCategory.classList.add('hidden');
                this.fetchLikes(1);
            };

            window.selectSort = (sort) => {
                this.currentSort = sort === 'reset' ? null : sort;
                const sortLabels = {
                    'latest': '최신순',
                    'popular': '인기순',
                    'deadline': '마감순',
                    'closed': '마감 정책',
                    'reset': '정렬'
                };
                if (this.labelSort) this.labelSort.innerText = sortLabels[sort] || '정렬';
                this.dropdownSort.classList.add('hidden');
                this.fetchLikes(1);
            };
        },

        selectRegion: function (region) {
            this.currentRegion = region === '전체' ? null : region;
            if (this.labelRegion) this.labelRegion.innerText = region;
            this.fetchLikes(1);
        },

        // [NEW] API Call with Filters
        fetchLikes: function (page) {
            const userEmail = localStorage.getItem('userEmail');
            if (!userEmail) {
                if (this.listContainer) this.listContainer.innerHTML = `<div class="empty-state"><p>로그인이 필요한 서비스입니다.</p></div>`;
                return;
            }

            this.currentPage = page;

            // Query Params
            const params = new URLSearchParams();
            params.append('user_email', userEmail);
            params.append('page', page);
            params.append('limit', this.itemsPerPage);

            if (this.currentKeyword) params.append('keyword', this.currentKeyword);
            if (this.currentCategory) params.append('category', this.currentCategory);
            if (this.currentRegion) params.append('region', this.currentRegion);
            if (this.currentSort) params.append('sort', this.currentSort);

            fetch(`/api/mypage/likes?${params.toString()}`)
                .then(res => res.json())
                .then(data => {
                    const policies = data.policies || [];
                    const totalCount = data.total_count || 0;

                    if (policies.length === 0) {
                        if (this.listContainer) this.listContainer.innerHTML = `<div class="empty-state w-full text-center py-10"><i class="fa-regular fa-folder-open text-gray-300 text-4xl mb-4"></i><p class="text-gray-500">조건에 맞는 찜한 정책이 없어요.</p></div>`;
                        if (this.paginationContainer) this.paginationContainer.innerHTML = "";
                    } else {
                        // Render List
                        if (this.listContainer) {
                            this.listContainer.innerHTML = policies.map(item => createCardHTML(item, false)).join('');
                        }

                        // Render Pagination
                        this.renderPagination(totalCount);

                        // Edit Mode Re-apply
                        if (this.isEditMode) {
                            this.addCheckboxesToCards();
                        }

                        // Animation
                        if (typeof gsap !== 'undefined') {
                            gsap.from("#mypage-list .policy-card", { y: 20, opacity: 0, duration: 0.4, stagger: 0.05, clearProps: "all" });
                        }
                    }
                })
                .catch(err => {
                    console.error("Link Load Error:", err);
                });
        },

        renderPagination: function (totalItems) {
            if (!this.paginationContainer) return;
            this.paginationContainer.innerHTML = "";

            const totalPages = Math.ceil(totalItems / this.itemsPerPage);
            if (totalPages <= 1) return;

            const baseClass = "w-10 h-10 rounded-full text-sm font-bold transition-all flex items-center justify-center border";
            const activeClass = `${baseClass} bg-[#777777] text-white border-[#777777] shadow-md transform scale-105`;
            const inactiveClass = `${baseClass} bg-white text-gray-500 border-gray-200 hover:bg-gray-100 hover:text-primary-teal`;
            const navClass = "px-4 h-10 rounded-full text-sm font-bold transition-all flex items-center justify-center border bg-white text-gray-500 border-gray-200 hover:bg-gray-100 hover:text-primary-teal";

            const createBtn = (text, onClick, className) => {
                const btn = document.createElement('button');
                btn.innerText = text;
                btn.className = className;
                btn.addEventListener('click', onClick);
                return btn;
            };

            // 이전
            if (this.currentPage > 1) {
                this.paginationContainer.appendChild(createBtn('이전', () => this.fetchLikes(this.currentPage - 1), navClass));
            }

            // 페이지 번호 (간단하게 구현: 1~Total)
            // * all.html 처럼 ... 처리 하려면 로직 추가 필요. 여기선 간단히 10페이지 이하는 다 보여주고, 많으면 앞뒤만 보여주는 식으로 개선 가능
            // * 여기서는 all.html과 유사한 "스마트 페이지네이션" 로직 적용

            const delta = 2;
            let startPage = Math.max(1, this.currentPage - delta);
            let endPage = Math.min(totalPages, this.currentPage + delta);

            if (startPage > 1) {
                this.paginationContainer.appendChild(createBtn(1, () => this.fetchLikes(1), this.currentPage === 1 ? activeClass : inactiveClass));
                if (startPage > 2) {
                    const span = document.createElement('span'); span.innerText = "..."; span.className = "px-2 text-gray-500";
                    this.paginationContainer.appendChild(span);
                }
            }

            for (let i = startPage; i <= endPage; i++) {
                this.paginationContainer.appendChild(createBtn(i, () => this.fetchLikes(i), i === this.currentPage ? activeClass : inactiveClass));
            }

            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    const span = document.createElement('span'); span.innerText = "..."; span.className = "px-2 text-gray-500";
                    this.paginationContainer.appendChild(span);
                }
                this.paginationContainer.appendChild(createBtn(totalPages, () => this.fetchLikes(totalPages), this.currentPage === totalPages ? activeClass : inactiveClass));
            }

            // 다음
            if (this.currentPage < totalPages) {
                this.paginationContainer.appendChild(createBtn('다음', () => this.fetchLikes(this.currentPage + 1), navClass));
            }
        },

        toggleEditMode: function () {
            this.isEditMode = !this.isEditMode;

            if (this.isEditMode) {
                this.btnManage.innerText = "완료";
                this.btnManage.classList.replace('text-gray-500', 'text-primary-orange');
                this.btnManage.classList.add('font-bold');
                this.btnManage.classList.remove('underline');

                this.editControls.classList.remove('hidden');
                this.editControls.classList.add('flex');
                this.addCheckboxesToCards();
            } else {
                this.btnManage.innerText = "편집";
                this.btnManage.classList.replace('text-primary-orange', 'text-gray-500');
                this.btnManage.classList.remove('font-bold');
                this.btnManage.classList.add('underline');

                this.editControls.classList.add('hidden');
                this.editControls.classList.remove('flex');
                if (this.checkAll) this.checkAll.checked = false;
                this.removeCheckboxesFromCards();
            }
        },

        addCheckboxesToCards: function () {
            if (!this.listContainer) return;
            const cards = this.listContainer.querySelectorAll('.policy-card');
            cards.forEach(card => {
                if (card.querySelector('.check-overlay')) return;
                const policyId = card.getAttribute('data-id');
                const overlay = document.createElement('div');
                overlay.className = 'check-overlay absolute inset-0 z-20 bg-black/5 cursor-pointer flex items-start justify-end p-4 animate-fade-in rounded-[20px]';
                overlay.onclick = (e) => {
                    e.stopPropagation();
                    if (e.target === overlay) {
                        const cb = overlay.querySelector('input');
                        cb.checked = !cb.checked;
                    }
                };
                overlay.innerHTML = `
                <div class="relative pointer-events-none">
                    <input type="checkbox" class="policy-check peer sr-only" value="${policyId}">
                    <div class="w-6 h-6 bg-white border-2 border-gray-300 rounded-full peer-checked:bg-primary-orange peer-checked:border-primary-orange transition-all shadow-sm flex items-center justify-center">
                        <i class="fa-solid fa-check text-white text-[10px] opacity-0 peer-checked:opacity-100 transition-opacity"></i>
                    </div>
                </div>`;
                card.classList.add('relative');
                card.appendChild(overlay);
            });
        },

        removeCheckboxesFromCards: function () {
            if (!this.listContainer) return;
            const overlays = this.listContainer.querySelectorAll('.check-overlay');
            overlays.forEach(el => el.remove());
        },

        deleteSelected: async function () {
            const checkedBoxes = document.querySelectorAll('.policy-check:checked');
            if (checkedBoxes.length === 0) {
                alert("삭제할 정책을 선택해주세요.");
                return;
            }

            if (!confirm(`선택한 ${checkedBoxes.length}개의 정책을 찜 목록에서 삭제하시겠습니까?`)) {
                return;
            }

            const ids = Array.from(checkedBoxes).map(cb => parseInt(cb.value));
            const userEmail = localStorage.getItem('userEmail');

            try {
                const res = await fetch('/api/mypage/likes/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_email: userEmail, policy_ids: ids })
                });

                const result = await res.json();
                if (res.ok) {
                    // 성공 시 현재 페이지 재로딩 (빈 페이지 되면 처리 로직은 fetchLikes 내부는 아니지만, 
                    // 보통 백엔드가 빈 리스트 주면 UI 처리됨. 
                    // 단, 현재 페이지가 비게 되면 page-1로 가는게 좋음. 간단히 현재 페이지 호출 후 데이터 없으면 page-1 호출 등의 로직 추가 가능)

                    // 체크박스 초기화
                    if (this.checkAll) this.checkAll.checked = false;

                    // 활동 지수 업데이트
                    if (typeof window.loadUserProfile === 'function') {
                        setTimeout(() => window.loadUserProfile(), 500);
                    }

                    // [NEW] 차트 업데이트 (삭제 반영)
                    if (typeof window.updateMyPageChart === 'function') {
                        setTimeout(() => window.updateMyPageChart(), 500);
                    }

                    // 재로딩
                    this.fetchLikes(this.currentPage);

                } else {
                    alert(`삭제 실패: ${result.detail || '오류가 발생했습니다.'}`);
                }
            } catch (e) {
                console.error(e);
                alert("서버 통신 중 오류가 발생했습니다.");
            }
        }
    };

    // Initialize
    MyPageManager.init();
});