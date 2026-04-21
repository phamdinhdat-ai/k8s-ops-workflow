# GitHub Setup Guide

Since GitHub CLI is not installed, use these steps:

## Option 1: Using Git with HTTPS

1. **Create repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `k8s-ops-workflow`
   - Make it Public or Private
   - Don't initialize with README
   - Click "Create repository"

2. **Get your GitHub username** (you'll need this)

3. **Add remote and push:**
```bash
cd /c/Users/Dat\ Pham/k8s-ops-workflow

# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/phamdinhdat-ai/k8s-ops-workflow.git
git branch -M main
git push -u origin main
```

4. **Authentication:**
   - Username: your GitHub username
   - Password: use a Personal Access Token (PAT)
   
   **Create PAT:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control)
   - Generate and copy the token
   - Use this token as password when pushing

## Option 2: Using SSH (Recommended)

1. **Check for existing SSH key:**
```bash
ls -la ~/.ssh
```

2. **Generate SSH key if needed:**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

3. **Add SSH key to GitHub:**
```bash
cat ~/.ssh/id_ed25519.pub
# Copy the output
```
   - Go to https://github.com/settings/keys
   - Click "New SSH key"
   - Paste your public key

4. **Push using SSH:**
```bash
git remote add origin git@github.com:YOUR_USERNAME/k8s-ops-workflow.git
git branch -M main
git push -u origin main
```

## Option 3: Install GitHub CLI

```bash
# Windows (using winget)
winget install --id GitHub.cli

# Or download from https://cli.github.com/
```

Then run:
```bash
gh auth login
gh repo create k8s-ops-workflow --public --source=. --push
```
