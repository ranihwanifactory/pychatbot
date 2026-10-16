import streamlit as st
from google import genai
from google.genai import types

# 1. 웹 페이지 설정
st.set_page_config(page_title="나만의 무료 AI 챗봇", page_icon="💬")
st.title("💬 나만의 무료 AI 챗봇")
st.caption("Google Gemini API를 활용하여 비용이 전혀 들지 않는 무료 챗봇입니다.")

# 2. 사이드바에 무료 API 키 입력창 만들기
with st.sidebar:
    google_api_key = st.text_input("Google API Key", key="chatbot_api_key", type="password")
    "[Google AI Studio에서 무료 Key 발급받기](https://google.com)"

# 3. 대화 세션 상태 정의
if "chat_history" not in st.session_state:
    # 화면 표시용과 내부 대화 기록 통합 관리
    st.session_state["chat_history"] = []

# 4. 환영 인사 메시지 표시
if not st.session_state["chat_history"]:
    st.chat_message("assistant").write("안녕하세요! 비용 걱정 없는 무료 챗봇입니다. 무엇을 도와드릴까요?")

# 5. 기존 대화 기록을 화면에 그리기
for message in st.session_state["chat_history"]:
    st.chat_message(message["role"]).write(message["content"])

# 6. 사용자 채팅 입력 처리
if user_input := st.chat_input():
    if not google_api_key:
        st.info("시작하려면 왼쪽에 있는 사이드바에 Google API Key를 입력해주세요.")
        st.stop()

    # 구글 API 클라이언트 연결
    client = genai.Client(api_key=google_api_key)
    
    # 사용자가 입력한 메시지 화면 표시 및 저장
    st.chat_message("user").write(user_input)
    st.session_state["chat_history"].append({"role": "user", "content": user_input})

    # 7. Gemini 라이브러리의 정석적인 Chat 기능 활용
    # 이전까지의 대화 내역을 구글 공식 규격(types.Content) 리스트로 빌드
    history_objects = []
    for msg in st.session_state["chat_history"][:-1]:  # 마지막 직전 입력까지 기록 구축
        gemini_role = "model" if msg["role"] == "assistant" else "user"
        history_objects.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )
    
    # 세션 채팅 개시
    chat = client.chats.create(
        model="gemini-2.5-flash",
        history=history_objects
    )

    # 8. 답변 생성 및 실시간 스트리밍 출력
    with st.chat_message("assistant"):
        response_stream = chat.send_message_stream(user_input)
        
        # 청크를 받아 스트리밍 출력하는 제너레이터 함수
        def stream_chunks():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
                    
        response = st.write_stream(stream_chunks())
    
    # 챗봇의 최종 답변을 대화 기록에 저장
    st.session_state["chat_history"].append({"role": "assistant", "content": response})
