# Spastha-GenAI-RAG
```markdown
# 🧠 Spasht: Legal Document Intelligence with Generative AI

Spasht is a cloud-native platform for secure legal document analysis, built for scale, speed, and clarity. It combines Django Ninja, Next.js, Google Cloud, and Vertex AI to transform complex legal texts into referenced, fact-grounded insights using RAG pipelines and semantic search.

## 🚀 Features

### 🔐 Authentication & Security
- JWT-based user authentication
- reCAPTCHA v3 integration to prevent bot abuse
- CSRF protection with trusted origin validation
- GCP Token Swap for secure credential handling

### 📄 Document Ingestion & Storage
- Secure PDF upload via signed URLs or direct-to-GCS
- Temporary GCP access tokens for safe client-side uploads
- Public bucket upload support with FormData
- Metadata stored in NeonDB (PostgreSQL)

### 💬 Chat & Q&A Interface
- Authenticated chat interface with history retrieval
- RESTful endpoints for saving and retrieving messages
- Bot responses powered by RAG + Vertex AI summarization
- Auto-scroll and responsive UI for chat flow

### 🧠 Generative AI Capabilities
- Vertex AI Search for semantic retrieval
- Gemini / Vertex AI Text for summarizing legal content
- Referenced answers grounded in source documents

### 🌐 Frontend Stack
- Next.js with TypeScript
- Axios interceptor for JWT-based API calls
- File upload UI with status feedback
- Responsive chat interface with auto-scroll

### 🧪 Backend Architecture
- Django Ninja for type-safe REST APIs
- Swagger/OpenAPI auto-generated docs
- Serverless-ready with Cloud Run
- Containerized with Docker for portability

## 📦 Technologies Used

| Layer        | Tech Stack |
|--------------|------------|
| Frontend     | Next.js, TypeScript, Tailwind CSS |
| Backend      | Django Ninja, NeonDB, reCAPTCHA v3 |
| AI & Search  | Vertex AI Search, Gemini / Vertex AI Text |
| Cloud Infra  | Google Cloud Run, GCS, Cloud Functions |
| DevOps       | Docker, Swagger/OpenAPI |

## 📁 Project Structure

```

genai-next-frontend/
├── front/
│   ├── Dockerfile
│   ├── .env.local
│   ├── package.json
│   ├── next.config.ts
│   ├── src/
│   │   └── app/
│   │       ├── chat/
│   │       │   └── page.tsx  ← Chat + File Upload UI
│   │       ├── login/
│   │       │   └── page.tsx  ← Login with reCAPTCHA
│   │       └── signup/
│   │           └── page.tsx  ← Signup with email verification

````

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-org/spasht-legal-ai.git
cd genai-next-frontend/front
````

### 2. Configure environment variables

Create `.env.local` in the frontend directory:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_GCP_BUCKET=spastha-final-bucket
NEXT_PUBLIC_RECAPTCHA_SITE_KEY=your-site-key
```

Create `.env` in the backend directory:

```env
RECAPTCHA_PRIVATE_KEY=your-secret-key
EMAIL=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
NEON_PASSWORD=your-db-password
NEON_HOST=your-db-host
GCP_SERVICE_ACCOUNT_EMAIL=your-service-account@gcp.com
GCP_SIGNING_CREDENTIALS=your-json-credentials
GCP_AUDIENCE=your-workload-identity-audience
FRONTEND_URL=http://localhost:3000
```

### 3. Build and run with Docker

#### Frontend

```bash
npm install
npm run dev
```

#### Backend

```bash
docker build -t spasht-backend .
docker run -p 8000:8000 spasht-backend
```

## 📚 API Endpoints

| Endpoint                      | Method | Description                    |
| ----------------------------- | ------ | ------------------------------ |
| `/api/signup`                 | POST   | Register new user              |
| `/api/login`                  | POST   | Authenticate user              |
| `/api/chat/save`              | POST   | Save chat message              |
| `/api/chat/history`           | GET    | Retrieve chat history          |
| `/api/get-gcp-token`          | GET    | Get temporary GCP access token |
| `/verify-email/{uid}/{token}` | GET    | Verify user email              |
| `/api/refresh`                | POST   | Refresh JWT token              |

## 🧩 Architecture Overview

```plaintext
User → Next.js Frontend → Django Ninja Backend → GCP Services
                                      ↓
                            Vertex AI Search + GCS
```

## 💡 Unique Selling Points

* Referenced answers from exact legal documents
* Secure, scalable, and serverless infrastructure
* Ready-to-integrate APIs for enterprise use
* Future-ready for multi-document search, privacy, and audit trails

## 🧪 Testing & Debugging Tips

* Use DevTools → Network tab to inspect reCAPTCHA and API calls
* Check Cloud Run logs for port binding or CSRF errors
* Use `collectstatic` before deploying Django admin
* Validate `.env.local` and `.env` before building Docker images

## 📄 License

MIT © Blueberry Team – GenAI Exchange Hackathon

```

---

```
