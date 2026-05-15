import streamlit as st
from groq import Groq
import sqlite3
from datetime import datetime
import pytz
import time

# --- მონაცემთა ბაზის გამართვა ---
def init_db():
    conn = sqlite3.connect('gemo_data.db')
    c = conn.cursor()
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

init_db()

# --- კონფიგურაცია ---
client = Groq(api_key="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")
st.set_page_config(page_title="Gemo AI Pro", page_icon="🤖")

# --- ლოკალური ლოგიკა ---
def get_local_answer(text):
    text = text.lower().strip()
    
    # სახელით მოკითხვა
    user_name = get_info('name')
    if "მე მქვია" in text:
        name = text.split("მქვია")[-1].strip().capitalize()
        save_info('name', name)
        return f"სასიამოვნოა შენი გაცნობა, **{name}**! დავიმახსოვრე შენი სახელი."
    
    if "რა მქვია" in text:
        return f"შენ გქვია **{user_name}**." if user_name else "ჯერ არ გითქვამს შენი სახელი."

    # დრო და ვალუტა
    if "დრო" in text:
        return f"🕒 თბილისში ახლა: **{datetime.now(pytz.timezone('Asia/Tbilisi')).strftime('%H:%M')}**"
    
    if "დოლარი" in text or "$" in text:
        nums = [float(s) for s in text.split() if s.replace('.','',1).isdigit()]
        if nums: return f"💵 {nums[0]}$ არის დაახლოებით **{round(nums[0]*2.70, 2)} ₾**."

    return None

# --- ინტერფეისი ---
with st.sidebar:
    st.title("🧒 Gemo AI Pro")
    name_display = get_info('name') or "მეგობარო"
    st.write(f"მოგესალმები, **{name_display}**!")
    if st.button("🗑️ მეხსიერების წაშლა"):
        st.session_state.messages = []
        st.rerun()

# ხმის ფუნქცია
st.markdown("<script>function speakText(t){window.speechSynthesis.cancel();const m=new SpeechSynthesisUtterance(t);m.lang='ka-GE';window.speechSynthesis.speak(m);}</script>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": f"შენ ხარ Gemo AI. მომხმარებელს ჰქვია {name_display}."}]

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("ჰკითხე Gemo-ს..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        local_res = get_local_answer(prompt)
        if local_res:
            full_res = local_res
            st.write(full_res)
        else:
            comp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=st.session_state.messages)
            full_res = comp.choices[0].message.content
            st.write(full_res)
        
        # ხმის გაშვება
        clean_v = full_res.replace("#", "").replace("*", "").replace("\n", " ")
        st.components.v1.html(f"<script>speakText('{clean_v}');</script>", height=0)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
