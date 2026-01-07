# CI/CD Setup Guide for E2E Deployment

This guide will help you set up automated deployment from GitHub to your E2E server.

## 📋 Prerequisites

1. ✅ E2E server instance created
2. ✅ SSH access to the server
3. ✅ GitHub repository with your code
4. ✅ Git installed on your local machine

## 🚀 Step-by-Step Setup

### 1. Initial Server Setup

**SSH into your E2E server:**
```bash
ssh username@your-e2e-server-ip
```

**Run the setup script:**
```bash
# Clone your repository first
cd /opt
sudo mkdir -p buy2cash
sudo chown -R $USER:$USER /opt/buy2cash
cd /opt/buy2cash
git clone <your-github-repo-url> .

# Run setup
cd backend
chmod +x setup-server.sh
./setup-server.sh
```

**Configure environment variables:**
```bash
nano /opt/buy2cash/backend/.env
# Add your MongoDB URI, Supabase keys, etc.
```

### 2. Generate SSH Key for GitHub Actions

**On your E2E server, generate an SSH key:**
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
# Press Enter to accept default location (no passphrase for CI/CD)
```

**Add public key to authorized_keys:**
```bash
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
```

**Copy the private key:**
```bash
cat ~/.ssh/github_actions
# Copy this entire output - you'll need it for GitHub Secrets
```

### 3. Configure GitHub Secrets

**Go to your GitHub repository:**
1. Navigate to: `Settings` → `Secrets and variables` → `Actions`
2. Click `New repository secret`
3. Add the following secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `E2E_HOST` | `your-server-ip` | Your E2E server IP address |
| `E2E_USERNAME` | `your-username` | SSH username for E2E server |
| `E2E_SSH_KEY` | `(paste private key)` | Private SSH key from step 2 |
| `E2E_PORT` | `22` | SSH port (default: 22) |

### 4. Update GitHub Workflow (if needed)

**Check the workflow file:** `.github/workflows/deploy-backend.yml`

**Update the deployment path if different:**
```yaml
script: |
  cd /opt/buy2cash  # Change this if your path is different
  git pull origin production
  # ... rest of the script
```

### 5. Test the Deployment

**Make a small change and push to production branch:**
```bash
git add .
git commit -m "Test CI/CD deployment"
git push origin production
```

**⚠️ Important:** CI/CD only triggers on pushes to the `production` branch, not `main`. This ensures only production-ready code gets deployed.

**Check GitHub Actions:**
1. Go to your repository on GitHub
2. Click `Actions` tab
3. Watch the workflow run
4. Check for any errors

**Verify on server:**
```bash
ssh username@your-e2e-server-ip
sudo systemctl status buy2cash-api
# Or check logs
tail -f /opt/buy2cash/backend/app.log
```

## 🔧 Manual Deployment (Alternative)

If CI/CD is not working, you can deploy manually:

```bash
# SSH into server
ssh username@your-e2e-server-ip

# Navigate to project
cd /opt/buy2cash

# Pull latest changes
git pull origin production

# Deploy
cd backend
./deploy.sh
```

## 📊 Monitoring

### Check Application Status

**Systemd:**
```bash
sudo systemctl status buy2cash-api
sudo journalctl -u buy2cash-api -f  # Follow logs
```

**PM2:**
```bash
pm2 status
pm2 logs buy2cash-api
```

**Direct logs:**
```bash
tail -f /opt/buy2cash/backend/app.log
```

### Restart Application

**Systemd:**
```bash
sudo systemctl restart buy2cash-api
```

**PM2:**
```bash
pm2 restart buy2cash-api
```

**Manual:**
```bash
cd /opt/buy2cash/backend
./deploy.sh
```

## 🔒 Security Best Practices

1. **Use SSH keys** instead of passwords
2. **Restrict SSH access** to specific IPs (if possible)
3. **Keep dependencies updated**: `pip install -r requirements.txt --upgrade`
4. **Use environment variables** for sensitive data
5. **Regular backups** of your database
6. **Monitor logs** for suspicious activity

## 🐛 Troubleshooting

### CI/CD Not Triggering
- Check if workflow file is in `.github/workflows/` directory
- Verify you're pushing to the `production` branch (CI/CD only triggers on `production`)
- Check GitHub Actions tab for errors

### Deployment Fails
- Verify SSH key is correct in GitHub Secrets
- Check server connectivity: `ssh -i ~/.ssh/github_actions username@host`
- Review GitHub Actions logs for specific errors

### Application Not Starting
- Check `.env` file exists and has correct values
- Verify MongoDB connection
- Check logs: `tail -f app.log`
- Verify port 8000 is not in use: `lsof -i :8000`

### Permission Denied
```bash
chmod +x deploy.sh setup-server.sh
sudo chown -R $USER:$USER /opt/buy2cash
```

## 📞 Support

For issues:
1. Check application logs
2. Review GitHub Actions logs
3. Verify environment variables
4. Test database connectivity

---

**Next Steps:**
1. ✅ Complete server setup
2. ✅ Configure GitHub Secrets
3. ✅ Test deployment
4. ✅ Set up monitoring
5. ✅ Configure domain (if needed)

