import secrets

import streamlit as st
from api_client import ApiError, ask
from settings import UI_PASSWORD

st.set_page_config(page_title="Agentic RAG Demo", page_icon="🤖")
st.title("Agentic RAG Demo")


def check_password() -> None:
    if st.session_state.get("authenticated"):
        return

    password = st.text_input("Demo password", type="password")
    if password:
        if UI_PASSWORD and secrets.compare_digest(password.encode(), UI_PASSWORD.encode()):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.stop()


def show_details(result: dict) -> None:
    if result["sources"]:
        st.caption("Sources: " + ", ".join(result["sources"]))
    with st.expander("How the agent decided"):
        st.write(f"Route: **{result['route']}**")
        st.write(f"Rewrites: **{result['rewrites']}**")
        if result["critic_reason"]:
            st.write(f"Critic: {result['critic_reason']}")


check_password()

if st.sidebar.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("details"):
            show_details(message["details"])

if question := st.chat_input("Ask about refunds, shipping or account security...", max_chars=500):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                result = ask(question)
        except ApiError as exc:
            st.error(str(exc))
        else:
            st.markdown(result["answer"])
            show_details(result)
            st.session_state.messages.append(
                {"role": "assistant", "content": result["answer"], "details": result}
            )