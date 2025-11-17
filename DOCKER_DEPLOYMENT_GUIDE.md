# Docker Deployment Guide for Zomato App

This guide covers deploying your Zomato Flask app using Docker to make it publicly accessible.

---

## 📋 Prerequisites

1. **Docker Desktop** installed on your machine
   - Download: https://www.docker.com/products/docker-desktop/
   - For Windows: Install Docker Desktop for Windows

2. **Git** (optional, for version control)
3. **Account on a cloud platform** (for public deployment)

---

## 🏃 Quick Start: Local Docker Deployment

### Step 1: Build the Docker Image

```bash
cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
docker build -t zomato-app .
```

### Step 2: Run the Container

**Option A: Using Docker directly:**
```bash
docker run -d -p 5000:5000 --name zomato-app -v ./instance:/app/instance zomato-app
```

**Option B: Using Docker Compose (Recommended):**
```bash
docker-compose up -d
```

### Step 3: Access the App

Open your browser and go to: `http://localhost:5000`

### Step 4: Stop the Container

```bash
# Using Docker directly
docker stop zomato-app
docker rm zomato-app

# Using Docker Compose
docker-compose down
```

---

## 🌐 Public Deployment Options

### Option 1: Railway.app (Easiest - Recommended)

Railway automatically detects Dockerfiles and deploys your app.

#### Steps:

1. **Install Railway CLI** (optional, or use web interface):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize and Deploy**:
   ```bash
   cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
   railway init
   railway up
   ```

4. **Or use Web Interface**:
   - Go to https://railway.app
   - Sign up/login
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Connect your GitHub repository
   - Railway automatically detects `Dockerfile` and deploys
   - Get your public URL from the dashboard

**Advantages:**
- ✅ Free tier available ($5 credit/month)
- ✅ Automatic HTTPS
- ✅ Auto-detects Dockerfile
- ✅ Easy database management
- ✅ Environment variables support

---

### Option 2: Render.com

Render supports Docker deployments with automatic HTTPS.

#### Steps:

1. **Push your code to GitHub** (if not already)

2. **Create Render Account**:
   - Go to https://render.com
   - Sign up/login

3. **Create New Web Service**:
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select the `Zomato` repository

4. **Configure Deployment**:
   - **Name:** zomato-app (or your choice)
   - **Environment:** Docker
   - **Build Command:** (leave empty - Render uses Dockerfile)
   - **Start Command:** (leave empty - defined in Dockerfile)
   - **Instance Type:** Free tier available

5. **Environment Variables** (Optional):
   - Add `FLASK_ENV=production`
   - Add `SECRET_KEY=<your-secret-key>` (generate a secure one)

6. **Deploy**:
   - Click **"Create Web Service"**
   - Render builds and deploys automatically
   - Get your public URL (e.g., `https://zomato-app.onrender.com`)

**Advantages:**
- ✅ Free tier (may spin down after inactivity)
- ✅ Automatic HTTPS
- ✅ Easy setup
- ✅ Automatic deployments on git push

---

### Option 3: Fly.io

Fly.io offers global deployment with edge computing.

#### Steps:

1. **Install Fly CLI**:
   ```bash
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login to Fly**:
   ```bash
   fly auth login
   ```

3. **Create Fly App**:
   ```bash
   cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
   fly launch
   ```
   - Follow prompts (name, region, etc.)
   - Fly detects Dockerfile automatically

4. **Deploy**:
   ```bash
   fly deploy
   ```

5. **Get Public URL**:
   ```bash
   fly open
   ```

**Advantages:**
- ✅ Generous free tier
- ✅ Global edge deployment
- ✅ Fast deployments
- ✅ Built-in HTTPS

---

### Option 4: DigitalOcean App Platform

#### Steps:

1. **Create DigitalOcean Account**: https://www.digitalocean.com

2. **Create App**:
   - Go to App Platform
   - Click **"Create App"**
   - Connect GitHub repository
   - Select repository and branch

3. **Configure**:
   - **Source:** Dockerfile (auto-detected)
   - **Plan:** Basic ($5/month minimum, or free trial)

4. **Deploy**:
   - Review settings
   - Click **"Launch App"**
   - Get your public URL

---

### Option 5: AWS (Advanced)

For AWS deployment, you can use:

- **AWS Elastic Beanstalk** (easiest)
- **AWS ECS/Fargate** (more control)
- **AWS App Runner** (serverless containers)

#### Using AWS Elastic Beanstalk:

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**:
   ```bash
   cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
   eb init -p docker zomato-app
   ```

3. **Create Environment**:
   ```bash
   eb create zomato-env
   ```

4. **Deploy**:
   ```bash
   eb deploy
   ```

5. **Open**:
   ```bash
   eb open
   ```

---

### Option 6: Google Cloud Run

#### Steps:

1. **Install Google Cloud SDK**: https://cloud.google.com/sdk/docs/install

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Build and Deploy**:
   ```bash
   cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
   gcloud run deploy zomato-app --source . --platform managed --region us-central1
   ```

4. **Access**: Get URL from output

---

### Option 7: Azure Container Instances

#### Steps:

1. **Install Azure CLI**: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

2. **Login**:
   ```bash
   az login
   ```

3. **Create Resource Group**:
   ```bash
   az group create --name zomato-rg --location eastus
   ```

4. **Deploy Container**:
   ```bash
   az container create \
     --resource-group zomato-rg \
     --name zomato-app \
     --image zomato-app:latest \
     --dns-name-label zomato-app \
     --ports 5000
   ```

---

## 🔧 Docker Commands Reference

### Build Image
```bash
docker build -t zomato-app .
```

### Run Container
```bash
docker run -d -p 5000:5000 --name zomato-app zomato-app
```

### View Running Containers
```bash
docker ps
```

### View Container Logs
```bash
docker logs zomato-app
# Or follow logs
docker logs -f zomato-app
```

### Stop Container
```bash
docker stop zomato-app
```

### Remove Container
```bash
docker rm zomato-app
```

### Remove Image
```bash
docker rmi zomato-app
```

### Execute Commands in Running Container
```bash
docker exec -it zomato-app bash
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

