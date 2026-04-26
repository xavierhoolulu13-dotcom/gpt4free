# n8n-Style Chatbot with Google Sheets Backend

A production-ready conversational AI system that automatically routes user queries to specialized workflows, powered by gpt4free and Google Sheets.

## 🎯 Features

✅ **Intelligent Intent Routing** - Classifies user intent (Sales/Content/Data/General)  
✅ **Multi-Workflow Architecture** - Pre-configured AOM (Sales), CG (Content), and General agents  
✅ **Real-time Streaming** - Server-Sent Events for responsive chat UX  
✅ **Google Sheets Backend** - Easy management of workflows, agents, and routing rules  
✅ **Full Audit Trail** - All conversations automatically logged to Sheets  
✅ **Analytics** - Track success rates, response times, user engagement  
✅ **gpt4free Integration** - Free LLM with automatic provider fallback  
✅ **Session Management** - Full conversation history per user session  

## 🏗️ Architecture

```
User Message (Chat UI)
    ↓
[Intent Router] → Classifies intent (Sales/Content/Data/General)
    ↓
[Agent Selection] → Routes to appropriate workflow agent
    ↓
[gpt4free LLM] → Generates response via streaming
    ↓
[Google Sheets] → Logs conversation & analytics
    ↓
Response to user with workflow context
```

## 📦 Tech Stack

**Backend:**
- FastAPI (Python)
- Google Sheets API
- gpt4free (free LLM)
- Uvicorn

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Zustand (state management)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud project with Sheets API enabled
- Service account credentials (JSON)

### Backend Setup

1. **Clone and navigate:**
```bash
cd chatbot/backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your Google Sheets ID and credentials path
export SHEETS_ID=your-google-sheets-id
export GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/credentials.json
```

5. **Run server:**
```bash
python main.py
# Server runs on http://localhost:8000
```

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd chatbot/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create environment file:**
```bash
echo "VITE_API_URL=http://localhost:8000" > .env
```

4. **Start development server:**
```bash
npm run dev
# Open http://localhost:5173
```

## 📊 Google Sheets Setup

1. **Create a Google Cloud project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable Sheets API

2. **Create service account:**
   - Go to Service Accounts
   - Create new service account
   - Generate JSON key
   - Download and save as `credentials.json`

3. **Create Google Sheet:**
   - Create new spreadsheet
   - Share it with the service account email
   - Copy Sheet ID from URL

4. **Configure environment:**
```bash
export SHEETS_ID=your-sheet-id-from-url
export GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/credentials.json
```

The system will automatically create and initialize all required sheets on first run.

## 📋 Google Sheets Structure

### workflows
Stores available workflow configurations:
- `id`: Unique identifier (aom, cg, general)
- `name`: Display name
- `description`: Workflow description
- `icon`: Emoji icon
- `color`: Hex color code
- `system_prompt`: AI system prompt
- `created_at`: Timestamp

### agents
AI agents for each workflow:
- `id`: Agent identifier
- `name`: Display name
- `workflow_id`: Parent workflow
- `role`: Agent role/description
- `system_prompt`: Custom system prompt
- `model`: LLM model to use
- `created_at`: Timestamp

### conversations
Full chat logs:
- `id`: Message ID
- `session_id`: User session
- `user_id`: User identifier
- `message`: User message
- `intent`: Detected intent
- `workflow_id`: Routed workflow
- `response`: AI response
- `timestamp`: Message time

### routing_rules
Custom routing configuration:
- `intent_keyword`: Keyword to match
- `workflow_id`: Target workflow
- `confidence_threshold`: Min confidence
- `priority`: Rule priority

### users
User tracking:
- `user_id`: Unique user ID
- `name`: User name
- `email`: User email
- `created_at`: Registration time
- `last_active`: Last activity

### analytics
Performance metrics:
- `timestamp`: Event time
- `session_id`: Session ID
- `intent`: User intent
- `workflow_id`: Workflow used
- `response_time`: Response duration (ms)
- `success`: Success flag
- `user_feedback`: User rating/feedback

## 🔌 API Endpoints

### Chat Endpoints

**POST /chat** - Send message and get one-shot response
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me B2B SaaS leads",
    "session_id": "session_123",
    "user_id": "user_456"
  }'
