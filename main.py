import os
import streamlit as st
from dotenv import load_dotenv
from rag_sql.sql_generator import generate_sql_query
from rag_sql.sql_executor import execute_sql_query
from rag_sql.nl_answer import generate_nl_answer
from rag_sql.memory import get_memory
import logging
import time
import re
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# Load environment variables
load_dotenv()

st.set_page_config(page_title="School DB QA Chat", page_icon="📚", layout="centered")
st.title("📚 School Database QA Chat")
st.write("Ask questions about your school database. Follow-up questions are supported!")

# Custom CSS for right-aligned user messages and status hover color
st.markdown(
    """
    <style>
    .user-message {
        background-color: #DCF8C6;
        color: #222;
        padding: 0.7em 1.2em;
        border-radius: 18px 18px 2px 18px;
        margin-left: 30%;
        margin-right: 0;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        text-align: right;
        max-width: 70%;
        float: right;
        clear: both;
        font-size: 1.1em;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .assistant-message {
        background-color: #fff;
        color: #222;
        padding: 0.7em 1.2em;
        border-radius: 18px 18px 18px 2px;
        margin-right: 30%;
        margin-left: 0;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        text-align: left;
        max-width: 70%;
        float: left;
        clear: both;
        font-size: 1.1em;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for chat history and memory
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'memory' not in st.session_state:
    st.session_state.memory = get_memory()

def is_small_talk(text):
    greetings = [
        r"^hi$", r"^hello$", r"^hey$", r"^how are you[\?\!\.]*$", r"^good morning$", r"^good evening$", r"^good afternoon$",
        r"^what's up\??$", r"^how's it going\??$", r"^yo$", r"^sup\??$", r"^thanks$", r"^thank you$", r"^bye$", r"^see you$"
    ]
    text = text.strip().lower()
    for pattern in greetings:
        if re.match(pattern, text):
            return True
    return False

FRIENDLY_SQL_ERROR_MESSAGES = [
    "Sorry, I couldn't process your request due to a technical issue. Please try rephrasing your question.",
    "Oops! Something went wrong while processing your question. Please try again.",
    "There was a problem executing your request. Please try a different question.",
    "Sorry, I ran into an error. Could you try asking in a different way?"
]

def small_talk_response(text):
    responses = {
        "hi": "Hello! How can I help you with your school database today?",
        "hello": "Hi there! What would you like to know about the school database?",
        "hey": "Hey! How can I assist you?",
        "how are you": "I'm just a bot, but I'm here to help you!",
        "good morning": "Good morning! Ready to answer your school database questions.",
        "good evening": "Good evening! How can I help?",
        "good afternoon": "Good afternoon! What would you like to know?",
        "what's up": "Not much, just ready to answer your questions!",
        "how's it going": "All good here! How can I help you?",
        "yo": "Yo! What's your question?",
        "sup": "Not much! How can I help?",
        "thanks": "You're welcome!",
        "thank you": "Happy to help!",
        "bye": "Goodbye! Have a great day!",
        "see you": "See you next time!"
    }
    text = text.strip().lower()
    for key in responses:
        if key in text:
            return responses[key]
    return "Hello! How can I help you with your school database today?"

def is_data_question(text):
    # Simple heuristic: look for keywords related to data
    data_keywords = [
        "student", "class", "section", "parent", "mark", "subject", "scholarship", "bank", "list", "show", "find", "who", "which", "how many", "average", "total", "count", "name", "details", "record", "table"
    ]
    text = text.strip().lower()
    for word in data_keywords:
        if word in text:
            return True
    return False

# Chat input box
user_input = st.chat_input("Type your question and press Enter...")

# Display chat history with custom alignment
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

# Handle new user input
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.markdown(f'<div class="user-message">{user_input}</div>', unsafe_allow_html=True)

    if is_small_talk(user_input) or not is_data_question(user_input):
        logging.info(f"[SMALL TALK] User: {user_input}")
        response = small_talk_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.markdown(f'<div class="assistant-message">{response}</div>', unsafe_allow_html=True)
    else:
        # Data-related question: run the full pipeline
        logging.info(f"[DATA REQUEST] User: {user_input}")
        # Step 1: Generate SQL from NL
        with st.status("🤔 Thinking... Generating SQL query..."):
            t0 = time.time()
            sql_query = generate_sql_query(user_input, st.session_state.memory)
            t1 = time.time()
            sql_gen_time = t1 - t0
            logging.info(f"[SQL GENERATION] Time taken: {sql_gen_time:.2f} seconds")
            logging.info(f"[SQL GENERATED] Query: {sql_query}")
        # Step 2: Execute SQL
        with st.status("🛠️ Executing SQL query..."):
            t2 = time.time()
            sql_result = execute_sql_query(sql_query)
            t3 = time.time()
            sql_exec_time = t3 - t2
            logging.info(f"[SQL EXECUTION] Time taken: {sql_exec_time:.2f} seconds")
            logging.info(f"[SQL OUTPUT] Result: {sql_result}")
        if sql_result is None:
            error_msg = random.choice(FRIENDLY_SQL_ERROR_MESSAGES)
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            st.markdown(f'<div class="assistant-message">{error_msg}</div>', unsafe_allow_html=True)
            logging.error("[USER ERROR] SQL execution failed, user notified.")
        else:
            with st.status("✍️ Generating natural language answer..."):
                t4 = time.time()
                nl_answer = generate_nl_answer(user_input, sql_query, sql_result, st.session_state.memory)
                t5 = time.time()
                nl_gen_time = t5 - t4
                logging.info(f"[NL ANSWER GENERATION] Time taken: {nl_gen_time:.2f} seconds")
                logging.info(f"[RESPONSE FLOW] User input -> SQL gen -> SQL exec -> NL answer -> Response sent")
            # Store a plain markdown version in chat history for persistence
            response_md = f"**SQL Query:**\n{sql_query}\n\n**Answer:**\n{nl_answer}"
            st.session_state.chat_history.append({"role": "assistant", "content": response_md})
            # Display with syntax highlighting for SQL
            st.markdown('<div class="assistant-message"><b>SQL Query:</b></div>', unsafe_allow_html=True)
            st.code(sql_query, language='sql')
            st.markdown(f'<div class="assistant-message"><b>Answer:</b><br>{nl_answer}</div>', unsafe_allow_html=True)