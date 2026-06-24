# ContractScan - Backend API 🐍

The Python/Flask backend for the [ContractScan App](https://github.com/vigneshsai52/contractscan-frontend).

🚀 **Live App:** [Click Here](https://contractscan-frontend-three.vercel.app/) *(Takes ~50 seconds to wake up!)*

## ⚡ API Features

- **AI Analysis:** Uses Groq AI (Llama 3.1) to analyze contracts and extract key terms.
- **Chat with Contract:** Contextual Q&A based on the uploaded document text.
- **History Dashboard:** Saves past 5 analyses per user in SQLite.
- **User Auth:** Secure Sign Up & Login with JWT authentication.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Python, Flask |
| **AI Engine** | Groq API (Llama 3.1) |
| **Database** | SQLite |
| **Authentication** | JWT (JSON Web Tokens) |
| **Deployment** | Render |

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/signup` | Register user | No |
| `POST` | `/login` | Authenticate user | No |
| `POST` | `/analyze` | Upload & analyze contract | Yes |
| `GET` | `/history` | Get past 5 analyses | Yes |
| `POST` | `/chat` | Chat with a specific contract | Yes |

## 🚀 Getting Started

```bash
git clone https://github.com/vigneshsai52/contractscan.git
cd contractscan
pip install -r requirements.txt
python app.py
```

### Frontend Repo

👉 [ContractScan Frontend](https://github.com/vigneshsai52/contractscan-frontend)

## 📝 License

MIT License — free to use and modify.

Built with ❤️ by Udayagiri Vignesh Sai
