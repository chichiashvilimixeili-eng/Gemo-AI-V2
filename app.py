import streamlit as st
from groq import Groq
import sqlite3

# მონაცემთა ბაზის ფუნქციები
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

# Groq კონფიგურაცია - აქ ჩასვი შენი API Key
client = Groq(api_key="შენი_გასაღები_აქ")

st.set_page_config(page_title="Gemo AI Pro", page_icon="🤖")
st.title("🤖 Gemo AI Pro")

# სახელი ბაზიდან
user_name = get_info('name')
if user_name:
    st.sidebar.write(f"მომხმარებელი: **{user_name}**")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "შენ ხარ Gemo AI, ჭკვიანი ასისტენტი. ისაუბრე მხოლოდ გამართული ქართულით. იყავი ზუსტი და ლოგიკური."}
    ]

# ისტორიის ჩვენება
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ჩატის ლოგიკა
if prompt := st.chat_input("ჰკითხე რამე Gemo-ს..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # სახელის დამახსოვრება
    if "მე მქვია" in prompt.lower() or "ჩემი სახელია" in prompt.lower():
        name = prompt.lower().replace("მე მქვია", "").replace("ჩემი სახელია", "").strip().capitalize()
        save_info('name', name)
        response_text = f"სასიამოვნოა, {name}! დავიმახსოვრე შენი სახელი."
    else:
        try:
            # ვიყენებთ უფრო ძლიერ მოდელს და დაბალ ტემპერატურას
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.1, # მაქსიმალური სიზუსტე
                max_tokens=500
            )
            response_text = completion.choices[0].message.content
        except Exception as e:
            response_text = "ხარვეზია კავშირისას. სცადე ცოტა ხანში."

    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