---

## 🔐 Security Best Practices

### 1. Change Secret Key

Before deploying, update `SECRET_KEY` in `app.py`:

```python
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'your-super-secret-key-here')
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Use Environment Variables

Create `.env` file (don't commit to git):
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///zomato_clone.db
```

Update Dockerfile to use environment variables:
```dockerfile
ENV SECRET_KEY=${SECRET_KEY}
```

### 3. Production Database

For production, consider using PostgreSQL instead of SQLite:
- Add `psycopg2-binary` to requirements.txt
- Update database URI in app.py
- Use managed database (e.g., Railway Postgres, Render Postgres)

---

## 📝 Files Created

1. **Dockerfile** - Defines the container image
2. **.dockerignore** - Excludes unnecessary files from build
3. **docker-compose.yml** - Simplifies container management
4. **requirements.txt** - Updated with gunicorn for production

---

## 🚀 Recommended Deployment Flow

1. **Local Testing**:
   ```bash
   docker build -t zomato-app .
   docker-compose up
   # Test at http://localhost:5000
   ```

2. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Add Docker support"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

3. **Deploy to Railway/Render**:
   - Connect GitHub repository
   - Auto-deploy on push

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Container Won't Start
```bash
# Check logs
docker logs zomato-app

# Check if image built successfully
docker images | grep zomato-app
```

### Database Not Persisting
Ensure volume is mounted:
```yaml
volumes:
  - ./instance:/app/instance
```

### Build Errors
```bash
# Clear Docker cache
docker builder prune

# Rebuild without cache
docker build --no-cache -t zomato-app .
```

---

## 📊 Platform Comparison

| Platform | Free Tier | HTTPS | Auto-Deploy | Ease of Use | Best For |
|----------|-----------|-------|-------------|-------------|----------|
| **Railway** | ✅ $5/month credit | ✅ | ✅ | ⭐⭐⭐⭐⭐ | Quick deployment |
| **Render** | ✅ (may sleep) | ✅ | ✅ | ⭐⭐⭐⭐⭐ | Simple projects |
| **Fly.io** | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ | Global deployment |
| **DigitalOcean** | ❌ ($5/min) | ✅ | ✅ | ⭐⭐⭐⭐ | Production apps |
| **AWS** | ❌ (free tier complex) | ✅ | ✅ | ⭐⭐⭐ | Enterprise |
| **Google Cloud** | ✅ (free credits) | ✅ | ✅ | ⭐⭐⭐ | Google ecosystem |
| **Azure** | ✅ (free credits) | ✅ | ✅ | ⭐⭐⭐ | Microsoft ecosystem |

---

## 🎯 Quick Deployment Checklist

- [ ] Docker installed
- [ ] Dockerfile created
- [ ] .dockerignore created
- [ ] requirements.txt includes gunicorn
- [ ] SECRET_KEY updated
- [ ] Code pushed to GitHub (if using cloud platforms)
- [ ] Cloud platform account created
- [ ] Environment variables configured
- [ ] Application deployed and accessible

---

## 💡 Tips

1. **Use Docker Compose** for local development - easier management
2. **Start with Railway or Render** - simplest for beginners
3. **Monitor logs** during first deployment to catch errors
4. **Use environment variables** for configuration
5. **Set up CI/CD** for automatic deployments on git push
6. **Backup database** regularly (especially SQLite)
7. **Use managed databases** for production (PostgreSQL)

---

For local testing or specific platform issues, refer to the platform's official documentation.

