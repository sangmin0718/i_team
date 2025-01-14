import easyocr
import sqlite3
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from difflib import unified_diff, SequenceMatcher

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (필요한 경우 특정 도메인만 허용 권장)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """HTML 페이지 반환"""
    return templates.TemplateResponse("index.html", {"request": request})

# 데이터베이스 초기화
def initialize_database():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect("extracted_texts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_texts (
            image_name TEXT PRIMARY KEY,
            extracted_text TEXT
        )
    """)
    conn.commit()
    return conn

def get_database_texts(conn):
    """데이터베이스에서 저장된 텍스트 가져오기"""
    cursor = conn.cursor()
    cursor.execute("SELECT image_name, extracted_text FROM extracted_texts")
    return cursor.fetchall()

def compare_first_five_sentences(db_text, input_text, threshold=0.8):
    """첫 5문장 비교 (유사도 기반)"""
    db_sentences = [line.strip() for line in db_text.split("\n")[:5] if line.strip()]
    input_sentences = [line.strip() for line in input_text.split("\n")[:5] if line.strip()]
    db_combined = " ".join(db_sentences)
    input_combined = " ".join(input_sentences)
    similarity = SequenceMatcher(None, db_combined, input_combined).ratio()
    return similarity >= threshold

def compare_full_text(db_text, input_text):
    """전체 텍스트 비교 (차이점 찾기)"""
    db_lines = db_text.splitlines()
    input_lines = input_text.splitlines()
    return list(unified_diff(db_lines, input_lines, lineterm=""))

def extract_text_from_image(image_data):
    """이미지에서 텍스트 추출"""
    reader = easyocr.Reader(['ko', 'en'])  # 한글 및 영어 지원
    results = reader.readtext(image_data)
    return "\n".join([text for _, text, _ in results])

@app.post("/compare")
async def compare_with_database(image: UploadFile = File(...)):
    """사용자 이미지와 데이터베이스 비교"""
    conn = initialize_database()
    rows = get_database_texts(conn)

    if not rows:
        return JSONResponse(content={"message": "데이터베이스에 저장된 텍스트가 없습니다."}, status_code=400)

    try:
        image_data = await image.read()
        input_text = extract_text_from_image(image_data)
    except Exception as e:
        return JSONResponse(content={"message": f"텍스트 추출 중 오류 발생: {str(e)}"}, status_code=500)

    results = []
    differences_found = False

    for image_name, db_text in rows:
        if compare_first_five_sentences(db_text, input_text):
            diff = compare_full_text(db_text, input_text)
            if diff:
                differences_found = True
                results.append({"image_name": image_name, "differences": diff})
            else:
                results.append({"image_name": image_name, "message": "텍스트가 완전히 동일합니다."})
        else:
            results.append({"image_name": image_name, "message": "첫 5문장이 다릅니다."})

    conn.close()

    if differences_found:
        return JSONResponse(content={"message": "비교 완료", "results": results})
    return JSONResponse(content={"message": "모든 텍스트에서 유의미한 차이점을 찾을 수 없습니다."})
