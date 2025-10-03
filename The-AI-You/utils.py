import os
import requests
from PyPDF2 import PdfReader
def push(text):
         requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
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
     
     