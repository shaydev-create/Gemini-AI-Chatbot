# 🚀 Deployment Guide: Hybrid Gemini AI App

This guide explains how to deploy your **Hybrid AI Application** that supports both:
1.  **Online Mode:** Using Google Gemini API (Backend Python/Flask).
2.  **Offline Mode:** Using Chrome Built-in AI (Frontend JavaScript/PWA).

---

## 🏗️ Architecture Overview

The application uses a **Hybrid Strategy**:
*   **Server (Python/Flask):** Hosts the web interface and handles API requests to Google Cloud when online.
*   **Client (JavaScript/PWA):** Handles the UI and communicates with the *local* browser AI when offline or for privacy-first tasks.

---

## 🌐 1. Deploying the Backend (Online Mode)

Since this is a Python Flask app, you can deploy it to any standard platform.

### Recommended Platforms:
*   **Vercel:** (Requires `vercel.json` config)
*   **Render / Railway / Heroku:** (Requires `Procfile` or Docker)

### Environment Variables:
Make sure to set these in your deployment platform:
```env
FLASK_ENV=production
GOOGLE_API_KEY=your_actual_api_key_here
SECRET_KEY=your_secure_random_key
```

### Docker Deployment (Recommended for Production)
The project includes a `Dockerfile`. To build and run:
```bash
docker build -t gemini-chat .
docker run -p 3000:3000 gemini-chat
```

---

## ⚡ 2. Enabling Offline Mode (Chrome Built-in AI)

**Crucial:** You do NOT deploy "Chrome Canary" to the server. The *user* must have a compatible browser installed.

### Requirements for the User:
1.  **Browser:** Chrome Dev, Canary, or Chromium (v128+).
2.  **Flags:** The user must enable experimental flags.
3.  **Model:** The model (~1.7GB) is downloaded *locally* on the user's device.

### How it works in Production:
1.  User visits your deployed site (e.g., `https://your-gemini-app.com`).
2.  The **Service Worker** (`sw.js`) installs automatically, caching the HTML/CSS/JS.
3.  If the user goes **offline**, the PWA loads from cache.
4.  The app detects if `window.ai` is available.
    *   **If available:** Chats are processed locally on their device (0 latency, private).
    *   **If not available:** App waits for internet connection to use the Cloud API.

### Verifying Offline Capability:
We have included a setup page to guide your users:
*   **URL:** `https://your-app.com/chrome-ai-setup`
*   **Function:** Checks browser compatibility and guides the user to enable flags.

---

## 📦 3. PWA Checklist (Before Launch)

Ensure these files are served correctly to allow "Install to Home Screen":
*   [x] `manifest.json`: Defines app name, icons, and theme color.
*   [x] `sw.js`: Caches the app shell (HTML, CSS, JS).
*   [x] `HTTPS`: **Mandatory**. Service Workers and Chrome AI APIs *only* work on HTTPS (or localhost).

## 🔄 Hybrid Logic Flow

The updated `chrome-ai-complete.js` handles this automatically:

1.  **User sends message.**
2.  **Check 1:** Is `window.ai` (Chrome AI) initialized?
    *   ✅ YES: Generate response locally (Offline supported).
    *   ❌ NO: Proceed to Check 2.
3.  **Check 2:** Is the device Online?
    *   ✅ YES: Send request to Python Backend -> Google Gemini API.
    *   ❌ NO: Show error "Please connect to internet or set up Chrome AI".

---

## 📝 Summary for Hackathon Judges

> "This application features a **Resilient Hybrid Architecture**. It functions as a standard cloud-connected chatbot but progressively enhances itself on compatible devices to offer a fully offline, privacy-first local AI experience using Chrome's built-in Nano models."
