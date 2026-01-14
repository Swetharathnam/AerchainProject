# AI-Powered RFP Management System

A single-user web application to streamline the Request for Proposal (RFP) process using AI.

## Tech Stack
- **Frontend**: React, Vite, TypeScript, Tailwind CSS, Shadcn/UI
- **Backend**: Python, FastAPI, SQLModel (SQLAlchemy), Pydantic
- **Database**: PostgreSQL
- **AI**: Google Gemini 1.5
- **Email**: Nodemailer (SMTP) / IMAP

## Project Setup

### Prerequisites
- Node.js (v24+)
- Python (3.11+)
- PostgreSQL installed and running locally
- Google Gemini API Key
- Gmail Account (App Password) for email testing

### Installation

#### 1. Backend
```bash
cd backend
# Create virtual environment (optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env with your DB credentials and API keys
```

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## AI Tools Usage
- **Google Gemini**: Used for extracting structured data from natural language RFPs and vendor emails.

## Decisions & Assumptions
- **Single User**: No authentication implemented as per requirements.
- **Email Polling**: basic IMAP polling is used instead of webhooks for simplicity in local dev.