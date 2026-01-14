import streamlit as st
from PIL import Image, ImageSequence
# import google.generativeai as genai # Unused in admin tool
import firebase_admin
from firebase_admin import credentials, db
import json
import time
from datetime import datetime
import os

# --- CONFIGURATION ---
# Helper to get secrets
def get_secret(key):
    if key in os.environ:
        return os.environ[key]
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    return None

import os # Ensure os is imported if it wasn't already at top level, but it is at line 9.

GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("⚠️ GENAI_API_KEY is missing! Please set it in .streamlit/secrets.toml or as an environment variable.")
    st.stop()
FIREBASE_CREDENTIALS_PATH = "firebase_credentials.json"
FIREBASE_DB_URL = "https://loga-portfolio-default-rtdb.firebaseio.com"

# --- INIT FIREBASE ---
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Portfolio Admin", page_icon="⚡")
st.title("⚡ Portfolio Admin (Local Assets Mode)")

# --- HELPER: GET LOCAL GIFS ---
def get_local_gifs():
    """Scans the 'static' folder for GIF files"""
    static_dir = "static"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        return []
    files = [f for f in os.listdir(static_dir) if f.lower().endswith('.gif')]
    return files

def get_gif_duration(filename):
    """Calculates total duration of local GIF in milliseconds"""
    try:
        path = os.path.join("static", filename)
        with Image.open(path) as img:
            duration = 0
            for frame in ImageSequence.Iterator(img):
                duration += frame.info.get('duration', 100)
            return duration
    except Exception as e:
        st.error(f"Error calculating duration for {filename}: {e}")
        return 5000 # Default fallback

# --- TABS ---
tab1, tab2 = st.tabs(["✨ Create / Edit Project", "🗑️ Manage Existing"])

# --- SESSION STATE INITIALIZATION ---
if 'edit_mode' not in st.session_state:
    st.session_state['edit_mode'] = False
    st.session_state['edit_id'] = None
    st.session_state['title'] = ""
    st.session_state['desc'] = ""
    st.session_state['stack'] = ""
    st.session_state['challenge'] = ""
    st.session_state['repo'] = ""
    st.session_state['live'] = ""
    st.session_state['selected_gif'] = ""

# --- TAB 1: CREATE / EDIT ---
with tab1:
    header_text = f"✏️ Editing: {st.session_state['edit_id']}" if st.session_state['edit_mode'] else "✨ Create New Project"
    st.subheader(header_text)

    # 1. DETAILS
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['title'] = st.text_input("Project Title", st.session_state['title'])
        st.session_state['desc'] = st.text_area("Description", st.session_state['desc'], height=150)
    
    with col2:
        st.session_state['stack'] = st.text_input("Tech Stack (comma separated)", st.session_state['stack'])
        st.session_state['challenge'] = st.text_area("Key Challenge", st.session_state['challenge'], height=150)

    # 2. MEDIA SELECTION (LOCAL ASSETS)
    st.markdown("---")
    st.markdown("### 🎬 Media (GIF)")
    
    local_gifs = get_local_gifs()
    if not local_gifs:
        st.warning("⚠️ No GIFs found in 'static/' folder! Please add files manually.")
    else:
        # Selection Dropdown
        # Find index of currently selected gif if editing
        try:
            default_ix = local_gifs.index(st.session_state['selected_gif']) + 1
        except ValueError:
            default_ix = 0

        selected = st.selectbox(
            "Select GIF from 'static' folder:", 
            options=["-- Select --"] + local_gifs,
            index=default_ix
        )
        
        if selected != "-- Select --":
            st.session_state['selected_gif'] = selected
            st.image(f"static/{selected}", caption="Preview", width=400)

    # 3. LINKS
    col3, col4 = st.columns(2)
    with col3:
        st.session_state['repo'] = st.text_input("GitHub Repo URL", st.session_state['repo'])
    with col4:
        st.session_state['live'] = st.text_input("Live Demo URL", st.session_state['live'])

    # 4. ACTIONS
    st.markdown("---")
    btn_text = "🔄 Update Project" if st.session_state['edit_mode'] else "🚀 Deploy Project"
    
    if st.button(btn_text, type="primary"):
        if not st.session_state['title'] or st.session_state.get('selected_gif', '-- Select --') == "-- Select --":
            st.error("Title and GIF are required!")
        else:
            data = {
                "title": st.session_state['title'],
                "description": st.session_state['desc'],
                "stack": [s.strip() for s in st.session_state['stack'].split(',') if s.strip()],
                "challenge": st.session_state['challenge'],
                "links": {"github": st.session_state['repo'], "live": st.session_state['live']},
                "media_type": "gif",
                "gifFilename": st.session_state['selected_gif'], # Storing filename ONLY
                "duration": get_gif_duration(st.session_state['selected_gif']), # Save duration
                "timestamp": int(time.time() * 1000)
            }
            
            ref = db.reference('projects')
            
            if st.session_state['edit_mode']:
                ref.child(st.session_state['edit_id']).update(data)
                st.success("✅ Project Updated Successfully!")
            else:
                ref.push(data)
                st.success("✅ Project Created Successfully!")
            
            # Reset form
            st.session_state['edit_mode'] = False
            st.session_state['edit_id'] = None
            st.session_state['title'] = ""
            st.session_state['desc'] = ""
            st.session_state['stack'] = ""
            st.session_state['challenge'] = ""
            st.session_state['repo'] = ""
            st.session_state['live'] = ""
            st.session_state['selected_gif'] = ""
            time.sleep(1)
            st.rerun()
            
    if st.session_state['edit_mode']:
        if st.button("❌ Cancel Edit"):
            st.session_state['edit_mode'] = False
            st.session_state['edit_id'] = None
            st.session_state['title'] = ""
            st.session_state['desc'] = ""
            st.session_state['stack'] = ""
            st.session_state['challenge'] = ""
            st.session_state['repo'] = ""
            st.session_state['live'] = ""
            st.session_state['selected_gif'] = ""
            st.rerun()

# --- TAB 2: MANAGE EXISTING ---
with tab2:
    st.subheader("📋 Existing Projects")
    try:
        ref = db.reference('projects')
        projects = ref.get()
        
        if projects:
            for pid, pdata in projects.items():
                with st.expander(f"{pdata.get('title', 'Untitled')} ({pdata.get('media_type', 'unknown')})"):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        st.write(f"**Desc:** {pdata.get('description', '')[:100]}...")
                        st.write(f"**GIF:** {pdata.get('gifFilename', 'None')}")
                    with c2:
                        if st.button("✏️ Edit", key=f"edit_{pid}"):
                            st.session_state['edit_mode'] = True
                            st.session_state['edit_id'] = pid
                            # Load data
                            st.session_state['title'] = pdata.get('title', '')
                            st.session_state['desc'] = pdata.get('description', '')
                            st.session_state['stack'] = ",".join(pdata.get('stack', []))
                            st.session_state['challenge'] = pdata.get('challenge', '')
                            st.session_state['repo'] = pdata.get('links', {}).get('github', '')
                            st.session_state['live'] = pdata.get('links', {}).get('live', '')
                            st.session_state['selected_gif'] = pdata.get('gifFilename', '')
                            st.rerun()
                    with c3:
                        if st.button("🗑️ Delete", key=f"del_{pid}", type="primary"):
                            ref.child(pid).delete()
                            st.success("Deleted!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("No projects found in database.")
    except Exception as e:
        st.error(f"Error fetching projects: {e}")