```

Response:
```json
{
  "response": "I'll help you find qualified B2B SaaS leads...",
  "intent": "sales",
  "workflow": "AOM Master Flow",
  "confidence": "92%",
  "keywords_matched": ["find", "leads", "b2b", "saas"],
  "response_time": "1.23s",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

**GET /stream** - Stream response in real-time (Server-Sent Events)
```bash
curl "http://localhost:8000/stream?message=Find%20me%20leads&session_id=abc123"
```

### Management Endpoints

**GET /workflows** - List all workflows
```bash
curl http://localhost:8000/workflows
```

**GET /agents** - List all agents (optionally filtered by workflow)
```bash
curl http://localhost:8000/agents?workflow_id=aom
```

**GET /history** - Get conversation history
```bash
curl "http://localhost:8000/history?session_id=session_123"
```

**POST /clear** - Clear session history
```bash
curl -X POST "http://localhost:8000/clear?session_id=session_123"
```

**POST /refresh** - Reload from Google Sheets
```bash
curl -X POST http://localhost:8000/refresh
```

**GET /routing-info** - Debug routing decision
```bash
curl "http://localhost:8000/routing-info?message=Find%20me%20leads"
```

## 🧠 Intent Classification

### Sales Intent
Triggered by keywords: lead, prospect, client, customer, outreach, qualify, pipeline, etc.
→ Routes to: **AOM (Automated Outreach Machine)**

### Content Intent
Triggered by keywords: content, blog, seo, optimize, quality, rewrite, traffic, viral, etc.
→ Routes to: **CG (Content Guardian)**

### Data Intent
Triggered by keywords: data, process, analyze, transform, extract, report, etc.
→ Routes to: **General Assistant**

### General Intent
Default fallback for other queries
→ Routes to: **General Assistant**

## 🎛️ Customization

### Add New Workflow

Add a row to the `workflows` sheet:
```
my_workflow | My Workflow | Description | 🎯 | #ff6b6b | Your system prompt here | 2024-01-20T10:00:00Z
```

Then add agents to `agents` sheet:
```
agent_1 | My Agent | my_workflow | Senior Specialist | System prompt | gpt-3.5-turbo | 2024-01-20T10:00:00Z
```

### Customize Routing Rules

Add to `routing_rules` sheet to override default intent detection:
```
keyword_pattern | target_workflow | 0.75 | 10
```

### Add Agents to Existing Workflow

1. Add row to `agents` sheet
2. Call `POST /refresh` to reload
3. New agent available for workflow

## 🔒 Security Considerations

- Store credentials in environment variables, not in code
- Use service account with minimal required permissions
- Enable Sheets API auditing in Google Cloud
- Implement rate limiting in production
- Add authentication layer to API endpoints
- Encrypt sensitive data in Google Sheets

## 📈 Monitoring & Analytics

View analytics in the `analytics` sheet:
- **Response times** - Track performance
- **Success rates** - Monitor workflow effectiveness
- **Intent distribution** - Understand user behavior
- **User engagement** - Track active users

Query analytics:
```bash
curl "http://localhost:8000/analytics?workflow_id=aom&days=7"
```

## 🐛 Troubleshooting

**"Google Sheets API not found"**
- Ensure Sheets API is enabled in Google Cloud Console
- Check service account has Editor role

**"Sheet not found"**
- Verify SHEETS_ID is correct
- Confirm service account email has access to sheet

**"gpt4free provider unavailable"**
- Try different provider in .env
- Check internet connection

**CORS errors on frontend**
- Verify API_BASE URL in .env.local
- Check backend CORS configuration

## 📝 Example Conversations

### Sales Workflow
```
User: "Find me 50 qualified B2B SaaS leads in the HR tech space"
Bot: [Routes to AOM] I'll help you find and qualify HR tech leads...
     [System searches, analyzes, and provides lead list]
```

### Content Workflow
```
User: "Optimize my blog post about machine learning for SEO"
Bot: [Routes to CG] I'll analyze your content and provide SEO improvements...
     [Provides title, meta, keyword, structure recommendations]
```

### General Workflow
```
User: "What's the best way to structure a sales funnel?"
Bot: [Routes to General] Here's a comprehensive sales funnel approach...
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables (Production)
```bash
SHEETS_ID=prod-sheet-id
GOOGLE_SERVICE_ACCOUNT_JSON=/secrets/credentials.json
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=https://yourdomain.com
MAX_HISTORY=100
SESSION_TIMEOUT=3600
```

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please submit PRs to the main branch.

## 📞 Support

For issues and questions, create a GitHub issue or contact support.
