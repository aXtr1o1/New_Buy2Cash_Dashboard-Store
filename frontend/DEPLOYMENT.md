# Deploying Frontend to Vercel

## Prerequisites
1. A GitHub/GitLab/Bitbucket account with your code pushed
2. A Vercel account (sign up at https://vercel.com)

## Step-by-Step Deployment

### Method 1: Vercel Dashboard (Recommended)

1. **Push your code to Git**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Go to Vercel Dashboard**
   - Visit https://vercel.com
   - Sign in with your GitHub/GitLab/Bitbucket account

3. **Import Project**
   - Click "Add New Project"
   - Select your repository
   - Choose the repository containing your frontend code

4. **Configure Project Settings**
   - **Root Directory**: If your frontend is in a subfolder, set it to `frontend`
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build` (or `cd frontend && npm run build` if deploying from root)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (or `cd frontend && npm install` if deploying from root)

5. **Set Environment Variables**
   - Click "Environment Variables"
   - Add the following:
     - **Name**: `NEXT_PUBLIC_API_BASE`
     - **Value**: Your backend API URL (e.g., `https://your-backend-api.com`)
     - **Environment**: Production, Preview, Development (select all)

6. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete
   - Your site will be live at `https://your-project.vercel.app`

### Method 2: Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

4. **Deploy**
   ```bash
   vercel
   ```
   - Follow the prompts
   - When asked for settings, use defaults (Next.js will be auto-detected)

5. **Set Environment Variables**
   ```bash
   vercel env add NEXT_PUBLIC_API_BASE
   ```
   - Enter your backend API URL when prompted
   - Select environments: Production, Preview, Development

6. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Environment Variables

Make sure to set these in Vercel Dashboard → Settings → Environment Variables:

- `NEXT_PUBLIC_API_BASE`: Your backend API URL (e.g., `https://api.yourdomain.com`)

## Important Notes

1. **CORS Configuration**: Make sure your backend allows requests from your Vercel domain
2. **API URL**: Update `NEXT_PUBLIC_API_BASE` with your production backend URL
3. **Store ID**: The `STORE_ID` is currently hardcoded in `api.ts`. Consider making it an environment variable if needed

## Troubleshooting

- **Build Errors**: Check the build logs in Vercel dashboard
- **API Connection Issues**: Verify `NEXT_PUBLIC_API_BASE` is set correctly
- **CORS Errors**: Update your backend CORS settings to allow your Vercel domain

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

