import os
import requests
import streamlit as st
from PyPDF2 import PdfReader
def push(text):
         requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": st.secrets["PUSHOVER_TOKEN"],
            "user": st.secrets["PUSHOVER_USER"],
            "message": text,
        }
    )

def read_pdf(pdf_path):       
     reader = PdfReader(pdf_path)
     prof_summary = ""
     for page in reader.pages:
          text = page.extract_text()
          if text:
               prof_summary += text
     return prof_summary

if __name__ == "__main__":
     push()
     
     