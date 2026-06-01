from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return "Server running with FREE Groq AI!"

def analyze_with_ai(text):
    """Send text to FREE Groq AI for analysis"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # UPDATED MODEL NAME
            messages=[
                {"role": "system", "content": "You are a document analyzer. Provide: 1) Document type 2) 3 key points 3) Brief summary in simple English"},
                {"role": "user", "content": f"Analyze this document:\n\n{text[:4000]}"}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI analysis error: {str(e)}"

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['file']

    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files allowed"}), 400

    try:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

        if len(text) < 50:
            return jsonify({"error": "Could not extract text from PDF"}), 400

        ai_result = analyze_with_ai(text)

        return jsonify({
            "filename": file.filename,
            "pages": len(pdf.pages),
            "analysis": ai_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)