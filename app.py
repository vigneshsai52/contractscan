from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import os
import json
from groq import Groq
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- DATABASE & AUTH SETUP ---
MONGO_URI = "mongodb+srv://batting370_db_user:mydb123@vignesh.txnygj9.mongodb.net/?appName=vignesh"
client_db = MongoClient(MONGO_URI)
db = client_db.contractscan_db 
users_collection = db.users 
history_collection = db.history 

app.config["JWT_SECRET_KEY"] = "mySuperSecretKey123"
jwt = JWTManager(app)
# --------------------------------

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
    return "ContractScan API v2.0 - Now with Auth & Database!"

# --- AUTH ROUTES ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"email": email, "password": hashed_password})
    
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})
    if not user or not check_password_hash(user['password'], password):
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

Your response must follow this exact format:

📋 CONTRACT TYPE
[Identify: Employment Agreement, NDA, Rental/Lease, Service Agreement, Sales Contract, Loan Agreement, Partnership Agreement, etc.]

👥 PARTIES INVOLVED
• [Party 1 name and role]
• [Party 2 name and role]

📅 KEY DATES & DEADLINES
• [Date]: [What happens on this date]

💰 FINANCIAL TERMS
• [Payment amount, frequency, penalties, fees, etc.]

⚠️ RISKY CLAUSES
🔴 HIGH RISK: [Clause that could cause major problems]
🟡 MEDIUM RISK: [Clause that could be problematic]
🟢 LOW RISK: [Minor concern]

❓ MISSING STANDARD CLAUSES
• [Missing protection or standard term]

📝 PLAIN ENGLISH SUMMARY
[Explain this contract simply. What should they watch out for?]"""
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
            return jsonify({"error": "Could not extract text. PDF might be scanned/image-based. Try a text PDF or DOCX."}), 400

        contract_keywords = ['agreement', 'contract', 'terms', 'parties', 'obligations', 
                           'liability', 'confidential', 'termination', 'payment', 'clause']
        text_lower = text.lower()
        is_likely_contract = any(kw in text_lower for kw in contract_keywords)

        ai_result = analyze_contract(text)

        result = {
            "filename": file.filename,
            "is_likely_contract": is_likely_contract,
            "analysis": ai_result,
            "user_email": current_user_email,
            "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        }
        if pages is not None:
            result["pages"] = pages

        history_collection.insert_one(result.copy())
        result.pop('_id', None)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- GET USER HISTORY ROUTE ---
@app.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    current_user_email = get_jwt_identity()
    user_history = history_collection.find({"user_email": current_user_email}).sort("date", -1).limit(10)
    
    histories = []
    for doc in user_history:
        doc.pop('_id', None) 
        histories.append(doc)
        
    return jsonify(histories), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)