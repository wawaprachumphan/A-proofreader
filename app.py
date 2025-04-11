import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re
import json
import os

# Config
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Gemini setup
model = genai.GenerativeModel("gemini-pro")

# Load credentials
credentials_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
creds = service_account.Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)

# Google Docs reader
def extract_doc_id(link):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", link)
    return match.group(1) if match else None

def read_google_doc(doc_id):
    docs_service = build("docs", "v1", credentials=creds)
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])
    text = ''
    for c in content:
        if 'paragraph' in c:
            for e in c['paragraph'].get('elements', []):
                if 'textRun' in e:
                    text += e['textRun']['content']
    return text.strip()

# Proofread with Gemini
def proofread_text(text):
    prompt = f"Please proofread and edit the following text for grammar, clarity, and tone:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

# Streamlit UI
st.title("📄 Google Docs Proofreader with Gemini AI")
st.write("Paste a Google Docs link below (shared with 'Anyone with the link can view').")

doc_link = st.text_input("🔗 Google Docs link")

if doc_link:
    try:
        doc_id = extract_doc_id(doc_link)
        raw_text = read_google_doc(doc_id)
        st.subheader("📄 Original Text")
        st.text_area("Original", raw_text, height=300)

        with st.spinner("🔍 Proofreading with Gemini..."):
            improved_text = proofread_text(raw_text)

        st.subheader("✅ Improved Text")
        st.text_area("Proofread", improved_text, height=300)
    except Exception as e:
        st.error(f"Error: {e}")
