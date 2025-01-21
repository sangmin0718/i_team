import os
import streamlit as st
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import requests

# 타이틀
st.title("LOL 캐릭터 성대모사 😊")

# FastAPI 서버 URL
API_URL = "http://127.0.0.1:8000/upload_audio"

# 절대 경로를 얻는 함수
def get_absolute_path(relative_path):
    return os.path.abspath(relative_path)

# 캐릭터 데이터 (대사 및 오디오 추가)
characters = [
    {
        "name": "아리 (Ari)",
        "image": get_absolute_path("image/ari.image.webp"),
        "key": "ari",
        "quotes": [
            {"text": "난 음식 갖고 장난 안 쳐.", "audio": get_absolute_path("voice/Ari_1.wav")},
            {"text": "삶이 얼마나 아름다운 건지, 정말 오랜 시간이 지나서야 깨달았어.", "audio": get_absolute_path("voice/Ari_2.wav")},
            {"text": "오늘은 또 어떤 새로운 경험 앞에서 당당히 맞서 볼까?", "audio": get_absolute_path("voice/Ari_3.wav")},
            {"text": "가까이 오렴. 어딜 가려고?", "audio": get_absolute_path("voice/Ari_4.wav")},
            {"text": "제아무리 가슴 아픈 기억이라도, 아름다움을 품고 있는 법이야.", "audio": get_absolute_path("voice/Ari_5.wav")},
        ],
    },
    {
        "name": "룰루 (Lulu)",
        "image": get_absolute_path("image/ruru.image.jpg"),
        "key": "ruru",
        "quotes": [
            {"text": "커져라~! 거대하게! 크게, 크게!", "audio": get_absolute_path("voice/Lulu_1.wav")},
            {"text": "맞다, 보라 색 맛 났어!", "audio": get_absolute_path("voice/Lulu_2.wav")},
            {"text": "웃음(1)", "audio": get_absolute_path("voice/Lulu_3.wav")},
            {"text": "웃음(2)", "audio": get_absolute_path("voice/Lulu_4.wav")},
            {"text": "깽깽이 발로 갈까요?", "audio": get_absolute_path("voice/Lulu_5.wav")},
        ],
    },
    {
        "name": "럭스 (Lux)",
        "image": get_absolute_path("image/lux.image.jpg"),
         "key": "lux",
        "quotes": [
            {"text": "데마시아의 빛이여!", "audio": get_absolute_path("voice/Lux_1.wav")},
            {"text": "어디, 지팡이 좀 휘둘러 볼까요?", "audio": get_absolute_path("voice/Lux_2.wav")},
            {"text": "제가 끝장 내 드리죠.", "audio": get_absolute_path("voice/Lux_3.wav")},
            {"text": "그림자를 걷어내겠어요.", "audio": get_absolute_path("voice/Lux_4.wav")},
            {"text": "모두 함께, 데마시아를 위해!", "audio": get_absolute_path("voice/Lux_5.wav")},
        ],
    },
    {
        "name": "징크스 (Jinx)",
        "image": get_absolute_path("image/jinx.image.jpg"),
        "key": "jinx",
        "quotes": [
            {"text": "뭐 할 차례였더라? 아, 깽판 칠 차례였지!", "audio": get_absolute_path("voice/Jinx_1.wav")},
            {"text": "가만히 있어 봐. 생각 좀 해... 보긴 뭘 해?", "audio": get_absolute_path("voice/Jinx_2.wav")},
            {"text": "그래, 내가 징크스다. 왜, 기분 나빠?", "audio": get_absolute_path("voice/Jinx_3.wav")},
            {"text": "뭐라구? 안 들려~ 듣고 싶지도 않고.", "audio": get_absolute_path("voice/Jinx_4.wav")},
            {"text": "미쳤다고? 내가? 어머~ 아직 누굴 안 만나 보셨네.", "audio": get_absolute_path("voice/Jinx_5.wav")},
        ],
    },
    {
        "name": "나르 (Gnar)",
        "image": get_absolute_path("image/naru.image.jpg"),
        "key": "naru",
        "quotes": [
            {"text": "나르 외계어(1)", "audio": get_absolute_path("voice/naru1.wav")},
            {"text": "나르 외계어(2)", "audio": get_absolute_path("voice/naru2.wav")},
            {"text": "메가나르", "audio": get_absolute_path("voice/naru3.wav")},
        ],
    },
    {
        "name": "티모 (Timo)",
        "image": get_absolute_path("image/timo.image.webp"),
        "key": "timo",
        "quotes": [
            {"text": "밴들시티 정찰대장, 티모 출동입니다!", "audio": get_absolute_path("voice/timo1.wav")},
            {"text": "정찰대의 규율을 깔보지 마시길!", "audio": get_absolute_path("voice/timo2.wav")},
            {"text": "헛둘셋넷 둘둘셋넷! 문제가 있는 곳엔 내가 있다구.", "audio": get_absolute_path("voice/timo3.wav")},
            {"text": "헉, 강아지다! 오구오구~ 간식 먹을래?", "audio": get_absolute_path("voice/timo4.wav")},
            {"text": "거기, 제 도움이 필요한 것 같은데요?", "audio": get_absolute_path("voice/timo5.wav")},
        ],
    },
]

