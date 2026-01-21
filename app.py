import streamlit as st
from groq import Groq

# მონაცემები
client = Groq(api_key="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")

st.set_page_config(page_title="Gemo AI", page_icon="🧒")

# დიზაინი
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ხმის ფუნქცია
st.markdown("""
    <script>
    function speakText(text) {
        window.speechSynthesis.cancel();
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'ka-GE';
        msg.pitch = 1.1;
        window.speechSynthesis.speak(msg);
    }
    </script>
    """, unsafe_allow_html=True)

# სისტემური ინსტრუქცია (ტვინი)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "შენ ხარ Gemo AI. შენი შემქმნელია მიხეილ ჭიჭიაშვილი. უპასუხე მოკლედ და გამართული ქართულით."}
    ]

# ჩატი
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("ჰკითხე რამე Gemo-ს..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.messages,
            temperature=0.1,
            max_tokens=100
        )
        response = completion.choices[0].message.content
        st.markdown(response)
        st.components.v1.html(f"<script>speakText('{response.replace(chr(39), '')}');</script>", height=0)
        st.session_state.messages.append({"role": "assistant", "content": response})
