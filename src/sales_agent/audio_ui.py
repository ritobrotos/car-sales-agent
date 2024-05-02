import streamlit as st
from audio_recorder_streamlit import audio_recorder
import google.generativeai as genai
import os
import pyttsx3

from src.sales_agent.gemini_agent import send_message

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.title("Car Sales Chatbot")
st.write('\n\n')
audio_bytes = audio_recorder()

# Initialize rag history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def save_audio_bytes_to_file(audio_bytes, file_path):
    print("Saving car_sales_agent to file")
    with open(file_path, "wb") as f:
        f.write(audio_bytes)


def audiorec_demo_app():
    print("audio_recorder_demo_app")
    st.title('streamlit car_sales_agent recorder')
    st.write('\n\n')

    audio_bytes = audio_recorder()
    if audio_bytes:
        st.audio(audio_bytes, format="car_sales_agent/wav")
        save_audio_bytes_to_file(audio_bytes, "car_sales_agent.wav")


# Ref: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Audio.ipynb
def transcribe_audio_file():
    your_file = genai.upload_file(path='car_sales_agent.wav')
    prompt = "Listen carefully to the following car_sales_agent file and transcribe the car_sales_agent."
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    print("Calling Gemini endpoint for transcribing car_sales_agent...")
    response = model.generate_content([prompt, your_file])
    print(response.text)
    return response.text


def transcribe_audio():
    if audio_bytes:
        st.audio(audio_bytes, format="car_sales_agent/wav")
        save_audio_bytes_to_file(audio_bytes, "car_sales_agent.wav")
        st.write('\n\n')
        transcribed_user_message = transcribe_audio_file()

        if transcribed_user_message is not None and len(transcribed_user_message) != 0:
            st.session_state.messages.append({"role": "user", "content": transcribed_user_message})
            with st.chat_message("user"):
                st.markdown(transcribed_user_message)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                response = send_message(transcribed_user_message)
                message_placeholder.markdown(response.text)
                print("AI Response: ", response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                text_to_audio(response.text)


# Ref: https://pypi.org/project/py3-tts/
def text_to_audio(agent_response: str):
    engine = pyttsx3.init()

    # Setting up voice
    # voices = engine.getProperty('voices')   # getting details of current voice
    # engine.setProperty('voice', voices[1].id)   # 1 for female, 0 for male

    # speak
    engine.say(agent_response)
    engine.runAndWait()
    # engine.stop()


if __name__ == '__main__':
    transcribe_audio()