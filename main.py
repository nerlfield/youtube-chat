from openai import OpenAI
import streamlit as st
import os
import chromadb
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm.auto import tqdm

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from youtube_io import get_transcription, chunk_with_overlap, extract_youtube_video_id, get_yt_metadata
from prompts import transcription_summary_template, prompt_to_dataquestion_template, vdb_query_prompt_template

st.title("youtube-chat")

model = ChatOpenAI(model='gpt-3.5-turbo-1106', temperature=0)
chroma_client = chromadb.PersistentClient(path='/app/db')

# Initialize messages in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.collection_map = {item.metadata['title']:item.name for item in chroma_client.list_collections()}
st.session_state.selected_message = st.selectbox("Select a collection", st.session_state.collection_map.keys())
st.session_state.collection = chroma_client.get_collection(name=st.session_state.collection_map[st.session_state.selected_message])

# Reset button to clear the conversation
if st.button("Reset Conversation"):
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
def process_video_flow(video_id):
    transcription = get_transcription(video_id)
    transcription_chunks = chunk_with_overlap(transcription, 200, 50)

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

    # TODO: format videoid, it should not contain any wrong chars!
    st.session_state.collection = chroma_client.get_or_create_collection(name=video_id.lower(), metadata=get_yt_metadata(video_id))

    if st.session_state.collection.count() == 0:
        print(f"The collection for video ID {video_id} is empty.")
        ids = [f'{i}' for i in range(len(chunk_summaries))]

        st.session_state.collection.add(
                    documents=chunk_summaries,
                    ids=ids
                )
        
    st.session_state.collection_map = {item.metadata['title']:item.name for item in chroma_client.list_collections()}
    st.session_state.selected_message = st.session_state.collection.metadata['title'] #st.selectbox("Select a collection", st.session_state.collection_map.keys())
    st.session_state.collection = chroma_client.get_collection(name=st.session_state.collection_map[st.session_state.selected_message])
    
    return video_id

def answer_main_question(collection, question, llm, n_results=10):
    query = llm.predict( prompt_to_dataquestion_template.format(prompt=question) )
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    prompt = vdb_query_prompt_template.format(
        summaries=results,
        question=question,
    )

    out = llm.predict( prompt )
    return out

def process_question(question):
    return answer_main_question(st.session_state.collection, question, model, 10)

def user_flow(prompt):
    video_id = extract_youtube_video_id(prompt)
    if video_id:# and video_id not in st.session_state.collection_map.keys():
        prompt = process_video_flow(video_id)
    else:
        prompt = process_question(prompt)
    return prompt

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner('Please wait...'):
        stream = user_flow(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": stream})

    with st.chat_message("assistant"):
        st.markdown(stream)
