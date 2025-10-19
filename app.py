import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


SYSTEM_PROMPT = """
Anda adalah "ChefBot," seorang Asisten Kuliner AI yang merupakan chef berpengalaman.
Tugas Anda adalah:
1. Memberikan resep masakan berdasarkan bahan yang dimiliki pengguna.
2. Memberikan tips dan teknik memasak yang jelas.
3. Selalu tanyakan tentang preferensi diet atau alergi.
4. Gunakan bahasa yang suportif dan penuh semangat (misalnya, sapa pengguna dengan "Chef").
5. Prioritaskan masakan yang lezat dan mudah dibuat.
"""

st.set_page_config(page_title="ChefBot: Asisten Kuliner", page_icon="👨‍🍳")
st.title("ChefBot: Asisten Kuliner 🧑‍🍳")


def get_api_key_input():
    if "GOOGLE_API_KEY" not in st.session_state:
        st.session_state["GOOGLE_API_KEY"] = ""

    if st.session_state["GOOGLE_API_KEY"]:
        return

    st.warning("⚠️ Masukkan Google API Key Anda untuk memulai ChefBot!")

    col1, col2 = st.columns((80, 20))
    with col1:
        api_key = st.text_input("🔑 Google API Key", label_visibility="collapsed", type="password")

    with col2:
        is_submit_pressed = st.button("Submit")
        if is_submit_pressed and api_key:
            st.session_state["GOOGLE_API_KEY"] = api_key

    os.environ["GOOGLE_API_KEY"] = st.session_state["GOOGLE_API_KEY"]

    if not st.session_state["GOOGLE_API_KEY"]:
        st.stop()
    st.rerun()


def load_llm():
    if "llm" not in st.session_state:
        st.session_state["llm"] = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    return st.session_state["llm"]


def get_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [SystemMessage(content=SYSTEM_PROMPT)]
        
        st.session_state["chat_history"].append(AIMessage(
            content="Halo, Chef! Mau masak apa hari ini? Coba sebutkan bahan-bahan yang Anda punya!"
        ))
        
    return st.session_state["chat_history"]


def display_chat_message(message):
    if type(message) is HumanMessage:
        role = "user"
        avatar_icon = "🍽️"
    elif type(message) is AIMessage:
        role = "assistant"
        avatar_icon = "🧑‍🍳"
    elif type(message) is SystemMessage:
        return
    else:
        return

    with st.chat_message(role, avatar=avatar_icon):
        st.markdown(message.content)


def display_chat_history(chat_history):
    for chat in chat_history:
        display_chat_message(chat)


def user_query_to_llm(llm, chat_history):
    prompt = st.chat_input("Tulis bahan yang Anda punya atau masakan yang ingin dibuat...")
    if not prompt:
        return

    chat_history.append(HumanMessage(content=prompt))
    display_chat_message(chat_history[-1])

    with st.spinner("ChefBot sedang meracik resep..."):
        response = llm.invoke(chat_history)

    chat_history.append(response)
    display_chat_message(chat_history[-1])


def main():
    get_api_key_input()
    
    llm = load_llm()
    chat_history = get_chat_history()
    display_chat_history(chat_history)
    
    user_query_to_llm(llm, chat_history)


if __name__ == "__main__":
    main()