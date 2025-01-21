from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from pathlib import Path

app = FastAPI()

# uvicorn main:app --reload

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프로젝트 디렉토리 기준 경로 설정
BASE_DIR = Path(__file__).resolve().parent
characters = {
    "ari": BASE_DIR / "voice/wab/ari.wav",  # 아리
    "jinx": BASE_DIR / "voice/wab/jinx.wav",  # 징크스
    "lux": BASE_DIR / "voice/wab/lux.wav",  # 럭스
    "naru": BASE_DIR / "voice/wab/naru.wav",  # 나르
    "timo": BASE_DIR / "voice/wab/timo.wav",  # 티모
    "ruru": BASE_DIR / "voice/wab/ruru.wav",  # 룰루
}

# 피드백 생성 함수
def provide_feedback(distance):
    feedback = ""
    if distance < 50:  # DTW 거리 기준 값 설정
        feedback += "성대모사가 매우 잘되었습니다! "
    elif distance < 100:
        feedback += "성대모사가 꽤 잘 되었으나 약간 더 개선이 필요합니다. "
    else:
        feedback += "성대모사에 많은 개선이 필요합니다. "

    return feedback

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...), character: str = Query(...)):
    try:
        # 사용자 음성 파일 저장 경로
        user_audio_path = BASE_DIR / "user_audio.wav"
        with open(user_audio_path, "wb") as buffer:
            buffer.write(await file.read())

        # 캐릭터 음성 파일 경로 확인
        target_audio_path = characters.get(character)
        if not target_audio_path or not target_audio_path.exists():
            return JSONResponse(
                status_code=404,
                content={"message": f"Character audio not found: {character}"},
            )

        # 음성 파일 로드 및 MFCC 추출
        target_audio, target_sr = librosa.load(target_audio_path, sr=None)
        user_audio, user_sr = librosa.load(user_audio_path, sr=None)

        target_mfcc = librosa.feature.mfcc(y=target_audio, sr=target_sr, n_mfcc=13)
        user_mfcc = librosa.feature.mfcc(y=user_audio, sr=user_sr, n_mfcc=13)

        # DTW 거리 계산 (fastdtw)
        distance, path = fastdtw(target_mfcc.T, user_mfcc.T, dist=euclidean)
        feedback = provide_feedback(distance)

        return JSONResponse(content={"feedback": feedback, "distance": distance})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": f"Server error: {e}"}
        )

@app.get("/")
def read_root():
    return {"message": "FastAPI 서버가 실행 중입니다."}