# 선택된 캐릭터를 저장하는 상태 변수
if "selected_character" not in st.session_state:
    st.session_state["selected_character"] = None

# 캐릭터 선택 화면 (사이드바)
st.sidebar.write("### 모든 캐릭터")

for i, character in enumerate(characters):
    # 캐릭터 이미지와 이름 표시
    try:
        st.sidebar.image(character["image"], caption=character["name"], use_container_width=True)
    except Exception:
        st.sidebar.error(f"이미지 로드 실패: {character['name']}")

    # 버튼을 가운데 정렬
    col1, col2, col3 = st.sidebar.columns([1, 2, 1])
    with col2:
        if st.button(character["name"], key=f"sidebar_button_{i}"):
            st.session_state["selected_character"] = character

    st.sidebar.write("")  # 공백 추가

# 선택된 캐릭터 표시
selected_character = st.session_state["selected_character"]
if selected_character:
    st.subheader(f"선택된 캐릭터: {selected_character['name']}")

    # 선택된 캐릭터의 이미지 표시
    try:
        img = Image.open(selected_character["image"])
        st.image(img, caption=selected_character["name"], use_container_width=True)
    except Exception:
        st.error("캐릭터 이미지를 불러오는 데 실패했습니다.")

    # 대사와 오디오 재생 버튼
    st.write("**대사 및 오디오 재생:**")
    for i, quote in enumerate(selected_character["quotes"]):
        if st.button(f"오디오 재생 {i + 1}: {quote['text']}", key=f"audio_button_{selected_character['name']}_{i}"):
            try:
                st.audio(quote["audio"], format="audio/wav")
            except Exception:
                st.error("오디오 파일을 재생할 수 없습니다.")

    # 녹음 기능 추가
    st.header("녹음 기능")
    audio_bytes = audio_recorder(
        text="녹음 버튼을 눌러주세요!",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="6x",
    )

    if audio_bytes:
        # 녹음된 오디오 파일 저장
        file_name = f"{selected_character['key']}_녹음.wav"
        with open(file_name, "wb") as f:
            f.write(audio_bytes)
        st.success(f"녹음 파일이 '{file_name}'에 저장되었습니다!")

        st.audio(audio_bytes, format="audio/wav")
        st.download_button(
            label="녹음 파일 다운로드",
            data=audio_bytes,
            file_name=file_name,
            mime="audio/wav",
        )

        # "성대모사 비교해보기" 버튼
        if st.button("성대모사 비교해보기"):
            try:
                with open(file_name, "rb") as f:
                    files = {"file": f}
                    params = {"character": selected_character["key"]}
                    response = requests.post(API_URL, files=files, params=params)

                if response.status_code == 200:
                    feedback = response.json().get("feedback", "결과를 가져오지 못했습니다.")
                    st.success(f"비교 결과: {feedback}")
                else:
                    st.error(f"서버 오류: {response.status_code}")
            except Exception as e:
                st.error(f"FastAPI 서버와의 연결 실패: {e}")
else:
    st.subheader("")
    st.subheader("캐릭터를 선택해주세요.")




















