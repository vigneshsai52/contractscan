# ContractScan 🔍

**AI-powered contract analyzer.** Upload any contract (PDF, DOCX, DOC, TXT) and get instant analysis of key terms, risky clauses, and a plain-English summary.

🚀 **Live Demo:** https://documind-ai-roan.vercel.app/

---

## ⚡ The Problem

People sign contracts every day without understanding them:
- Employment agreements with hidden non-competes
- Rental leases with unfair penalties
- Service contracts with auto-renewal traps
- NDAs that are way too broad

**Lawyers cost $300-500/hour.** Most people can't afford that.

---

## ✅ The Solution

ContractScan uses AI to make contract review **free and accessible**:

| Feature | What It Does |
|---------|-------------|
| 📋 **Contract Type Detection** | Identifies what kind of contract it is |
| 👥 **Party Extraction** | Who's involved and their roles |
| 📅 **Key Dates** | Deadlines, start/end dates, milestones |
| 💰 **Financial Terms** | Payments, penalties, fees, hidden costs |
| ⚠️ **Risk Detection** | Flags HIGH/MEDIUM/LOW risk clauses |
| ❓ **Missing Clauses** | Standard protections that should be there |
| 📝 **Plain English Summary** | Explains what you're actually agreeing to |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask |
| **AI Engine** | Groq API (Llama 3.1) — **FREE tier** |
| **Document Processing** | PyPDF2, python-docx |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Deployment** | Railway (backend), Vercel (frontend) |

---

## 📊 Example Analysis

**Input:** Employment contract PDF

**Output:**

📋 **CONTRACT TYPE**
Employment Agreement

👥 **PARTIES INVOLVED**
- Employee: John Doe
- Employer: TechCorp Inc.

📅 **KEY DATES & DEADLINES**
- Start Date: January 15, 2024
- Review Period: 90 days
- Notice Period: 30 days

💰 **FINANCIAL TERMS**
- Salary: $85,000/year
- Bonus: Up to 10% based on performance
- Health insurance: Employer pays 80%

⚠️ **RISKY CLAUSES**
- 🔴 HIGH RISK: Non-compete clause prevents working in same industry for 2 years after leaving
- 🟡 MEDIUM RISK: Intellectual property assignment is very broad
- 🟢 LOW RISK: 30-day termination notice is shorter than standard 60 days

❓ **MISSING STANDARD CLAUSES**
- Severance package details
- Remote work policy
- Expense reimbursement procedure

📝 **PLAIN ENGLISH SUMMARY**
You're agreeing to work for TechCorp for $85k/year. The big red flag is the non-compete — you can't work in tech for 2 years if you leave. Also, they own everything you create, even outside work hours. Consider negotiating these points before signing.

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/vigneshsai52/contractscan.git
cd contractscan

# Backend setup
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
python app.py

# Frontend (open index.html or use live server)
```

---

## 🧠 What I Learned

| Challenge | Solution |
|-----------|----------|
| PDF parsing edge cases | Handled scanned vs text-based PDFs, encoding issues |
| AI cost management | Used Groq's free tier instead of expensive OpenAI |
| Structured output | Prompt engineering for consistent analysis format |
| Multi-format support | Unified text extraction for PDF, DOCX, TXT |
| CORS deployment | Configured Railway/Vercel for cross-origin requests |

---

## 📝 License

MIT License — free to use and modify.

Built with ❤️ to help people understand what they sign.
