import streamlit as st
from supabase import Client, create_client
from typing import List, Dict
from hashlib import sha256

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = init_connection()

def get_user(username: str) -> List[Dict]:
    res = supabase.table('users').select('*').eq('username', username).execute().data
    return None if not res else res[0]

st.title('Example Streamlit Supabase Auth')
if 'username' not in st.session_state:
    if st.slider('Login <-> Signup', min_value=0, max_value=1) == 1:
        # do signup
        with st.form('signup'):
            st.subheader('Signup')
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')
            submitted = st.form_submit_button('Signup')

            if submitted:
                if not (username and password):
                    st.error('Username and password required.')
                else:
                    if get_user(username):
                        st.error('That username is taken. Maybe you meant to login?')
                    else:
                        supabase.table('users').insert({
                            'username': username,
                            'passhash': sha256(password.encode()).hexdigest()
                        }).execute()
                        st.session_state['username'] = str(username)
                        st.success('Account created!')
                        st.experimental_rerun()
    else:
        # do login
        with st.form('login'):
            st.subheader('Login')
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')
            submitted = st.form_submit_button('Login')

            if submitted:
                if not (username and password):
                    st.error('Username and password required.')
                else:
                    if (user := get_user(username)):
                        if user['passhash'] == sha256(password.encode()).hexdigest():
                            st.session_state['username'] = str(username)
                            st.success('Signed in!')
                            st.experimental_rerun()
                        else:
                            st.error('Incorrect password.')
                    else:
                        st.error('Username not found. Did you mean to signup?')
else:
    st.subheader('Welcome, ' + st.session_state['username'])

    if st.button('Logout'):
        del st.session_state['username']
        st.experimental_rerun()