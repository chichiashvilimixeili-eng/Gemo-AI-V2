import streamlit as st
from groq import Groq

# --- მონაცემები ---
client = Groq(api_key="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")

st.set_page_config(page_title="Gemo AI Pro", page_icon="🧒")

# --- ფუნქცია შენი პერსონალური პასუხებისთვის ---
def get_custom_response(text):
    responses = {
        "გამარჯობა": "სალამი! მე Gemo AI ვარ, მიხეილის შექმნილი.",
        "ვინ შეგქმნა": "მე მიხეილ ჭიჭიაშვილმა შემქმნა.",
        "რა გქვია": "მე მქვია Gemo AI.",
        "ნახვამდის": "ნახვამდის, იმედია მალე ისევ ვისაუბრებთ!",
        "როგორ ხარ": "კარგად ვარ, გმადლობ! შენ როგორ ხარ?",
        "მიხეილ ჭიჭიაშვილი ვინ არის": "მიხეილ ჭიჭიაშვილი ჩემი შემქმნელი და ძალიან ნიჭიერი დეველოპერია."
    }
    # ვამოწმებთ, არის თუ არა კითხვა ჩვენს სიაში
    return responses.get(text.lower().strip())

# --- ხმის ფუნქცია ---
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

# მეხსიერების ინიციალიზაცია
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "შენ ხარ Gemo AI, შექმნილი მიხეილ ჭიჭიაშვილის მიერ. იყავი მოკლე და ზუსტი."}
    ]

# ისტორიის ჩვენება
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ჩატი
if prompt := st.chat_input("ჰკითხე რამე Gemo-ს..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. ჯერ ვამოწმებთ ჩვენს პერსონალურ პასუხებს
        custom_answer = get_custom_response(prompt)
        
        if custom_answer:
            response = custom_answer
        else:
            # 2. თუ პასუხი სიაში არ არის, ვიძახებთ Groq AI-ს
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=st.session_state.messages,
                    temperature=0.1,
                    max_tokens=100
                )
                response = completion.choices[0].message.content
            except Exception:
                response = "უკაცრავად, ცოტა დავიბენი. კიდევ ერთხელ მკითხე."

        st.markdown(response)
        
        # ხმის გაშვება
        st.components.v1.html(f"<script>speakText('{response.replace(chr(39), '')}');</script>", height=0)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
