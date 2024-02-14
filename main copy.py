from openai import OpenAI
import streamlit as st
import re
import os

st.title("ChatGPT-like clone")

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Reset button to clear the conversation
if st.button("Reset Conversation"):
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def extract_youtube_video_id(url: str) -> str:
    regex_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)', # Standard format
        r'(?:https?://)?youtu\.be/([^?&]+)' # Shortened format
    ]
    
    for pattern in regex_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def interact_with_model(prompt):
    video_id = extract_youtube_video_id(prompt)
    if video_id:
        # st.session_state.messages.pop()
        prompt = f"Write to user that video id is {video_id}. Just say: Hey, your video id is {video_id}"
        # st.session_state.messages.append({"role": "user", "content": prompt})

    print(prompt)  # Print the user prompt to the console
    # stream = client.chat.completions.create(
    #     model=st.session_state["openai_model"],
    #     messages=[
    #         {"role": m["role"], "content": m["content"]}
    #         for m in st.session_state.messages
    #     ],
    #     stream=True,
    # )
    # return stream
    return prompt

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = interact_with_model(prompt)
        # response = st.write_stream(stream)
        # response = st.write(stream)
        st.session_state.messages.append({"role": "assistant", "content": stream})
        st.write(stream)
