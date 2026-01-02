// ============================================================
// [0] GSAP & 플러그인 안전 등록
// ============================================================
if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
} else {
    console.warn("GSAP or ScrollTrigger not loaded.");
}

// ============================================================
// [1] 데이터 & 유틸리티
// ============================================================

// [수정 1] 가짜 데이터 생성 함수(generatePolicyData) 삭제함.
// HTML에서 window 객체에 넣어준 DB 데이터만 사용. 없으면 빈 배열([]).
const tinderData = window.tinderData || [];
const allSlideData = window.allSlideData || [];

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
    
    // 2. 장르 기반 이미지 자동 생성
    const displayImage = getCategoryImage(displayGenre);

    // 3. 모달에 넘겨줄 데이터 객체 생성 (이미지 경로 포함)
    const modalData = {
        title: displayTitle,
        genre: displayGenre,
        desc: displayDesc,
        date: displayDate,
        image: displayImage,
        link: displayLink
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
                        <span class="inline-block py-1 px-3 rounded-full bg-orange-50 text-primary-orange text-sm font-bold mb-3 border border-orange-100">${displayGenre}</span>
                        <h3 class="card-title text-2xl font-extrabold text-gray-900 leading-tight mb-3 line-clamp-2">${displayTitle}</h3>
                        <p class="card-desc text-base text-gray-500 font-medium line-clamp-3 leading-relaxed">${displayDesc}</p>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
                        <span class="card-date text-sm text-gray-400 font-bold"><i class="fa-regular fa-clock mr-1"></i> ${displayDate}</span>
                        
                        <button class="relative z-50 text-sm font-bold text-gray-900 underline decoration-gray-300 underline-offset-4 p-2 hover:text-primary-orange transition-colors" 
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
                 onclick="openCardModal(this)">
                
                <div class="card-image w-full h-[180px] flex items-end justify-center overflow-hidden bg-white">
                    <img src="${displayImage}" alt="${displayTitle}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110">
                </div>
                <div class="card-content p-6 flex flex-col gap-2">
                    <div class="flex justify-between items-center">
                        <span class="text-xs font-bold text-primary-orange bg-orange-50 px-2 py-1 rounded-md">${displayGenre}</span>
                    </div>
                    <h3 class="card-title text-xl font-extrabold text-[#222] line-clamp-2">${displayTitle}</h3>
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
            gsap.from(".tinder-card:nth-last-child(-n+5)", { y: 100, opacity: 0, duration: 0.8, stagger: 0.1, ease: "back.out(1.7)" });
        }
    }
    setupEvents() {
        this.cards.forEach((card) => { this.addListeners(card); });

        document.addEventListener('keydown', (e) => {
            const currentCards = document.querySelectorAll('.tinder-card');
            if (currentCards.length === 0) return;
            const topCard = currentCards[currentCards.length - 1];

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

            const userEmail = localStorage.getItem('userEmail');
            if (userEmail) {
                const actionType = direction === 'right' ? 'like' : 'pass';
                const policyId = card.getAttribute('data-id');

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
window.openCardModal = function (element) {
    const itemDataEncoded = element.getAttribute('data-json');
    const policyModalEl = document.getElementById('policy-modal');
    if (!policyModalEl) return;

    try {
        const item = JSON.parse(itemDataEncoded);
        
        // HTML 요소 매핑
        const els = { 
            title: document.getElementById('modal-title'), 
            desc: document.getElementById('modal-desc'), 
            img: document.getElementById('modal-img'), 
            cate: document.getElementById('modal-category'), 
            date: document.getElementById('modal-date'),
            linkBtn: document.getElementById('btn-modal-link') // HTML에 이 ID를 가진 버튼이 있어야 함
        };

        if (els.title) els.title.innerText = item.title;
        if (els.desc) els.desc.innerText = item.desc;
        if (els.img) els.img.src = item.image;
        if (els.cate) els.cate.innerText = item.genre;
        if (els.date) els.date.innerText = item.date;

        // [신규] 원문 보기 링크 연결
        if (els.linkBtn) {
            // 기존 이벤트 제거를 위해 cloneNode 사용하거나 단순히 onclick 덮어쓰기
            els.linkBtn.onclick = function() {
                if(item.link && item.link.trim() !== "") {
                    window.open(item.link, '_blank');
                } else {
                    alert("원문 링크가 없습니다.");
                }
            };
        }

        policyModalEl.classList.remove('hidden');
        setTimeout(() => { policyModalEl.classList.add('active'); }, 10);
    } catch (e) { console.error("Data Parsing Error:", e); }
};

// ============================================================
// [2] Controllers (Auth & Share)
// ============================================================

const AuthController = {
    currentRegion: null,
    pendingCallback: null,

    init: function () {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[id]');
            if (!target) return;

            if (target.id === 'btn-signup-submit') {
                e.preventDefault();
                this.handleSignup();
            }
            if (target.id === 'btn-login-submit') {
                e.preventDefault();
                this.handleLogin();
            }
            if (target.id === 'btn-modal-close-icon') {
                this.closeModal();
            }
            if (target.id === 'btn-modal-browse') {
                this.closeModal();
                if (this.pendingCallback) {
                    this.pendingCallback();
                }
            }
            if (['btn-promo-login', 'btn-goto-login'].includes(target.id)) this.switchView('login');
            if (['btn-promo-signup', 'btn-goto-signup'].includes(target.id)) this.switchView('signup');

            const trigger = e.target.closest('.js-login-trigger');
            if (trigger) {
                const mode = trigger.dataset.mode || 'login';
                this.open(mode);
            }
        });
    },

    open: function (mode = 'promo', regionName = null, count = 0, callback = null) {
        const modal = document.getElementById('auth-modal');
        const modalContent = document.getElementById('auth-modal-content');
        if (!modal) return;

        this.currentRegion = regionName;
        this.pendingCallback = callback;

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
        setTimeout(() => {
            modal.classList.remove('opacity-0');
            if (modalContent) {
                modalContent.classList.remove('scale-95');
                modalContent.classList.add('scale-100');
            }
        }, 10);

        this.switchView(mode);
    },

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
            document.querySelectorAll('.auth-input').forEach(input => input.value = '');
        }, 300);
    },

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

    handleSignup: async function () {
        const email = document.getElementById('signup-id').value;
        const password = document.getElementById('signup-pw').value;
        const name = document.getElementById('signup-name').value;

        if (!email || !password || !name) {
            alert("모든 정보를 입력해주세요.");
            return;
        }

        try {
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

const ShareController = {
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

window.socialLogin = function (provider) {
    if (!['google', 'naver'].includes(provider)) return;
    window.location.href = `/api/auth/${provider}/login`;
};

// ============================================================
// [3] 초기화 및 메인 로직
// ============================================================

async function checkLoginState() {
    const urlParams = new URLSearchParams(window.location.search);
    const socialLogin = urlParams.get('social_login');

    if (socialLogin === 'success') {
        const email = urlParams.get('email');
        const name = urlParams.get('name');

        if (email && name) {
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userName', name);
            window.history.replaceState({}, document.title, window.location.pathname);
            alert(`${name}님, 소셜 로그인 성공! 환영합니다.`);
            window.location.href = '/main.html';
        }
    }

    try {
        const res = await fetch('/api/auth/verify');
        if (!res.ok) {
            localStorage.clear();
            return;
        }
    } catch (e) {
        localStorage.clear();
        return;
    }

    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const userEmail = localStorage.getItem('userEmail');

    if (isLoggedIn && userEmail) {
        const pcNavList = document.getElementById('pc-nav-list');
        if (pcNavList) {
            pcNavList.innerHTML = `
                <li><a href="/main.html" class="flex items-center justify-center rounded-full px-4 py-2 text-[15px] font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 transition-all">Home</a></li>
                <li><a href="/all.html" class="flex items-center justify-center rounded-full px-4 py-2 text-[15px] font-bold text-white bg-primary-teal shadow-md hover:-translate-y-0.5 hover:shadow-lg hover:bg-[#3d8b94] transition-all">All Policies</a></li>
                <li><a href="/about.html" class="flex items-center justify-center rounded-full px-4 py-2 text-[15px] font-bold text-white bg-primary-beige shadow-md hover:-translate-y-0.5 hover:shadow-lg hover:bg-[#c49f5b] transition-all">About</a></li>
                <li><a href="/mypage.html" class="flex items-center justify-center rounded-full px-4 py-2 text-[15px] font-bold text-white bg-primary-orange shadow-md hover:-translate-y-0.5 hover:shadow-lg hover:bg-[#e06d2e] transition-all">My Page</a></li>
                <li><button onclick="handleLogout()" class="flex items-center justify-center rounded-full px-4 py-2 text-[15px] font-bold text-gray-500 border border-gray-300 hover:bg-gray-50 transition-all cursor-pointer">Logout</button></li>
            `;
        }
        const mobileProfile = document.getElementById('mobile-profile-section');
        if (mobileProfile) {
            mobileProfile.innerHTML = `
                <p class="text-gray-600 mb-2">반가워요 👋</p>
                <p class="text-xl font-bold text-gray-800 mb-4 truncate">${userEmail}님</p>
                <a href="/mypage.html" class="block w-full text-center rounded-xl bg-primary-orange py-3 text-white font-bold shadow-md transition-transform active:scale-95">My Page</a>
            `;
        }
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

        // Banner Text Cycle
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
    // [RENDERERS] Cards & MyPage (DB 데이터 기반)
    // --------------------------------------------------------

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

    // 마이페이지 (API 연동 버전)
    const mypageList = document.getElementById('mypage-list');
    if (mypageList) {
        const userEmail = localStorage.getItem('userEmail');

        if (!userEmail) {
            mypageList.innerHTML = `<div class="empty-state"><p>로그인이 필요한 서비스입니다.</p></div>`;
        } else {
            fetch(`/api/mypage/likes?user_email=${userEmail}`)
                .then(res => res.json())
                .then(data => {
                    if (data.length === 0) {
                        mypageList.innerHTML = `<div class="empty-state"><i class="fa-regular fa-folder-open"></i><p>아직 찜한 정책이 없어요.</p></div>`;
                    } else {
                        mypageList.innerHTML = data.map(item => createCardHTML(item, false)).join('');
                        if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
                            gsap.from("#mypage-list .policy-card", { y: 50, opacity: 0, duration: 0.6, stagger: 0.1, scrollTrigger: { trigger: "#mypage-list", start: "top 80%" } });
                        }
                    }
                })
                .catch(err => {
                    console.error("Link Load Error:", err);
                    mypageList.innerHTML = `<div class="empty-state"><p>데이터를 불러오는 중 오류가 발생했습니다.</p></div>`;
                });

            // 차트 부분은 동일
            const ctx = document.getElementById('myChart');
            if (ctx && typeof Chart !== 'undefined') {
                fetch(`/api/mypage/stats?user_email=${userEmail}`)
                    .then(res => res.json())
                    .then(stats => {
                        new Chart(ctx, {
                            type: 'radar',
                            data: {
                                labels: stats.labels,
                                datasets: [{
                                    label: '나의 관심도',
                                    data: stats.data,
                                    backgroundColor: 'rgba(244, 130, 69, 0.2)',
                                    borderColor: '#F48245',
                                    pointBackgroundColor: '#F48245',
                                    borderWidth: 2
                                }]
                            },
                            options: { responsive: true, maintainAspectRatio: false, scales: { r: { angleLines: { color: '#eee' }, grid: { color: '#eee' }, pointLabels: { font: { size: 12, family: 'Pretendard' }, color: '#666' }, ticks: { display: false, maxTicksLimit: 5 } } }, plugins: { legend: { display: false } } }
                        });
                    })
                    .catch(err => console.error("Stats Load Error:", err));
            }
        }
    }
});