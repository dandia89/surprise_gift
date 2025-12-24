# app.py
import base64
import time
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Password Chest", page_icon="🗝️", layout="centered")

SECRET_CODE = [2,7,1,9]
WIN_TEXT = "Congratulations! You win a vacation home to Spruce Grove."
WRONG_TEXT = "Wrong password."


def parse_numbers(raw: str):
    raw = (raw or "").strip().replace(",", " ")
    parts = [p for p in raw.split() if p]

    if len(parts) != len(SECRET_CODE):
        raise ValueError(f"Enter exactly {len(SECRET_CODE)} numbers.")

    nums = []
    for p in parts:
        if not p.lstrip("-").isdigit():
            raise ValueError("Only whole numbers allowed.")
        nums.append(int(p))

    return nums


def set_fullscreen_bg(mode: str):
    # mode: "normal" | "success" | "error"
    colors = {
        "normal": "#0b1220",   # dark
        "success": "#064e3b",  # green
        "error": "#b91c1c",    # red
    }
    bg = colors.get(mode, colors["normal"])

    st.markdown(
        f"""
        <style>
        .stApp {{ background: {bg}; }}

        .block-container {{
            padding-top: 1.2rem !important;
            max-width: 900px;
        }}

        header {{visibility: hidden; height: 0px;}}
        [data-testid="stToolbar"] {{display:none;}}
        footer {{visibility: hidden; height: 0px;}}
        </style>
        """,
        unsafe_allow_html=True
    )


def speak_js(text: str):
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace('"', '\\"')
    components.html(
        f"""
        <script>
        (function() {{
            try {{
                const msg = new SpeechSynthesisUtterance("{safe}");
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(msg);
            }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
    )


def autoplay_audio_bytes(file_bytes: bytes, mime: str):
    b64 = base64.b64encode(file_bytes).decode()
    components.html(
        f"""
        <audio autoplay>
            <source src="data:{mime};base64,{b64}" type="{mime}">
        </audio>
        """,
        height=0,
    )


def chest_animation():
    frames = ["🧰", "🧰 ✨", "🧰 ✨✨", "🎁 ✨✨", "🎁 ✨✨✨", "🏡 ✨✨✨"]
    box = st.empty()
    for f in frames:
        box.markdown(
            f"<div style='font-size:84px; text-align:center;'>{f}</div>",
            unsafe_allow_html=True
        )
        time.sleep(0.22)


if "screen" not in st.session_state:
    st.session_state.screen = "normal"

set_fullscreen_bg(st.session_state.screen)

st.title("🗝️ Password Chest")

wrong_audio = st.file_uploader(
    "Optional: upload your own 'wrong password' audio (wav/mp3/ogg)",
    type=["wav", "mp3", "ogg"]
)

with st.form("unlock_form"):
    code_str = st.text_input(
        f"Enter the code ({len(SECRET_CODE)} numbers):",
        placeholder="0000"
    )
    submitted = st.form_submit_button("Unlock")


if submitted:
    try:
        nums = parse_numbers(code_str)
    except ValueError as e:
        st.session_state.screen = "error"
        set_fullscreen_bg("error")

        st.markdown(
            "<div style='color:white; font-size:44px; font-weight:900; text-align:center; margin-top:40px;'>WRONG FORMAT</div>",
            unsafe_allow_html=True
        )
        speak_js(str(e))
        time.sleep(1.0)

        st.session_state.screen = "normal"
        st.rerun()

    if nums == SECRET_CODE:
        st.session_state.screen = "success"
        set_fullscreen_bg("success")

        st.markdown(
            "<div style='color:white; font-size:44px; font-weight:900; text-align:center; margin-top:20px;'>✅ UNLOCKED</div>",
            unsafe_allow_html=True
        )
        chest_animation()

        st.markdown(
            f"<div style='color:#d1fae5; font-size:22px; text-align:center; font-weight:700;'>{WIN_TEXT}</div>",
            unsafe_allow_html=True
        )
        speak_js(WIN_TEXT)

    else:
        st.session_state.screen = "error"
        set_fullscreen_bg("error")

        st.markdown(
            "<div style='color:white; font-size:48px; font-weight:900; text-align:center; margin-top:60px;'>WRONG PASSWORD</div>",
            unsafe_allow_html=True
        )

        if wrong_audio is not None:
            mime = wrong_audio.type or "audio/wav"
            autoplay_audio_bytes(wrong_audio.getvalue(), mime)
        else:
            speak_js(WRONG_TEXT)

        time.sleep(1.2)
        st.session_state.screen = "normal"
        st.rerun()
