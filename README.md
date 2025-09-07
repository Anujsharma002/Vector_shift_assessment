# 🚀 HubSpot OAuth Integration – VectorShift Technical Assessment

This project implements a **HubSpot OAuth2 integration** using **FastAPI (backend)**, **React (frontend)**, and **Redis** for temporary credential storage.  
It is built as part of the **VectorShift Integrations Technical Assessment**.

---

## 📂 Project Structure

```
/backend
  ├── main.py
  ├── integrations/
  │     ├── airtable.py
  │     ├── notion.py
  │     └── hubspot.py   # 🔑 HubSpot OAuth integration
  └── redis_client.py

/frontend
  └── src/
        ├── integrations/
        │     ├── airtable.js
        │     ├── notion.js
        │     └── hubspot.js   # 🔑 HubSpot OAuth UI
        ├── integration-form.js
        └── data-form.js
```

---

## ⚙️ Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)  
- [Node.js + npm](https://nodejs.org/)  
- [Redis](https://redis.io/) (for caching OAuth states & credentials)  
- A **HubSpot Developer Account** → [Sign up here](https://developers.hubspot.com/)  

---

## 🔑 HubSpot App Setup

1. Go to [HubSpot Developer Dashboard](https://developers.hubspot.com/).  
2. Create a **new private app**.  
3. Configure **OAuth settings**:
   - Redirect URI:
     ```
     http://localhost:8000/integrations/hubspot/oauth2callback
     ```
   - Example scopes:
     ```
     contacts crm.objects.deals.read
     ```
4. Copy your **Client ID** and **Client Secret** into `/backend/integrations/hubspot.py`:

   ```python
   CLIENT_ID = "your-client-id"
   CLIENT_SECRET = "your-client-secret"
   ```

👉 (Optional) Store them in a `.env` file for security.

---

## 🖥️ Backend Setup (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # (Linux/Mac)
.venv\Scripts\activate      # (Windows)

pip install -r requirements.txt
redis-server  # start Redis
uvicorn main:app --reload
```

Backend runs at:  
👉 `http://localhost:8000`

---

## 🌐 Frontend Setup (React)

```bash
cd frontend
npm install
npm run start
```

Frontend runs at:  
👉 `http://localhost:3000`

---

## 🔄 OAuth Flow

1. Open the frontend (`http://localhost:3000`).  
2. Select **HubSpot** from the integrations list.  
3. Click **Connect to HubSpot**.  
4. A popup will open for HubSpot login + authorization.  
5. On success:
   - The popup closes automatically.  
   - Access + Refresh tokens are stored in **Redis**.  
   - Credentials appear in the UI (via `DataForm`).  

---
---

## 🛠️ Troubleshooting

- **`No credentials found`** → Ensure Redis is running and app has correct `CLIENT_ID` / `CLIENT_SECRET`.  
- **`State does not match`** → Verify the redirect URI is **exactly** the same in HubSpot app settings.  
- **`Couldn't complete the connection`** → Ensure scopes are correctly added both in HubSpot and in `hubspot.py`.  

---

## ✅ Features Implemented

- [x] HubSpot OAuth2 integration with full flow  
- [x] Temporary credential storage in Redis  
- [x] React UI with popup + auto-close  
- [x] Example API call to HubSpot (Contacts)  
- [x] Integration alongside Airtable & Notion  

---

## 📜 License

This project is for **Vector_SHIFT**.  
