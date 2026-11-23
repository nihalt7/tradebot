# Deployment Guide: Vercel + Render + MongoDB Atlas

This document outlines the exact deployment workflow for the **TradePulse AI Indian Stock Market Quant Platform**.

---

## Architecture Summary

| Layer | Service | Configuration |
|---|---|---|
| **Frontend** | [Vercel](https://vercel.com) | React 18 + Vite + TypeScript + Tailwind CSS |
| **Backend** | [Render](https://render.com) | Python 3.12 + FastAPI + Uvicorn + WebSockets |
| **Database** | [MongoDB Atlas](https://www.mongodb.com/atlas) | Cloud Document DB via PyMongo / Motor |
| **Repository** | GitHub | Continuous Integration & Deployment (CI/CD) |

---

## 1. Database Setup (MongoDB Atlas)

1. Sign in to [MongoDB Atlas](https://cloud.mongodb.com).
2. Create a free **M0 Sandbox Cluster** (e.g. AWS / Mumbai `ap-south-1` or Oregon `us-west-2`).
3. Under **Database Access**, create a user (e.g. `tradepulse_admin`) with a secure password and **Read and Write to Any Database** permissions.
4. Under **Network Access**, add an IP Access List entry:
   - Click **Add IP Address** -> Choose **Allow Access from Anywhere** (`0.0.0.0/0`) so Render workers can connect.
5. In your cluster dashboard, click **Connect** -> **Drivers** -> **Python (3.12 or later)**.
6. Copy the connection string format:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority
   ```
7. Note this down as your `MONGODB_URI`.

---

## 2. Backend Deployment (Render)

### Option A: Using the included Blueprint (`render.yaml`)
1. Push your repository to GitHub.
2. Sign in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Blueprint**.
4. Connect your GitHub repository. Render will automatically detect `render.yaml`.
5. Enter the `MONGODB_URI` environment variable value when prompted.
6. Click **Apply**. Render will build and deploy the FastAPI service.

### Option B: Manual Web Service Setup on Render
1. In Render, click **New +** -> **Web Service**.
2. Connect your GitHub repo.
3. Configure the following settings:
   - **Name:** `tradepulse-backend`
   - **Language:** `Python 3`
   - **Region:** Choose closest to your users (e.g. Singapore / Frankfurt / Oregon)
   - **Branch:** `main`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables**:
   | Variable | Value | Description |
   |---|---|---|
   | `PYTHON_VERSION` | `3.12.0` | Python runtime version |
   | `MONGODB_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority` | MongoDB Atlas URI |
   | `DATABASE_NAME` | `tradepulse` | Database name |
   | `CORS_ORIGINS` | `*` (or your Vercel URL) | Allowed frontend origins |
   | `SECRET_KEY` | *(generate a random string)* | JWT Signing key |
5. Click **Deploy Web Service**.
6. Once deployed, note down your backend URL (e.g., `https://tradepulse-backend.onrender.com`).

---

## 3. Frontend Deployment (Vercel)

1. Sign in to [Vercel](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. Configure Project Settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Edit and set to `frontend` (or keep root if building via root script)
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Under **Environment Variables**, add:
   | Variable Name | Value | Description |
   |---|---|---|
   | `VITE_API_URL` | `https://tradepulse-backend.onrender.com` | Your Render Backend URL |
   | `VITE_WS_URL` | `wss://tradepulse-backend.onrender.com/ws/market` | Render Secure WebSocket URL |
6. Click **Deploy**.
7. Vercel will build the SPA and provide your production URL (e.g., `https://tradepulse-ai.vercel.app`).

---

## 4. Environment Variables Reference

### Backend (Render)
```env
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=tradepulse
CORS_ORIGINS=*
SECRET_KEY=generate_a_random_32_char_hex_string
PORT=8000
```

### Frontend (Vercel)
```env
VITE_API_URL=https://tradepulse-backend.onrender.com
VITE_WS_URL=wss://tradepulse-backend.onrender.com/ws/market
```

---

## 5. Verification Checklist

1. **Health Check:** Open `https://<your-render-app>.onrender.com/health`. Expect:
   ```json
   {"status":"healthy","database":"connected","timestamp":"..."}
   ```
2. **Swagger Docs:** Open `https://<your-render-app>.onrender.com/docs` to test endpoints interactively.
3. **Frontend Connectivity:** Open your Vercel site. The top ticker should stream live NSE index quotes and WebSocket status should display `NSE WebSocket Live`.
4. **Chat Test:** Type `TOP 5` or `ANALYZE RELIANCE` in the chat to test live quant analysis card generation.
