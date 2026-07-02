# GWU Technologies – Full Stack Website

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your SMTP email credentials

# 3. Run the server
python app.py
```

## Access

| URL | Description |
|-----|-------------|
| http://localhost:5000 | Public website |
| http://localhost:5000/news | All news articles |
| http://localhost:5000/admin | Admin dashboard |

## Admin Login
- **Username:** `admin`
- **Password:** `GWU@2026`
- Change your password after first login!

## How to Add News Articles
1. Go to http://localhost:5000/admin
2. Click **"+ New Article"**
3. Fill in: Title, Category, Emoji, Excerpt, Full Content
4. Click **"New Article →"**
5. It instantly appears on your website!

## How Contact Messages Reach You

### Option A – Email (Recommended)
1. Open `.env` file
2. Set your Gmail SMTP credentials:
   - Go to myaccount.google.com
   - Security → 2-Step Verification → App Passwords
   - Create a password for "Mail"
   - Paste it as `SMTP_PASS`
3. Every contact form submission will email you at `immangwu@gmail.com`

### Option B – Admin Dashboard
- Visit http://localhost:5000/admin
- All messages are saved to the database
- Click 📧 next to any message to reply directly

## Project Structure
```
gwu-fullstack/
├── app.py              ← Main server (Flask backend)
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment variables template
├── data/
│   └── gwu.db          ← SQLite database (auto-created)
├── templates/
│   ├── base.html       ← Base layout
│   ├── index.html      ← Homepage
│   ├── news_list.html  ← All news
│   ├── news_detail.html← Single article
│   ├── partials/
│   │   ├── nav.html
│   │   └── footer.html
│   └── admin/
│       ├── login.html
│       ├── dashboard.html
│       └── news_form.html
└── static/
    ├── css/main.css    ← All styles
    └── js/main.js      ← Animations + contact form
```

## Deploying to Production
For free hosting, try **Railway.app** or **Render.com**:
1. Push code to GitHub
2. Connect Railway/Render to your GitHub repo
3. Set environment variables in the dashboard
4. Deploy!
