document.getElementById('submitButton').addEventListener('click', async () => {
    const url = document.getElementById('url').value;

    if (!url) {
        document.getElementById('result').innerText = "URL을 입력해주세요.";
        return;
    }

    try {
        const response = await fetch('/process-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });

        if (!response.ok) {
            throw new Error(`HTTP 오류: ${response.status}`);
        }

        const data = await response.json();
        const resultDiv = document.getElementById('result');

        if (data.error) {
            resultDiv.innerText = `오류: ${data.error}`;
        } else {
            resultDiv.innerHTML = `
                <h2>${data.data.title}</h2>
                <p>${data.data.content.replace(/\n/g, '<br>')}</p>
                <p><strong>유사도 분석 결과: ${data.data.result} (${data.data.similarity_score.toFixed(2)})</strong></p>
            `;
        }
    } catch (error) {
        document.getElementById('result').innerText = `요청 중 오류가 발생했습니다: ${error.message}`;
    }
});
