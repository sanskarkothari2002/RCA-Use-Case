import os
import argparse
import json
import truststore
from PIL import Image
truststore.inject_into_ssl()

import httpx
import streamlit as st

def parse_args():
    parser = argparse.ArgumentParser(description="Simple CLI chatbot")
    parser.add_argument(
        "--model-api", help="Model API URL", default=os.environ.get("MODEL_API")
    )
    parser.add_argument(
        "--model-id", help="Model ID", default=os.environ.get("MODEL_ID")
    )
    parser.add_argument(
        "--token", help="Access token", default=os.environ.get("ACCESS_TOKEN")
    )
    return parser.parse_args()


def stream_chat_response(url, headers, data):
    with httpx.stream("POST", url, headers=headers, json=data, timeout=30) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield line


def main():
    st.set_page_config(page_title="Root Cause Analysis Miner", page_icon="🤖")
    image_path = "/Users/sanskar/Desktop/Images/Miner_info.png"

    col1, col2 = st.columns([5, 3])

    with col1:
        st.markdown("## Root Cause Analysis Miner")

    with col2:
        st.markdown("<div style='margin-top: 0px;'>", unsafe_allow_html=True)
        st.image(image_path, width=65)

    st.write("Type your message and press Enter. Responses will stream in real time.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "file_content" not in st.session_state:
        st.session_state["file_content"] = ""
        st.session_state["file_uploaded"] = False

    
    uploaded_file = st.file_uploader("Upload a log file (optional)", type=["txt", "log"])
    if uploaded_file and not st.session_state["messages"]:
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")
        st.session_state["file_uploaded"] = True
        st.session_state["file_content"] = file_content
        st.text_area("File Content", file_content, height=200)
    elif st.session_state["file_uploaded"]:
        st.text_area("File Content", st.session_state["file_content"], height=200, disabled=True)

    model_api = st.secrets["MODEL_API"] if "MODEL_API" in st.secrets else os.environ.get("MODEL_API")
    model_id = st.secrets["MODEL_ID"] if "MODEL_ID" in st.secrets else os.environ.get("MODEL_ID")
    token = st.secrets["ACCESS_TOKEN"] if "ACCESS_TOKEN" in st.secrets else os.environ.get("ACCESS_TOKEN")

    if not all([model_api, model_id, token]):
        st.error("MODEL_API, MODEL_ID, and ACCESS_TOKEN must be set as environment variables or in Streamlit secrets.")
        st.stop()

    url = f"{model_api.rstrip('/')}" + "/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    user_input = st.chat_input("Ask a question about the log file...")
    if user_input:
        st.chat_message("user").write(user_input)

        system_prompt = (
            "You are a helpful assistant. The user has uploaded the following log file:\n\n"
            + st.session_state["file_content"]
            + "\n\nAnswer the user's question based on this file."
        )

        current_messages = [
            {"role": "system", "content": system_prompt},
        ] + st.session_state["messages"] + [
            {"role": "user", "content": user_input}
        ]

        data = {
            "model": model_id,
            "messages": current_messages,
            "temperature": 0.7,
            "stream": True,
        }

        assistant_placeholder = st.chat_message("assistant").empty()
        full_response = ""

        try:
            for chunk in stream_chat_response(url, headers, data):
                if chunk.startswith("data: "):
                    chunk = chunk[6:]
                if chunk.strip() == "[DONE]":
                    break
                try:
                    delta = json.loads(chunk)
                    content = delta["choices"][0]["delta"].get("content", "")
                    full_response += content
                    assistant_placeholder.write(full_response)
                except Exception:
                    continue

            st.session_state["messages"].append({"role": "user", "content": user_input})
            st.session_state["messages"].append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()