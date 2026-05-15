import streamlit as st
from groq import Groq
import sqlite3
from datetime import datetime
import pytz

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
# აქ ჩასვი შენი Groq API Key
client = Groq(api_key="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") 

st.set_page_config(page_title="Gemo AI Pro", page_icon="🤖")

# მომხმარებლის სახელის შემოწმება ბაზაში
user_name = get_info('name')

# --- ჩატის ისტორიის ინიციალიზაცია ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # სისტემური ინსტრუქცია, რომ ბოტმა აღარ "ურიოს"
    st.session_state.messages.append({
        "role": "system", 
        "content": "შენ ხარ Gemo AI, შექმნილი მიხეილ ჩიჩიაშვილის მიერ. უპასუხე მხოლოდ გამართული ქართულით. იყავი მეგობრული და ლოგიკური."
    })

# ინტერფეისი
st.title("🤖 Gemo AI Pro")
if user_name:
    st.write(f"მოგესალმები, **{user_name}**!")

# ჩატის ისტორიის ჩვენება
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# მთავარი ლოგიკა
if prompt := st.chat_input("ჰკითხე რამე Gemo-ს..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # სახელის დამახსოვრების ლოგიკა
    if "მე მქვია" in prompt.lower():
        name = prompt.lower().split("მე მქვია")[-1].strip().capitalize()
        save_info('name', name)
        response_text = f"სასიამოვნოა შენი გაცნობა, {name}! დავიმახსოვრე შენი სახელი."
    else:
        # Groq-თან კავშირი დაბალი ტემპერატურით
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                temperature=0.2, # დაბალი ტემპერატურა ლოგიკური პასუხებისთვის
                max_tokens=300
            )
            response_text = completion.choices[0].message.content
        except Exception as e:
            response_text = "უკაცრავად, კავშირის პრობლემაა. სცადე მოგვიანებით."

    with st.chat_message("assistant"):
        st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
