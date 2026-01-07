# Buy2Cash Backend API

FastAPI backend for Buy2Cash analytics dashboard.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB database
- (Optional) Supabase account
- (Optional) Azure OpenAI account

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python main.py
   # Or
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📋 Environment Variables

Create a `.env` file with the following variables:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB=your_database_name
SUPABASE_URL=your_supabase_url (optional)
SUPABASE_KEY=your_supabase_key (optional)
AZURE_KEY=your_azure_openai_key (optional)
AZURE_ENDPOINT=your_azure_openai_endpoint (optional)
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

## 🚢 Deployment

### Option 1: Using Deployment Script

```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Using Systemd Service

1. **Copy service file**
   ```bash
   sudo cp buy2cash-api.service /etc/systemd/system/
   ```

2. **Update paths in service file** (edit `/etc/systemd/system/buy2cash-api.service`)

3. **Enable and start service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable buy2cash-api
   sudo systemctl start buy2cash-api
   ```

4. **Check status**
   ```bash
   sudo systemctl status buy2cash-api
   ```

### Option 3: Using PM2

1. **Install PM2**
   ```bash
   npm install -g pm2
   ```

2. **Start application**
   ```bash
   pm2 start ecosystem.config.js
   ```

3. **Save PM2 configuration**
   ```bash
   pm2 save
   pm2 startup
   ```

## 🔄 CI/CD Setup

This repository is configured for GitHub Actions CI/CD. The workflow will:

1. Install dependencies
2. Run tests (if any)
3. Deploy to E2E server via SSH

### Required GitHub Secrets

Add these secrets in your GitHub repository settings:

- `E2E_HOST`: Your E2E server IP address
- `E2E_USERNAME`: SSH username
- `E2E_SSH_KEY`: Private SSH key for authentication
- `E2E_PORT`: SSH port (default: 22)

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Development

### Project Structure
```
backend/
├── api.py           # API routes and endpoints
├── database.py      # Database connection and configuration
├── service.py       # Business logic
├── main.py          # FastAPI application entry point
├── requirements.txt # Python dependencies
└── .env.example     # Environment variables template
```

## 📝 Logs

- Application logs: `app.log` (when using deploy.sh)
- Systemd logs: `sudo journalctl -u buy2cash-api -f`
- PM2 logs: `pm2 logs buy2cash-api`

## 🔧 Troubleshooting

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Database connection issues
- Verify MongoDB URI in `.env`
- Check network connectivity
- Verify MongoDB is running and accessible

### Permission denied
```bash
chmod +x deploy.sh
```

## 📞 Support

For issues or questions, please contact the development team.

