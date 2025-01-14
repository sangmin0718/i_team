const uploadForm = document.getElementById('uploadForm');
const imageInput = document.getElementById('imageInput');
const uploadedImage = document.getElementById('uploadedImage');
const inputWrapper = document.querySelector('.input-wrapper');
const resultContent = document.getElementById('resultContent');

// 이미지 미리보기 및 박스 크기 조정
imageInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const { width, height } = resizeImage(img.width, img.height);
                inputWrapper.style.width = `${width}px`;
                inputWrapper.style.height = `${height}px`;
                uploadedImage.style.display = 'block';
                uploadedImage.src = e.target.result;
                uploadedImage.style.width = `${width}px`;
                uploadedImage.style.height = `${height}px`;
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

// 이미지 크기 계산
function resizeImage(imgWidth, imgHeight) {
    const maxWidth = window.innerWidth * 0.9; // 최대 너비: 화면 너비의 90%
    const maxHeight = 600; // 최대 높이: 600px

    let newWidth = imgWidth;
    let newHeight = imgHeight;

    if (imgWidth > maxWidth) {
        const ratio = maxWidth / imgWidth;
        newWidth = maxWidth;
        newHeight *= ratio;
    }

    if (newHeight > maxHeight) {
        const ratio = maxHeight / newHeight;
        newHeight = maxHeight;
        newWidth *= ratio;
    }

    return { width: Math.floor(newWidth), height: Math.floor(newHeight) };
}

// 폼 제출 이벤트 처리
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // 기본 폼 제출 동작 방지

    const formData = new FormData(uploadForm);

    resultContent.innerHTML = '<li>처리 중입니다...</li>'; // 로딩 표시

    try {
        const response = await fetch('/compare', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            displayResults(result.results);
        } else {
            const error = await response.json();
            resultContent.innerHTML = `<li>오류: ${error.message}</li>`;
        }
    } catch (error) {
        resultContent.innerHTML = `<li>네트워크 오류가 발생했습니다.</li>`;
        console.error('Error:', error);
    }
});

// 결과 출력
function displayResults(results) {
    resultContent.innerHTML = ''; // 이전 결과 초기화
    results.forEach((item) => {
        const li = document.createElement('li');
        li.textContent = `이미지 이름: ${item.image_name}`;
        resultContent.appendChild(li);

        if (item.differences) {
            item.differences.forEach((diff) => {
                const diffLi = document.createElement('li');
                diffLi.textContent = diff;
                diffLi.style.marginLeft = '20px';
                resultContent.appendChild(diffLi);
            });
        } else if (item.message) {
            const messageLi = document.createElement('li');
            messageLi.textContent = item.message;
            resultContent.appendChild(messageLi);
        }
    });
}
