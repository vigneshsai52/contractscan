from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import os
import sqlite3
from groq import Groq
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- SIMPLE SQLITE DATABASE (NO MORE MONGODB SSL ERRORS) ---
def init_db():
    conn = sqlite3.connect('contractscan.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

init_db()
# ----------------------------------------------------------

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "mySuperSecretKey123")
jwt = JWTManager(app)

# --- GROQ AI SETUP ---
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")
groq_client = Groq(api_key=api_key)
# ------------------------

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}

@app.route('/')
def home():
    return "ContractScan API v3.0 - SQLite Edition - Bulletproof!"

# --- AUTH ROUTES ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('contractscan.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('contractscan.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if not user or not check_password_hash(user[2], password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify({"access_token": access_token, "email": email}), 200
# ----------------------

def extract_text(file, filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.pdf':
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
        return text, len(pdf.pages)
    elif ext in ('.docx', '.doc'):
        import docx
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text, None
    elif ext == '.txt':
        text = file.read().decode('utf-8', errors='ignore')
        return text, None
    else:
        return None, None

def analyze_contract(text):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert legal contract analyzer. Analyze the provided contract and return a structured analysis.

📋 CONTRACT TYPE
👥 PARTIES INVOLVED
📅 KEY DATES & DEADLINES
💰 FINANCIAL TERMS
⚠️ RISKY CLAUSES (HIGH/MEDIUM/LOW)
❓ MISSING STANDARD CLAUSES
📝 PLAIN ENGLISH SUMMARY"""
                },
                {
                    "role": "user",
                    "content": f"Analyze this contract:\n\n{text[:6000]}"
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI analysis error: {str(e)}"

# --- PROTECTED ANALYSIS ROUTE ---
@app.route('/analyze', methods=['POST'])
@jwt_required() 
def analyze():
    current_user_email = get_jwt_identity() 
    
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Unsupported file type"}), 400

    try:
        text, pages = extract_text(file, file.filename)
        if text is None or not text.strip():
            return jsonify({"error": "Could not extract text. Try a text-based PDF or DOCX."}), 400

        contract_keywords = ['agreement', 'contract', 'terms', 'parties', 'obligations', 
                           'liability', 'confidential', 'termination', 'payment', 'clause']
        text_lower = text.lower()
        is_likely_contract = any(kw in text_lower for kw in contract_keywords)

        ai_result = analyze_contract(text)

        result = {
            "filename": file.filename,
            "is_likely_contract": is_likely_contract,
            "analysis": ai_result,
            "user_email": current_user_email
        }
        if pages is not None:
            result["pages"] = pages

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)