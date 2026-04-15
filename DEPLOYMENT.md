# Food Waste Optimization - Deployment Guide

## 🔧 Recent Fixes Applied

### Issues Fixed:
1. **404 Error Handler** - Fixed WSGI request conversion in `api/index.py`
2. **Deprecated Flask Hooks** - Replaced `@app.before_first_request` with `@app.before_request`
3. **Route Configuration** - Updated `vercel.json` for proper serverless routing
4. **Dependencies** - Updated to Flask 3.0.0 and compatible versions
5. **Database Initialization** - Improved database initialization with safety checks

### Files Changed:
- ✅ `api/index.py` - Completely rewritten for proper Vercel handler
- ✅ `app.py` - Fixed Flask initialization
- ✅ `vercel.json` - Optimized routing configuration
- ✅ `requirements.txt` - Updated dependencies
- ✅ `.gitignore` - Added for cleaner deployments

## 📋 Deployment Steps

### 1. **Local Testing** (Optional but Recommended)
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test locally
python app.py
# Visit http://localhost:5000
```

### 2. **Deploy to Vercel**

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI (if not already done)
npm install -g vercel

# Deploy from project root
vercel

# Follow the prompts and select appropriate options
# Select Python runtime
# Let Vercel detect the settings from vercel.json
```

#### Option B: Using GitHub Integration
1. Push your code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Vercel will auto-detect the Python framework
6. Click "Deploy"

### 3. **Verify Deployment**
```bash
# Test health endpoint
curl https://your-project.vercel.app/health

# Should return: OK
```

## 🗂️ Project Structure for Vercel

```
food_waste_optimization/
├── api/
│   ├── __init__.py          (NEW)
│   └── index.py             (FIXED)
├── templates/
│   ├── base.html
│   ├── index.html
│   └── ... (other HTML files)
├── static/
│   ├── style.css
│   └── ... (other static files)
├── app.py                   (FIXED)
├── vercel.json              (FIXED)
├── requirements.txt         (UPDATED)
├── runtime.txt
├── .gitignore               (NEW)
└── DEPLOYMENT.md           (THIS FILE)
```

## ⚙️ Configuration Details

### Environment Variables
If needed, add these in Vercel dashboard under project settings:

```
DATABASE_PATH=/tmp/food.db    # Vercel uses /tmp for temp storage
```

### Vercel.json Routing
- All requests → `api/index.py` handler
- Static files served through Flask
- Database path: `/tmp/food.db` (auto-configured)

## 🐛 Troubleshooting

### Still Getting 404?
1. Check that all files are pushed to repository
2. Verify `vercel.json` is in root directory
3. Ensure `api/index.py` exists and has the handler function
4. Check Vercel Function logs for detailed errors

### Database Not Persisting?
- Vercel's `/tmp` is ephemeral (resets per deployment)
- For persistent storage, connect to an external database:
  - MongoDB
  - PostgreSQL
  - Firebase Realtime Database

### Static Files Not Loading?
1. Flask is configured to serve from `/static/` folder
2. All CSS, JS, images should be in `static/` directory
3. Check browser console for 404 on static assets

## 📊 Performance Tips

1. **Database**: Consider migrating to a cloud database for better performance
2. **Caching**: Add Redis for session management
3. **CDN**: Vercel automatically uses Edge Network for static content

## 🔒 Security Notes

1. Change `app.secret_key` from "secret" to a strong random string
2. Add HTTPS (Vercel provides this automatically)
3. Consider adding authentication middleware
4. Store sensitive data in environment variables

## 📞 Support Resources

- [Vercel Python Runtime Docs](https://vercel.com/docs/runtimes/python)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Vercel CLI Documentation](https://vercel.com/cli)

---

**Last Updated**: April 2026
**Status**: ✅ Ready for Deployment
