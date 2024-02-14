from openai import OpenAI
import streamlit as st
import os
import chromadb
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm.auto import tqdm

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from youtube_io import get_transcription, chunk_with_overlap, extract_youtube_video_id, get_yt_metadata
from prompts import transcription_summary_template, prompt_to_dataquestion_template, vdb_query_prompt_template, question_answer_template

st.title("youtube-chat")

model = ChatOpenAI(model='gpt-3.5-turbo-1106', temperature=0)
chroma_client = chromadb.PersistentClient(path='/app/db')

# Initialize messages in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.collection = None if not st.session_state.get('collection', None) else st.session_state.collection

# Reset button to clear the conversation
if st.button("Reset Conversation"):
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_prompt_chat_history():
    chat_history = ""
    for message in st.session_state.messages: 
        if message["role"] == "assistant":
            chat_history += f"AI: {message['content']}\n"
        else:
            chat_history += f"User: {message['content']}\n"
    return chat_history


def process_video_flow(video_id):
    # TODO: format videoid, it should not contain any wrong chars!
    st.session_state.collection = chroma_client.get_or_create_collection(name=video_id.lower(), metadata=get_yt_metadata(video_id))
    if st.session_state.collection.count() > 0: 
        print(f"The collection for video ID {video_id} is empty.")
        return video_id

    transcription = get_transcription(video_id)
    transcription_chunks = chunk_with_overlap(transcription, 100, 50)

    joined_texts = ['\n'.join([i['text'] for i in chunk]) for chunk in transcription_chunks]

    def make_prediction(j_text):
        prompt = transcription_summary_template.format(transcription=j_text)
        return model.predict(prompt)

    chunk_summaries = []
    with ThreadPoolExecutor() as executor:
        future_to_jtext = {executor.submit(make_prediction, j_text): j_text for j_text in joined_texts}
        
        for future in tqdm(as_completed(future_to_jtext), total=len(joined_texts)):
            try:
                result = future.result()
                chunk_summaries.append(result)
            except Exception as exc:
                print(f'Generated an exception: {exc}')
    
    ids = [f'{i}' for i in range(len(chunk_summaries))]

    st.session_state.collection.add(
                documents=chunk_summaries,
                ids=ids
            )
        
    return video_id

def answer_main_question(collection, question, llm, n_results=10):
    chat_history = get_prompt_chat_history()
    query = llm.predict(prompt_to_dataquestion_template.format(prompt=question, chat_history=chat_history))
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    prompt = vdb_query_prompt_template.format(
        summaries=results,
        question=question,
        chat_history=chat_history
    )

    out = llm.predict(prompt)
    return out

def process_question(question):
    print(st.session_state.messages)
    if st.session_state.collection is not None:
        return answer_main_question(st.session_state.collection, question, model, 10)
    else:
        chat_history = get_prompt_chat_history()
        prompt = question_answer_template.format(question=question, chat_history=chat_history)

        print(prompt)

        return model.predict(prompt)

def user_flow(prompt):
    video_id = extract_youtube_video_id(prompt)
    if video_id:
        res = process_video_flow(video_id)
        res = process_question("Give me a summary of this video. Also give me the content and topics of it.")
    else:
        res = process_question(prompt)
    return res

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner('Please wait...'):
        stream = user_flow(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": stream})

    with st.chat_message("assistant"):
        st.markdown(stream)
