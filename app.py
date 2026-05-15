import streamlit as st
from groq import Groq
import sqlite3
from datetime import datetime
import pytz

# 1. ბაზის გამართვა
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

# 2. დრო და კონფიგურაცია
tbilisi_tz = pytz.timezone('Asia/Tbilisi')
now = datetime.now(tbilisi_tz)
current_time = now.strftime("%H:%M")
current_date = now.strftime("%d/%m/%Y")

client = Groq(api_key="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")
st.set_page_config(page_title="Gemo AI Pro", page_icon="🤖")

# 3. მეხსიერება და სისტემური ინსტრუქცია
if "messages" not in st.session_state:
    user_name = get_info('name') or "მეგობარო"
    st.session_state.messages = [
        {"role": "system", "content": f"შენ ხარ Gemo AI. დღეს არის {current_date}, ახლა არის {current_time}. მომხმარებლის სახელია {user_name}. ისაუბრე მხოლოდ გამართული ქართულით. დაიცავი გრამატიკა."}
    ]

st.title("🤖 Gemo AI Pro")

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 4. ჩატის ლოგიკა
if prompt := st.chat_input("ჰკითხე რამე Gemo-ს..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "მქვია" in prompt.lower():
        name = prompt.lower().split("მქვია")[-1].strip().capitalize()
        save_info('name', name)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # საუკეთესო მოდელი ქართულისთვის
            messages=st.session_state.messages,
            temperature=0.2, # დაბალი ტემპერატურა სიზუსტისთვის
            max_tokens=800
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        response_text = "ხარვეზია კავშირისას. გთხოვ, შეამოწმე API გასაღები."

    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
