# Direct Upsun Git Deployment Guide

## Add Upsun Remote
```bash
git remote add upsun ihnoolfr@git.upsun.com:ihnoolfr.git
```

## Deploy Directly
```bash
git push upsun main
```

## Check Remotes
```bash
git remote -v
```

Should show:
- origin: GitHub repository 
- upsun: Direct Upsun deployment
- trackfutura-oct: Old repository

## Auto-deploy Setup
1. Console: https://console.upsun.com/projects/inhoolfrqniuu
2. Settings → Integrations
3. Add GitHub integration for automatic deploys