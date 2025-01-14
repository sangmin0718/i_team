import easyocr
import sqlite3

# SQLite 데이터베이스 연결 및 테이블 생성
def initialize_database():
    conn = sqlite3.connect("extracted_texts.db")  # 데이터베이스 파일 생성
    cursor = conn.cursor()
    # 테이블 생성 (이미지 ID, 번호, 추출된 텍스트 저장)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_number INTEGER NOT NULL,
            image_name TEXT NOT NULL,
            extracted_text TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

# 텍스트를 데이터베이스에 저장
def save_to_database(conn, image_number, image_name, text):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO extracted_texts (image_number, image_name, extracted_text) VALUES (?, ?, ?)",
                   (image_number, image_name, text))
    conn.commit()

# 이미지에서 텍스트 추출
def process_images(image_paths):
    reader = easyocr.Reader(['ko', 'en'])  # EasyOCR Reader 생성
    conn = initialize_database()  # 데이터베이스 초기화
    
    for idx, image_path in enumerate(image_paths, start=1):  # 이미지에 번호 부여 (1번부터 시작)
        print(f"Processing ({idx}): {image_path}")
        # 텍스트 추출
        results = reader.readtext(image_path)
        
        # 추출된 텍스트 결합 (한 이미지의 모든 텍스트를 하나의 문자열로 저장)
        extracted_text = "\n".join([text for _, text, _ in results])
        
        # 텍스트 출력
        print(f"추출된 텍스트 ({idx}번):")
        print(extracted_text)
        
        # 데이터베이스에 저장
        save_to_database(conn, idx, image_path, extracted_text)  # 이미지 번호와 함께 저장
    
    conn.close()

# 이미지 경로 리스트
image_paths = [
    "C:/Users/82102/Desktop/paper/paper1.jpg",
    "C:/Users/82102/Desktop/paper/paper2.jpg",
    "C:/Users/82102/Desktop/paper/paper3.jpg",
    "C:/Users/82102/Desktop/paper/paper4.jpg",
    "C:/Users/82102/Desktop/paper/paper5.jpg",
    "C:/Users/82102/Desktop/paper/paper6.jpg",
    "C:/Users/82102/Desktop/paper/paper7.jpg",
    "C:/Users/82102/Desktop/paper/paper8.jpg",
    "C:/Users/82102/Desktop/paper/paper9.jpg",
    "C:/Users/82102/Desktop/paper/paper10.jpg"
]

# 이미지 처리 및 텍스트 저장 실행
process_images(image_paths)
