# Personal AI Command Center

A unified AI agent to control your entire digital life.

## 🌟 Features

- **📧 Email Automation**: Auto-classify, smart replies, schedule extraction
- **📱 Social Media Management**: Schedule posts, sync platforms, monitor engagement
- **🏠 Smart Home Control**: Scene automation, voice control, energy monitoring
- **🌐 Browser Automation**: Form filling, price monitoring, scheduled checks
- **🤖 Local AI**: Ollama-powered offline intelligence
- **✅ Human Approval**: HITL (Human-in-the-Loop) for sensitive actions
- **📜 Audit Logs**: Immutable hash-chain logs for transparency

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI + SQLAlchemy + WebSocket |
| **Frontend** | Next.js 15 + React 19 + TailwindCSS |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Cache** | Redis |
| **AI** | Ollama (local) + OpenAI (cloud) |
| **Email** | IMAP/SMTP |
| **Social** | Twitter API, LinkedIn API |
| **Smart Home** | Home Assistant REST API |
| **Browser** | Playwright |
| **Security** | AES-256 encryption + HITL approval |

## 📦 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama (optional, for local AI)
- Redis (optional, for caching)
- Home Assistant (optional, for smart home)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Initialize database
python init_db.py

# Test integrations (optional)
python test_services.py

# Start server
python run.py
```

Backend will be available at `http://localhost:8001`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 🔧 Configuration

Create a `.env` file in the backend directory:

```env
# Email (Gmail example)
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Twitter/X
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret

# Home Assistant
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=your_token

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3

# Security
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_32_byte_key
```

## 🚀 Quick Start

1. **Start Backend**
   ```bash
   cd backend
   source venv/bin/activate
   python run.py
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8001/docs

## 📁 Project Structure

```
personal-ai-command-center/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints (54 endpoints)
│   │   │   ├── email.py   # Email management
│   │   │   ├── social.py  # Social media
│   │   │   ├── home.py    # Smart home
│   │   │   ├── browser.py # Browser automation
│   │   │   ├── hitl.py    # Human approval
│   │   │   └── audit.py   # Audit logs
│   │   ├── services/      # Integration services
│   │   │   ├── email_service.py    # IMAP/SMTP
│   │   │   ├── social_service.py   # Twitter/LinkedIn
│   │   │   ├── home_assistant_service.py # Home Assistant
│   │   │   └── ollama_service.py   # Local LLM
│   │   ├── models/        # Data models (8 tables)
│   │   ├── core/          # Configuration
│   │   └── main.py        # FastAPI app
│   ├── tests/
│   ├── .env.example       # Environment template
│   ├── test_services.py   # Integration tester
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   └── components/    # React components (8)
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## 📊 Project Stats

| Category | Count |
|----------|-------|
| Backend Files | 24 |
| Backend Code | 7,827 lines |
| API Endpoints | 58 |
| Frontend Components | 8 |
| Services | 4 |
| Database Tables | 8 |

## ✅ API Status

All endpoints tested and working:

| API | Status |
|-----|--------|
| Auth (Register/Login/Me) | ✅ |
| Email (Create/List/Categorize) | ✅ |
| Social (Create/Publish/List) | ✅ |
| Home (Register/Control/Sync) | ✅ |
| Browser (Create/Execute) | ✅ |
| HITL (Create/Approve/Reject) | ✅ |
| Audit (List/Verify/Export) | ✅ |

## 🔌 API Endpoints

### Email API (8 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/email` | List emails |
| GET | `/api/email/{id}` | Get email details |
| POST | `/api/email/{id}/categorize` | Categorize email |
| POST | `/api/email/{id}/process` | Mark as processed |
| POST | `/api/email/reply` | Send reply |
| GET | `/api/email/unread/count` | Unread count |
| POST | `/api/email/sync` | Sync from IMAP |
| DELETE | `/api/email/{id}` | Delete email |

### Social Media API (9 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/social` | Create post |
| GET | `/api/social` | List posts |
| POST | `/api/social/{id}/publish` | Publish post |
| DELETE | `/api/social/{id}` | Delete post |
| GET | `/api/social/platforms` | List platforms |

### Smart Home API (12 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/home` | List devices |
| POST | `/api/home` | Register device |
| POST | `/api/home/{id}/control` | Control device |
| POST | `/api/home/scenes/execute` | Execute scene |
| POST | `/api/home/sync` | Sync devices |

### Browser Automation API (11 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/browser` | Create task |
| POST | `/api/browser/{id}/execute` | Execute task |
| POST | `/api/browser/quick/form-fill` | Quick form fill |
| POST | `/api/browser/quick/screenshot` | Take screenshot |

### HITL API (10 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/hitl` | Create approval request |
| GET | `/api/hitl/pending` | Get pending requests |
| POST | `/api/hitl/{id}/approve` | Approve/reject |
| GET | `/api/hitl/stats` | Get statistics |

### Audit API (8 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/audit` | List logs |
| GET | `/api/audit/verify` | Verify chain |
| GET | `/api/audit/export` | Export logs |

## 🧪 Testing Integrations

```bash
cd backend
python test_services.py
```

This will test:
- ✅ Email (IMAP/SMTP)
- ✅ Twitter API
- ✅ Home Assistant
- ✅ Ollama (Local LLM)

## 🐳 Docker Deployment

```bash
# Coming soon
docker-compose up -d
```

## 📄 License

MIT

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

---

Built with ❤️ for Personal AI Automation
