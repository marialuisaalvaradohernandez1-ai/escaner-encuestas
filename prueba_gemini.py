import requests
import streamlit as st

API_KEY = st.secrets["GEMINI_API_KEY"].strip()

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent"

headers = {
	"Content-Type": "application/json",
	"c-goog-api-key": API_KEY
}

payload= {
	"contents": [
		{
			"parts": [
				{"text": "Responde únicamente: OK"}
			]
		}
	]
}

response = requests.post(
	url,
	headers=headers,
	json=payload,
	timeout=60
)

print("status:", response.status_code)
print(response.text)
