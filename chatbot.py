from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import db  # Import the database module

# Page configuration
st.set_page_config(
    page_title="Enhanced Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .chat-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .message-time {
        font-size: 0.8em;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize database
db.init_db()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_conversation_id" not in st.session_state:
    new_id = db.create_conversation("New Conversation")
    st.session_state.current_conversation_id = new_id

# Sidebar for conversation history and settings
with st.sidebar:
    st.header("Conversations")
    
    # Display past conversations
    conversations = db.get_conversations()
    for conv in conversations:
        if st.button(f"{conv[1]} - {conv[2]}", key=conv[0]):
            st.session_state.current_conversation_id = conv[0]
            messages = db.get_messages(conv[0])
            st.session_state.messages = [
                {"role": role, "content": content, "timestamp": timestamp}
                for role, content, timestamp in messages
            ]
    
    # New conversation button
    if st.button("New Conversation"):
        new_id = db.create_conversation("New Conversation")
        st.session_state.current_conversation_id = new_id
        st.session_state.messages = []
    
    # Model selection
    model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    st.session_state["openai_model"] = st.selectbox(
        "Select Model",
        model_options,
        index=0
    )
    
    # Temperature slider
    temperature = st.slider(
        "Response Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )

# Main chat interface
st.title("🤖 Enhanced Chatbot")

# Chat container
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(
            message["role"],
            avatar="👤" if message["role"] == "user" else "🤖"
        ):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(message["content"])
            with col2:
                st.markdown(
                    f'<p class="message-time">{message.get("timestamp", "")}</p>',
                    unsafe_allow_html=True
                )

# Chat input form
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([8, 1, 1])
    with cols[0]:
        prompt = st.text_input("Type your message...", key="user_input")
    with cols[1]:
        submit = st.form_submit_button("Send")
    with cols[2]:
        voice_input = st.form_submit_button("🎤")  # Placeholder for voice input

    # Handle message submission
    if submit and prompt:
        current_time = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": current_time
        })
        db.save_message(st.session_state.current_conversation_id, "user", prompt, current_time)
        
        # Update conversation title based on the first user message
        if len(st.session_state.messages) == 1:
            title = ' '.join(prompt.split()[:3])
            db.update_conversation_title(st.session_state.current_conversation_id, title)
        
        # Generate assistant response
        with st.chat_message("assistant", avatar="🤖"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} 
                         for m in st.session_state.messages],
                temperature=temperature,
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            db.save_message(st.session_state.current_conversation_id, "assistant", response, 
                          datetime.now().strftime("%H:%M"))