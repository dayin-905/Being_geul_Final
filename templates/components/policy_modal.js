/* 정책 모달 제어 함수 
   - 기존의 openModal 대신 openCardModal로 이름 통일
   - 인자로 HTML 요소(element)를 직접 받음
*/
function openCardModal(element) {
    const modal = document.getElementById('policy-modal');
    if (!modal) return console.error("모달 요소를 찾을 수 없습니다: #policy-modal");

    // 1. 데이터 파싱 (HTML 태그의 data-json 속성에서 가져옴)
    const jsonStr = element.getAttribute('data-json');
    if (!jsonStr) return console.error("데이터(data-json)가 없습니다.");

    try {
        const data = JSON.parse(jsonStr);

        // 2. DOM 요소 매핑
        const els = {
            title: document.getElementById('modal-title'),
            desc: document.getElementById('modal-desc'),
            img: document.getElementById('modal-img'),
            cate: document.getElementById('modal-category'),
            date: document.getElementById('modal-date'),
            heartBtn: document.getElementById('modal-heart-btn') // 하트 버튼 추가
        };

        // 3. 데이터 주입 (DB 필드명과 일치하는지 꼭 확인하세요!)
        // 예: data.img 인지 data.image 인지 확인 필요
        if (els.title) els.title.innerText = data.title || '';
        if (els.desc) els.desc.innerText = data.desc || '';
        if (els.cate) els.cate.innerText = data.category ? `#${data.category}` : '';
        if (els.date) els.date.innerText = data.endDate ? `마감일: ${data.endDate}` : '상시 모집';

        // 이미지 처리 (이미지가 없으면 기본 이미지)
        if (els.img) {
            els.img.src = data.img || data.image || '/static/images/card_images/default.png';
        }

        // 4. 모달 보여주기 (애니메이션 처리)
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // 배경 스크롤 막기

        setTimeout(() => {
            modal.classList.add('active');
        }, 10);

    } catch (e) {
        console.error("JSON 파싱 에러:", e);
    }
}

/* 모달 닫기 및 초기화 (이 코드는 기존에 없다면 추가하세요) */
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById('policy-modal');
    const closeBtn = document.getElementById('modal-close-btn');

    // 닫기 기능 공통 함수
    const closeModal = () => {
        if (!modal) return;
        modal.classList.remove('active');
        setTimeout(() => {
            modal.classList.add('hidden');
            document.body.style.overflow = ''; // 스크롤 복원
        }, 300); // CSS transition 시간과 맞춤
    };

    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    // 배경 클릭 시 닫기
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    }
});