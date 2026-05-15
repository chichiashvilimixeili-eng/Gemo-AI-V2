import streamlit as st
from groq import Groq
import sqlite3
from datetime import datetime
import pytz

# 1. მონაცემთა ბაზის გამართვა (სახელისთვის)
def init_db():
    conn = sqlite3.connect('gemo_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_info (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

def get_info(key):
    try:
        conn = sqlite3.connect('gemo_data.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT value FROM user_info WHERE key=?", (key,))
        res = c.fetchone()
        conn.close()
        return res[0] if res else None
    except: return None

def save_info(key, value):
    conn = sqlite3.connect('gemo_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_info VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

init_db()

# 2. კონფიგურაცია
client = Groq(api_key="შენი_API_გასაღები")
st.set_page_config(page_title="Gemo AI Pro", page_icon="🤖")

# დროის გაგება (თბილისის დროით)
tbilisi_tz = pytz.timezone('Asia/Tbilisi')
current_time = datetime.now(tbilisi_tz).strftime("%H:%M:%S")
current_date = datetime.now(tbilisi_tz).strftime("%Y-%m-%d")

# 3. მეხსიერების შენარჩუნება (Session State)
if "messages" not in st.session_state:
    user_name = get_info('name') or "მეგობარო"
    st.session_state.messages = [
        {"role": "system", "content": f"შენ ხარ Gemo AI, მიხეილ ჩიჩიაშვილის მიერ შექმნილი. დღეს არის {current_date}, ახლა არის {current_time}. მომხმარებლის სახელია {user_name}. ისაუბრე მხოლოდ გამართული ქართულით, იყავი ზუსტი და მეგობრული. გრამატიკა დაიცავი მაქსიმალურად."}
    ]

st.title("🤖 Gemo AI Pro")

# ისტორიის ჩვენება
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 4. ჩატის ლოგიკა
if prompt := st.chat_input("ჰკითხე რამე Gemo-ს..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # სახელის ამოცნობა და შენახვა ბაზაში
    if "მქვია" in prompt:
        name = prompt.split("მქვია")[-1].strip().strip('.')
        save_info('name', name)

    try:
        # ვიყენებთ ყველაზე ძლიერ მოდელს გრამატიკისთვის
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.2, # დაბალი ტემპერატურა = ნაკლები გრამატიკული შეცდომა
            max_tokens=600
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        response_text = "ხარვეზია კავშირისას."

    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
