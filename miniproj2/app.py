from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from transformers import AutoTokenizer, AutoModel
import torch

app = Flask(__name__)
CORS(app)

# 모델 초기화
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained("Alibaba-NLP/gte-multilingual-base", trust_remote_code=True)
model = AutoModel.from_pretrained("Alibaba-NLP/gte-multilingual-base", trust_remote_code=True).to(device)

# 크롤링 함수
def crawl_news_article(url):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.headless = True

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    # 제목 추출a
    title_tag = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//meta[@property="og:title"]'))
    )
    title = title_tag.get_attribute("content") if title_tag else "제목 없음"

    # 본문 추출
    content_elements = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, '//p'))
    )
    content = "\n".join([elem.text for elem in content_elements])
    driver.quit()
    return title.strip(), content.strip()

# 유사도 계산 함수
def calculate_similarity(title, content):
    inputs = tokenizer([title, content], return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

    similarity = torch.nn.functional.cosine_similarity(
        torch.tensor(embeddings[0]).unsqueeze(0),
        torch.tensor(embeddings[1]).unsqueeze(0)
    ).item()
    return similarity

@app.route('/')
def index():
    return render_template('index.html')  # HTML 페이지 렌더링

@app.route('/process-url', methods=['POST'])
def process_url():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL이 입력되지 않았습니다."}), 400

    try:
        title, content = crawl_news_article(url)
        similarity = calculate_similarity(title, content)
        result = "일치" if similarity >= 0.7 else "불일치"

        return jsonify({
            "data": {
                "title": title,
                "content": content,
                "similarity_score": similarity,
                "result": result
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
