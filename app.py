import streamlit as st
from groq import Groq
import sqlite3
from datetime import datetime
import pytz
import time

# --- მონაცემთა ბაზის (მეხსიერების) გამართვა ---
def init_db():
    conn = sqlite3.connect('gemo_data.db')
    c = conn.cursor()
    # ვქმნით ცხრილს მომხმარებლის ინფორმაციისთვის
    c.execute('''CREATE TABLE IF NOT EXISTS user_info (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

def get_info(key):
    conn = sqlite3.connect('gemo_data.db')
    c = conn.cursor()
    c.execute("SELECT value FROM user_info WHERE key=?", (key,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def save_info(key, value):
    conn = sqlite3.connect('gemo_data.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_info VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# ბაზის ინიციალიზაცია
init_db()

# --- კონფიგურაცია ---
client = Groq(api_key="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") # გამოიყენე შენი გასაღები
st.set_page_config(page_title="Gemo AI Pro", page_icon="🤖", layout="centered")

# --- ლოკალური ლოგიკის ფუნქცია ---
def get_local_answer(text):
    text = text.lower().strip()
    
    # 1. სახელით მოკითხვა და დამახსოვრება
    saved_name = get_info('name')
    if "მე მქვია" in text or "ჩემი სახელია" in text:
        new_name = text.replace("მე მქვია", "").replace("ჩემი სახელია", "").strip().capitalize()
        save_info('name', new_name)
        return f"სასიამოვნოა შენი გაცნობა, **{new_name}**! დავიმახსოვრე შენი სახელი. 😊"
    
    if "რა მქვია" in text:
        return f"შენ გქვია **{saved_name}**." if saved_name else "ჯერ არ მითქვამს შენი სახელი. მითხარი: 'მე მქვია [სახელი]'."

    # 2. დრო და თარიღი
    if any(word in text for word in ["დრო", "საათი"]):
        tbi_time = datetime.now(pytz.timezone('Asia/Tbilisi')).strftime("%H:%M")
        return f"🕒 ახლა თბილისში არის **{tbi_time}**."

    # 3. ვალუტის კურსის სიმულაცია
    if "დოლარი" in text or "$" in text:
        nums = [float(s) for s in text.split() if s.replace('.','',1).isdigit()]
        if nums: return f"💵 {nums[0]}$ დაახლოებით არის **{round(nums[0]*2.75, 2)} ₾**."

    return None

# --- ინტერფეისი ---
with st.sidebar:
    st.title("🧒 Gemo AI Pro")
    current_user = get_info('name') or "მეგობარო"
    st.write(f"მოგესალმები, **{current_user}**!")
    st.markdown("---")
    if st.button("🗑️ ჩატის გასუფთავება"):
        st.session_state.messages = []
        st.rerun()

# ხმის ფუნქცია (JS)
st.markdown("<script>function speakText(t){window.speechSynthesis.cancel();const m=new SpeechSynthesisUtterance(t);m.lang='ka-GE';window.speechSynthesis.speak(m);}</script>", unsafe_allow_html=True)

# ჩატის ისტორია
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": f"შენ ხარ Gemo AI. მომხმარებელს ჰქვია {current_user}."}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# მთავარი პროცესი
if prompt := st.chat_input("ჰკითხე რამე Gemo-ს..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        local_res = get_local_answer(prompt)
        
        if local_res:
            response_text = local_res
            st.markdown(response_text)
        else:
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=st.session_state.messages
                )
                response_text = completion.choices[0].message.content
                st.markdown(response_text)
            except:
                response_text = "კავშირის პრობლემაა."
                st.error(response_text)

        # ხმის გაშვება
        clean_voice = response_text.replace("#", "").replace("*", "").replace("\n", " ")
        st.components.v1.html(f"<script>speakText('{clean_voice}');</script>", height=0)
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})
