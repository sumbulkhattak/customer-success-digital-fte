# Free API Setup Guide

All APIs used in this project have free tiers. Follow these steps to get your keys.

**Total time: ~15 minutes | Total cost: $0**

---

## 1. AI Provider (Choose One)

### Option A: Groq (Recommended)

Groq offers the fastest free AI API with generous rate limits.

**Models available (free):** `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`

**Steps:**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with Google or email (no credit card required)
3. Click **API Keys** in the left sidebar
4. Click **Create API Key**
5. Copy the key (starts with `gsk_`)

**In your `.env`:**
```env
AI_PROVIDER=groq
OPENAI_API_KEY=gsk_your-key-here
```

**Free tier limits:** ~30 requests/minute, 14,400 requests/day

---

### Option B: Google Gemini

Google offers free Gemini API access with no credit card.

**Models available (free):** `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-2.5-pro` (limited)

**Steps:**
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **Create API key**
4. Select or create a Google Cloud project
5. Copy the key

**In your `.env`:**
```env
AI_PROVIDER=gemini
OPENAI_API_KEY=your-gemini-key-here
```

**Free tier limits:** Gemini Flash: 10 RPM, 250 requests/day | Flash-Lite: 15 RPM, 1,000 requests/day

---

### Option C: OpenAI (Paid)

If you have an OpenAI account with credits.

**Steps:**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click **Create new secret key**
3. Copy the key (starts with `sk-`)

**In your `.env`:**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

---

## 2. Twilio WhatsApp (Free Trial)

Twilio provides a free trial with $15.50 credit and a WhatsApp Sandbox.

**Steps:**

### Sign Up
1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Fill in your details (no credit card required)
3. Verify your phone number and email

### Get Credentials
4. Go to [console.twilio.com](https://console.twilio.com)
5. Your **Account SID** and **Auth Token** are on the dashboard

### Activate WhatsApp Sandbox
6. In Twilio Console, go to **Messaging** > **Try it out** > **Send a WhatsApp message**
7. Follow the instructions to join the sandbox:
   - Open WhatsApp on your phone
   - Send the code shown (e.g., `join sandy-boat`) to **+1 415 523 8886**
8. You'll receive a confirmation message

### Configure Webhook
9. In the sandbox settings, set the webhook URL to:
   - **When a message comes in:** `https://your-url/webhooks/whatsapp`
   - For local development, use [ngrok](https://ngrok.com) to get a public URL:
     ```bash
     ngrok http 8000
     ```
   - Then use the ngrok URL: `https://abc123.ngrok.io/webhooks/whatsapp`

**In your `.env`:**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Sandbox limits:** Unlimited messages (sandbox only, not production)

---

## 3. Gmail API (Free)

Gmail API is free for personal use. You need a Google Cloud project with OAuth2 credentials.

**Steps:**

### Create Google Cloud Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown (top bar) > **New Project**
3. Name it (e.g., `techcorp-fte`) and click **Create**

### Enable Gmail API
4. Go to **APIs & Services** > **Library**
5. Search for **Gmail API**
6. Click **Enable**

### Configure OAuth Consent Screen
7. Go to **APIs & Services** > **OAuth consent screen**
8. Select **External** and click **Create**
9. Fill in app name (e.g., `TechCorp FTE`), your email for support
10. Add scopes: `gmail.readonly`, `gmail.send`, `gmail.modify`
11. Add your email as a test user
12. Click **Save**

### Create OAuth Credentials
13. Go to **APIs & Services** > **Credentials**
14. Click **+ Create Credentials** > **OAuth client ID**
15. Application type: **Desktop app**
16. Name it (e.g., `FTE Desktop`)
17. Click **Create**
18. **Download JSON** and save as `credentials/gmail.json`

### Generate Token (First Run)
19. Create the credentials directory:
    ```bash
    mkdir -p credentials
    ```
20. The first time the app runs, it will open a browser for OAuth authorization
21. Sign in and grant permissions
22. A token file will be saved automatically

**In your `.env`:**
```env
GMAIL_CREDENTIALS_PATH=./credentials/gmail.json
```

### Optional: Pub/Sub for Push Notifications
For real-time email notifications (not required for basic testing):
1. Enable **Cloud Pub/Sub API** in Google Cloud Console
2. Create a topic: `projects/your-project-id/topics/gmail-push`
3. Create a push subscription pointing to your webhook URL

**Gmail API limits:** 250 quota units/second (free)

---

## 4. PostgreSQL (Free via Docker)

Already configured in `docker-compose.yml`. No sign-up needed.

```bash
docker-compose up -d postgres
```

If you want a free cloud database instead:
- [Neon](https://neon.tech) - Free tier, 0.5 GiB storage
- [Supabase](https://supabase.com) - Free tier, 500 MB storage

---

## 5. Kafka (Free via Docker)

Already configured in `docker-compose.yml`. No sign-up needed.

```bash
docker-compose up -d zookeeper kafka
```

The project also has an **InMemoryEventBus** fallback that works without Kafka.

---

## Quick Start with Free APIs

1. **Copy and configure `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Get a Groq API key** (fastest option - 2 minutes):
   - Go to [console.groq.com](https://console.groq.com)
   - Sign up and create an API key
   - Paste it in `.env` as `OPENAI_API_KEY=gsk_...`

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```

4. **Seed the database:**
   ```bash
   docker-compose --profile seed up seed
   ```

5. **Test the health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

6. **Test the web form:**
   ```bash
   curl -X POST http://localhost:8000/support/submit \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test User",
       "email": "test@example.com",
       "subject": "Testing the AI agent",
       "category": "feature_question",
       "priority": "medium",
       "message": "How do I create a new project in TechCorp?"
     }'
   ```

---

## Summary

| Service | Provider | Cost | Sign-up Link |
|---------|----------|------|-------------|
| AI Agent | Groq | Free | [console.groq.com](https://console.groq.com) |
| AI Agent | Google Gemini | Free | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| WhatsApp | Twilio Trial | Free ($15.50 credit) | [twilio.com/try-twilio](https://www.twilio.com/try-twilio) |
| Email | Gmail API | Free | [console.cloud.google.com](https://console.cloud.google.com) |
| Database | PostgreSQL (Docker) | Free | N/A |
| Streaming | Kafka (Docker) | Free | N/A |
