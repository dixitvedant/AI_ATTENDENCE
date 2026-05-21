import streamlit as st
import base64
import uuid
import time

from src.services.ai_services import ask_ai


# =====================================
# Play Sound
# =====================================
def play_sound():

    try:

        with open(
            "assets/sounds/popup.mp3",
            "rb"
        ) as f:

            audio = f.read()

        b64 = base64.b64encode(
            audio
        ).decode()

        audio_id = uuid.uuid4()

        st.markdown(
            f"""
            <audio
            id="{audio_id}"
            autoplay
            style="display:none">
                <source
                src="data:audio/mp3;base64,{b64}"
                type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True
        )

    except:
        pass


# =====================================
# AI Dialog
# =====================================
@st.dialog(
    "🤖 SnapClass AI Assistant",
    width="large"
)
def ai_chat_dialog():

    # ---------------------------------
    # Fresh Chat Every Open
    # ---------------------------------
    if (
        "chat_history"
        not in st.session_state
    ):
        st.session_state.chat_history = []
    
    # Header
    col1, col2 = st.columns(
        [6,1]
    )

    with col1:

        st.caption(
            "Ask anything"
        )

    with col2:

        if st.button(
            "🗑",
            help="Clear Chat",
            use_container_width=True
        ):

            st.session_state.chat_history = []
            st.rerun()

    st.divider()
    play_sound()

    # ---------------------------------
    # Show Messages
    # ---------------------------------
    for role, msg in (
        st.session_state.chat_history
    ):

        with st.chat_message(
            role
        ):
            st.write(msg)

    # ---------------------------------
    # Chat Input
    # ---------------------------------
    question = st.chat_input(
        "Ask SnapClass AI..."
    )

    if question:

        # User
        with st.chat_message(
            "user"
        ):
            st.write(
                question
            )

        st.session_state.chat_history.append(
            (
                "user",
                question
            )
        )

        # AI
        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Thinking..."
            ):

                answer = ask_ai(
                    question
                )

            st.write(
                answer
            )

        st.session_state.chat_history.append(
            (
                "assistant",
                answer
            )
        )


# =====================================
# Floating Bubble
# =====================================
def ai_chat_widget():

    st.markdown("""
    <style>

    .st-key-open_ai button {

        position: fixed;
        right: 30px;
        bottom: 30px;

        width: 85px;
        height: 85px;

        border-radius:50%!important;

        background:
        linear-gradient(
            135deg,
            #5865F2,
            #7B61FF,
            #9B5CFF
        )!important;

        color:white!important;

        font-size:38px!important;

        border:none!important;

        box-shadow:
        0 10px 35px
        rgba(
            88,101,242,.45
        )!important;

        z-index:99999;

        transition:.25s;
    }

    .st-key-open_ai button:hover {

        transform:
        scale(1.08);

        box-shadow:
        0 14px 45px
        rgba(
            88,101,242,.6
        )!important;
    }

    </style>
    """, unsafe_allow_html=True)

    if st.button(
        "🤖",
        key="open_ai"
    ):

        # --------------------------
        # Fresh Chat On Every Open
        # --------------------------
        st.session_state[
            "chat_history"
        ] = []

        play_sound()

        time.sleep(
            0.15
        )

        ai_chat_dialog()