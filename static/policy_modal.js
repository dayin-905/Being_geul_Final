/**
 * static/policy_modal.js
 * 정책 모달의 데이터 주입 및 기능 제어 (최종 버전)
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. 모달 닫기 이벤트 (공통)
    const modal = document.getElementById('policy-modal');
    const closeBtn = document.getElementById('modal-close-x-btn'); // X 버튼 ID 확인 필요

    // 닫기 함수
    const closeModal = () => {
        if (!modal) return;
        modal.classList.remove('active');
        document.body.style.overflow = ''; // 스크롤 복구
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
    };

    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    // 배경 클릭 시 닫기
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    }
});

// 2. 카드 클릭 시 호출되는 함수 (HTML onclick="openCardModal(this)"와 연결)
function openCardModal(element) {
    const modal = document.getElementById('policy-modal');
    if (!modal) return;

    // 2-1. 데이터 가져오기 (HTML 태그의 data-json 속성 파싱)
    const jsonStr = element.getAttribute('data-json');
    if (!jsonStr) return console.error("데이터가 없습니다.");

    try {
        const data = JSON.parse(jsonStr);

        // 2-2. DOM 요소 매핑
        const els = {
            img: document.getElementById('modal-img'),
            category: document.getElementById('modal-category'),
            title: document.getElementById('modal-title'),
            desc: document.getElementById('modal-desc'),
            date: document.getElementById('modal-date'),
            linkBtn: document.getElementById('modal-link-btn'),   // [원문 보러 가기] 버튼
            shareBtn: document.getElementById('modal-share-btn'), // [공유하기] 버튼
            heartBtn: document.getElementById('modal-heart-btn')  // [찜하기] 버튼
        };

        // 2-3. 데이터 주입 (DB 칼럼명에 맞춰서 매핑)

        // [이미지]
        if (els.img) {
            // data.image가 없으면 DB의 img, 그것도 없으면 기본 이미지
            els.img.src = data.image || data.img || '/static/images/card_images/job_1.webp';
        }

        // [카테고리] DB 칼럼: genre (없으면 category)
        if (els.category) {
            els.category.innerText = data.genre || data.category || '기타';
        }

        // [제목] DB 칼럼: title
        if (els.title) {
            els.title.innerText = data.title || '제목 없음';
        }

        // [내용] DB 칼럼: summary (없으면 desc)
        if (els.desc) {
            els.desc.innerText = data.summary || data.desc || '상세 내용이 없습니다.';
        }

        // [마감일] DB 칼럼: period (없으면 date)
        if (els.date) {
            const periodText = data.period || data.date || '상시 모집';
            els.date.innerHTML = `<i class="fa-regular fa-calendar mr-1"></i> ${periodText}`;
        }

        // [핵심 1] 원문 보러 가기 (DB 칼럼: link)
        if (els.linkBtn) {
            if (data.link) {
                els.linkBtn.href = data.link; // href 속성에 URL 주입
                els.linkBtn.classList.remove('opacity-50', 'pointer-events-none'); // 활성화
                els.linkBtn.innerText = "원문 보러 가기"; // 텍스트 복구
            } else {
                els.linkBtn.href = "#";
                els.linkBtn.classList.add('opacity-50', 'pointer-events-none'); // 비활성화 스타일
                els.linkBtn.innerText = "링크 없음";
            }
        }

        // [핵심 2] 공유하기 버튼 (클립보드 복사)
        if (els.shareBtn) {
            // 기존 이벤트 리스너 중복 방지를 위해 onclick 속성으로 재할당
            els.shareBtn.onclick = () => {
                const shareUrl = data.link || window.location.href; // 링크가 있으면 그 링크, 없으면 현재 페이지 주소
                navigator.clipboard.writeText(shareUrl).then(() => {
                    alert('정책 링크가 복사되었습니다!');
                }).catch(err => {
                    console.error('복사 실패:', err);
                });
            };
        }

        // [핵심 3] 찜하기 버튼 (UI 토글)
        if (els.heartBtn) {
            // 버튼 초기화
            const icon = els.heartBtn.querySelector('i');
            icon.className = "fa-regular fa-heart text-xl";
            els.heartBtn.classList.remove('border-red-500', 'text-red-500');

            // [NEW] 서버에서 찜 상태 확인 (로그인 시에만)
            const userEmail = localStorage.getItem('userEmail');
            if (userEmail && data.id) {
                fetch(`/api/mypage/check?user_email=${userEmail}&policy_id=${data.id}`)
                    .then(res => res.json())
                    .then(res => {
                        if (res.liked) {
                            icon.className = "fa-solid fa-heart text-xl";
                            els.heartBtn.classList.add('border-red-500', 'text-red-500');
                        }
                    })
                    .catch(err => console.error("찜 상태 확인 실패:", err));
            }

            // 클릭 이벤트
            els.heartBtn.onclick = function () {
                // 토글 로직
                const isActive = icon.classList.contains('fa-solid');
                const userEmail = localStorage.getItem('userEmail');
                const policyId = data.id;

                if (!userEmail) {
                    alert('로그인이 필요한 기능입니다.');
                    // 선택적: 로그인 창 띄우기
                    // if (window.openAuthModal) window.openAuthModal('login');
                    return;
                }

                if (!isActive) {
                    // 찜하기 상태로 변경 (채워진 하트 + 빨간색)
                    icon.className = "fa-solid fa-heart text-xl";
                    this.classList.add('border-red-500', 'text-red-500');

                    // 백엔드 연동: Like
                    fetch('/api/mypage/action', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_email: userEmail,
                            policy_id: parseInt(policyId),
                            type: 'like'
                        })
                    }).then(res => res.json())
                        .then(res => {
                            console.log("찜하기 성공:", res);
                            // 네비게이션바 근처나 마이페이지 쪽으로 하트가 날아가는 애니메이션 등을 추가하면 좋음

                            // [NEW] 차트 실시간 업데이트
                            if (window.updateMyPageChart) window.updateMyPageChart();
                        })
                        .catch(err => console.error("찜하기 오류:", err));

                } else {
                    // 찜 취소 상태로 변경 (빈 하트 + 회색)
                    icon.className = "fa-regular fa-heart text-xl";
                    this.classList.remove('border-red-500', 'text-red-500');

                    // 백엔드 연동: Unlike
                    fetch('/api/mypage/action', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_email: userEmail,
                            policy_id: parseInt(policyId),
                            type: 'unlike'
                        })
                    }).then(res => res.json())
                        .then(res => {
                            console.log("찜하기 취소:", res);

                            // [NEW] 화면에서 즉시 제거 (마이페이지 등에서 보고 있을 때)
                            const cardsToRemove = document.querySelectorAll(`.policy-card[data-id='${policyId}']`);
                            cardsToRemove.forEach(card => {
                                // 카드가 삭제될 때 부드럽게 사라지게 하려면 애니메이션 추가 가능
                                card.style.transition = "all 0.3s ease";
                                card.style.opacity = "0";
                                card.style.transform = "scale(0.9)";
                                setTimeout(() => card.remove(), 300);
                            });

                            // [NEW] 리스트가 비었는지 확인 (마이페이지)
                            setTimeout(() => {
                                const mypageList = document.getElementById('mypage-list');
                                if (mypageList && mypageList.children.length === 0) {
                                    mypageList.innerHTML = `<div class="empty-state"><i class="fa-regular fa-folder-open"></i><p>아직 찜한 정책이 없어요.</p></div>`;
                                }
                            }, 310);

                            // [NEW] 차트 실시간 업데이트
                            if (window.updateMyPageChart) window.updateMyPageChart();
                        })
                        .catch(err => console.error("찜 취소 오류:", err));
                }
            };
        }

        // 2-4. 모달 보여주기
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // 배경 스크롤 막기

        // 애니메이션 효과
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);

    } catch (e) {
        console.error("JSON 파싱 에러:", e);
    }
}