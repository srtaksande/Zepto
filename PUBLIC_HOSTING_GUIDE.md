# Guide: Hosting Zomato App Publicly with Public IP

This guide covers multiple methods to make your Flask Zomato app accessible from the internet.

## ⚠️ Important Security Notes

- The Flask development server (`app.run()`) is **NOT suitable for production** use
- It's only for testing and development
- For production, use a proper WSGI server like Gunicorn or uWSGI with a reverse proxy (Nginx)
- Always use HTTPS in production
- Change the SECRET_KEY in `app.py` (line 17) to a secure random value

---

## Method 1: Direct Public IP Access (On Your Local Network)

### Step 1: Find Your Public IP Address

**On Windows (PowerShell/CMD):**
```bash
curl ifconfig.me
# OR
curl icanhazip.com
# OR
curl ipinfo.io/ip
```

**Alternative:** Visit https://whatismyipaddress.com/ in your browser

### Step 2: Configure Windows Firewall

1. Open **Windows Defender Firewall** (search in Start menu)
2. Click **"Advanced settings"** on the left
3. Click **"Inbound Rules"** → **"New Rule"**
4. Select **"Port"** → Next
5. Select **"TCP"** and enter port **5000** → Next
6. Select **"Allow the connection"** → Next
7. Check all profiles (Domain, Private, Public) → Next
8. Name it "Flask App Port 5000" → Finish

### Step 3: Configure Router Port Forwarding (If Behind Router)

If you're behind a router (most home networks), you need to forward port 5000:

1. Find your router's admin IP (usually `192.168.1.1` or `192.168.0.1`)
2. Log into router admin panel
3. Go to **Port Forwarding** or **Virtual Server** settings
4. Add rule:
   - **External Port:** 5000
   - **Internal IP:** Your local IP (run `ipconfig` in CMD to find it, look for IPv4 Address)
   - **Internal Port:** 5000
   - **Protocol:** TCP
   - **Save** the rule

### Step 4: Run the App

```bash
cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
python app.py
```

### Step 5: Access the App

- **Locally:** `http://localhost:5000` or `http://127.0.0.1:5000`
- **From other devices on your network:** `http://YOUR_LOCAL_IP:5000` (e.g., `http://192.168.1.100:5000`)
- **From internet:** `http://YOUR_PUBLIC_IP:5000` (e.g., `http://123.45.67.89:5000`)

### Finding Your Local IP (for network access):
```bash
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

---

## Method 2: Using ngrok (Easiest - Recommended for Testing)

**ngrok** creates a secure tunnel to your local app - perfect for testing without firewall/router configuration.

### Step 1: Install ngrok

1. Download from: https://ngrok.com/download
2. Extract `ngrok.exe` to a folder (or add to PATH)
3. Sign up for free account at https://ngrok.com/
4. Get your authtoken from dashboard

### Step 2: Authenticate ngrok

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### Step 3: Run Your Flask App

```bash
cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
python app.py
```

### Step 4: Create Tunnel (in a new terminal)

```bash
ngrok http 5000
```

You'll get output like:
```
Forwarding  https://abc123xyz.ngrok-free.app -> http://localhost:5000
```

### Step 5: Access Your App

Use the HTTPS URL provided by ngrok (e.g., `https://abc123xyz.ngrok-free.app`)

**Advantages:**
- ✅ No firewall/router configuration needed
- ✅ HTTPS automatically provided
- ✅ Works immediately
- ✅ Free tier available

**Limitations:**
- ⚠️ Free tier has session time limits
- ⚠️ URL changes each time (unless paid plan)
- ⚠️ For development/testing only

---

## Method 3: Cloud Platform Deployment (Production-Ready)

For production, deploy to cloud platforms:

### Option A: Render.com (Free Tier Available)

1. Push code to GitHub
2. Sign up at https://render.com
3. Create new **Web Service**
4. Connect your GitHub repo
5. Settings:
   - **Build Command:** `pip install -r requirements.txt && flask --app app init-db`
   - **Start Command:** `gunicorn app:app`
6. Add `gunicorn` to requirements.txt:
   ```
   Flask==3.0.3
   Flask-SQLAlchemy==3.1.1
   gunicorn==21.2.0
   ```
7. Deploy!

### Option B: Railway.app

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. In project folder: `railway init`
4. Deploy: `railway up`

### Option C: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Deploy using Heroku CLI

### Option D: PythonAnywhere

1. Sign up at https://www.pythonanywhere.com
2. Upload files via web interface
3. Configure web app
4. Free tier available

---

## Method 4: VPS/Server Deployment (Advanced)

For a dedicated server:

1. **Set up VPS** (DigitalOcean, AWS EC2, Linode, etc.)
2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```
3. **Clone/deploy your app**
4. **Use Gunicorn + Nginx:**
   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:8000 app:app
   ```
5. **Configure Nginx** as reverse proxy
6. **Set up SSL** with Let's Encrypt (certbot)

---

## Quick Start Commands Summary

### For Local Network Access:
```bash
# 1. Navigate to project
cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"

# 2. Run app (already configured with host='0.0.0.0')
python app.py

# 3. Find your IP
ipconfig  # Local network IP
curl ifconfig.me  # Public IP

# 4. Access from other devices
# http://YOUR_LOCAL_IP:5000 (local network)
# http://YOUR_PUBLIC_IP:5000 (internet, requires port forwarding)
```

### For ngrok (Easiest Testing):
```bash
# Terminal 1: Run Flask app
python app.py

# Terminal 2: Create tunnel
ngrok http 5000
# Use the provided HTTPS URL
```

---

## Troubleshooting

### Can't access from other devices?
- ✅ Check Windows Firewall allows port 5000
- ✅ Verify app is running with `host='0.0.0.0'`
- ✅ Check router port forwarding (if accessing from internet)
- ✅ Ensure device is on same network (for local access)

### Port already in use?
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# OR change port in app.py:
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Security warning?
- The Flask dev server has security vulnerabilities
- Never use `debug=True` in production
- Use Gunicorn + Nginx for production deployments

---

## Recommended Approach

- **For Testing:** Use **ngrok** (Method 2) - quickest and easiest
- **For Production:** Use **Render.com** or **Railway** (Method 3) - fully managed
- **For Learning:** Try **Direct IP** (Method 1) to understand networking

