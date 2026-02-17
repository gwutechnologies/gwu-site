"""
GWU Technologies - Full Stack Web Application
Backend: Python Flask + SQLite
"""
import os, sqlite3, hashlib, json, smtplib, secrets
from datetime import datetime
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import (Flask, render_template, request, redirect, url_for,
                   session, jsonify, flash, g)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'gwu.db')

# ─── DATABASE ────────────────────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        interest TEXT,
        message TEXT NOT NULL,
        ip_address TEXT,
        status TEXT DEFAULT 'unread',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        excerpt TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'Company',
        emoji TEXT DEFAULT '📰',
        theme TEXT DEFAULT 'dark1',
        published INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )''')

    # Default admin: admin / GWU@2026
    pw = hashlib.sha256('GWU@2026'.encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO admin (id,username,password_hash) VALUES (1,?,?)',
              ('admin', pw))

    # Seed news if empty
    c.execute('SELECT COUNT(*) FROM news')
    if c.fetchone()[0] == 0:
        seed = [
            ('GWU Technologies Achieves Udyam MSME Registration',
             'udyam-msme-registration',
             'Officially recognised as a Micro Enterprise (UDYAM-TN-03-0309835) under India\'s MSME framework, opening access to government schemes.',
             '<p>GWU Technologies is proud to announce its official registration as a Micro Enterprise under the Udyam Registration system with registration number <strong>UDYAM-TN-03-0309835</strong>.</p><p>This milestone opens access to government schemes, institutional partnerships, and priority sector lending for our growing AI startup.</p><p>The registration was completed on February 11, 2026 and marks our formal recognition as part of India\'s MSME ecosystem.</p>',
             'Milestone', '🏛️', 'dark1', 1, '2026-02-11 09:00:00', '2026-02-11 09:00:00'),
            ('AI Inspector Platform Begins Commercial Operations',
             'ai-inspector-launch',
             'Our flagship human-in-the-loop inspection platform is live. Industries can now train, test, and deploy custom defect detection models entirely self-serve.',
             '<p>We are excited to announce the commercial launch of <strong>AI Inspector</strong> — GWU Technologies\' flagship AI-powered inspection platform.</p><p>AI Inspector is the first self-serve inspection platform where industrial users can train their own defect detection models, validate performance in real-time, and deploy confidently — all without writing a single line of code.</p><h3>Key Highlights:</h3><ul><li>Train custom models with your own labelled images</li><li>Real-time live testing on production line feeds</li><li>One-click model deployment to edge devices</li><li>Human-in-the-loop feedback for continuous improvement</li></ul><p>Contact us to schedule a demo!</p>',
             'Product Launch', '🚀', 'red', 1, '2026-02-08 10:00:00', '2026-02-08 10:00:00'),
            ('GWU Technologies Incorporated at SRIT Incubation Centre',
             'company-incorporation',
             'The company was officially incorporated at Sri Ramakrishna Institute of Technology\'s SISH Incubation Centre, Coimbatore — our launch pad for transforming industrial AI.',
             '<p>GWU Technologies was officially incorporated on <strong>January 26, 2026</strong> at the SISH Incubation Centre, Sri Ramakrishna Institute of Technology, Coimbatore.</p><p>Founded by R Immanual with a core team of passionate technologists, GWU Technologies aims to democratize AI-powered quality inspection for industries across India.</p><p>Our motto — <strong>Love, Wisdom, Service</strong> — guides everything we build: software that cares about its users, intelligence born from deep expertise, and an unwavering commitment to our clients\' success.</p>',
             'Company', '🏢', 'dark2', 1, '2026-01-26 09:00:00', '2026-01-26 09:00:00'),
        ]
        c.executemany('INSERT INTO news (title,slug,excerpt,content,category,emoji,theme,published,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)', seed)

    conn.commit()
    conn.close()

# ─── AUTH ─────────────────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

# ─── PUBLIC ROUTES ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    db = get_db()
    news = db.execute('SELECT * FROM news WHERE published=1 ORDER BY created_at DESC LIMIT 3').fetchall()
    return render_template('index.html', news=news)

@app.route('/news')
def news_list():
    db = get_db()
    news = db.execute('SELECT * FROM news WHERE published=1 ORDER BY created_at DESC').fetchall()
    return render_template('news_list.html', news=news)

@app.route('/news/<slug>')
def news_detail(slug):
    db = get_db()
    article = db.execute('SELECT * FROM news WHERE slug=? AND published=1', (slug,)).fetchone()
    if not article:
        return redirect(url_for('news_list'))
    related = db.execute('SELECT * FROM news WHERE published=1 AND id!=? ORDER BY created_at DESC LIMIT 2', (article['id'],)).fetchall()
    return render_template('news_detail.html', article=article, related=related)

@app.route('/contact', methods=['POST'])
def contact_submit():
    data = request.get_json() or request.form
    first_name = str(data.get('first_name', '')).strip()
    last_name  = str(data.get('last_name', '')).strip()
    email      = str(data.get('email', '')).strip()
    interest   = str(data.get('interest', '')).strip()
    message    = str(data.get('message', '')).strip()

    # Basic validation
    if not all([first_name, email, message]):
        return jsonify({'success': False, 'error': 'Please fill in all required fields.'}), 400
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'error': 'Please enter a valid email address.'}), 400
    if len(message) < 10:
        return jsonify({'success': False, 'error': 'Message is too short.'}), 400

    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    db = get_db()
    db.execute('''INSERT INTO contacts (first_name,last_name,email,interest,message,ip_address)
                  VALUES (?,?,?,?,?,?)''',
               (first_name, last_name, email, interest, message, ip))
    db.commit()

    # Try to send email notification
    try:
        send_notification_email(first_name, last_name, email, interest, message)
    except Exception as e:
        pass  # Don't fail submission if email fails

    return jsonify({'success': True, 'message': f'Thank you {first_name}! We\'ll be in touch within 24 hours.'})

def send_notification_email(fname, lname, email, interest, message):
    """Send email notification to GWU admin"""
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASS = os.getenv('SMTP_PASS', '')
    TO_EMAIL  = os.getenv('NOTIFY_EMAIL', 'immangwu@gmail.com')

    if not SMTP_USER or not SMTP_PASS:
        return  # Skip if not configured

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'[GWU Website] New Contact: {fname} {lname} — {interest}'
    msg['From']    = SMTP_USER
    msg['To']      = TO_EMAIL

    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
      <div style="background:#C8102E;padding:24px;border-radius:8px 8px 0 0">
        <h2 style="color:white;margin:0">New Contact Form Submission</h2>
        <p style="color:rgba(255,255,255,0.7);margin:4px 0 0">GWU Technologies Website</p>
      </div>
      <div style="background:#f9f9f9;padding:24px;border:1px solid #e5e5e5">
        <table style="width:100%;border-collapse:collapse">
          <tr><td style="padding:8px 0;color:#666;width:130px">Name</td><td style="padding:8px 0;font-weight:600;color:#1a1a1a">{fname} {lname}</td></tr>
          <tr><td style="padding:8px 0;color:#666">Email</td><td style="padding:8px 0;font-weight:600;color:#C8102E">{email}</td></tr>
          <tr><td style="padding:8px 0;color:#666">Interest</td><td style="padding:8px 0;color:#1a1a1a">{interest or 'Not specified'}</td></tr>
          <tr><td style="padding:8px 0;color:#666;vertical-align:top">Message</td><td style="padding:8px 0;color:#1a1a1a;line-height:1.6">{message}</td></tr>
        </table>
      </div>
      <div style="background:#1a1a1a;padding:16px;border-radius:0 0 8px 8px;text-align:center">
        <p style="color:rgba(255,255,255,0.4);font-size:12px;margin:0">© 2026 GWU Technologies · Love · Wisdom · Service</p>
      </div>
    </div>
    """
    msg.attach(MIMEText(html_body, 'html'))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())

# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    messages  = db.execute('SELECT * FROM contacts ORDER BY created_at DESC LIMIT 20').fetchall()
    news      = db.execute('SELECT * FROM news ORDER BY created_at DESC').fetchall()
    unread    = db.execute('SELECT COUNT(*) FROM contacts WHERE status="unread"').fetchone()[0]
    total_msg = db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    total_news= db.execute('SELECT COUNT(*) FROM news').fetchone()[0]
    return render_template('admin/dashboard.html',
                           messages=messages, news=news,
                           unread=unread, total_msg=total_msg, total_news=total_news)

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        pw_hash  = hashlib.sha256(password.encode()).hexdigest()
        db = get_db()
        admin = db.execute('SELECT * FROM admin WHERE username=? AND password_hash=?',
                           (username, pw_hash)).fetchone()
        if admin:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials. Try admin / GWU@2026')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/message/<int:mid>/read', methods=['POST'])
@admin_required
def mark_read(mid):
    db = get_db()
    db.execute('UPDATE contacts SET status="read" WHERE id=?', (mid,))
    db.commit()
    return jsonify({'success': True})

@app.route('/admin/message/<int:mid>/delete', methods=['POST'])
@admin_required
def delete_message(mid):
    db = get_db()
    db.execute('DELETE FROM contacts WHERE id=?', (mid,))
    db.commit()
    return jsonify({'success': True})

# News CRUD
@app.route('/admin/news/new', methods=['GET','POST'])
@admin_required
def admin_news_new():
    if request.method == 'POST':
        title    = request.form.get('title','').strip()
        excerpt  = request.form.get('excerpt','').strip()
        content  = request.form.get('content','').strip()
        category = request.form.get('category','Company')
        emoji    = request.form.get('emoji','📰')
        theme    = request.form.get('theme','dark1')
        published= 1 if request.form.get('published') else 0
        slug     = slugify(title)

        db = get_db()
        # ensure unique slug
        base, i = slug, 1
        while db.execute('SELECT id FROM news WHERE slug=?',(slug,)).fetchone():
            slug = f'{base}-{i}'; i += 1
        db.execute('''INSERT INTO news (title,slug,excerpt,content,category,emoji,theme,published)
                      VALUES (?,?,?,?,?,?,?,?)''',
                   (title, slug, excerpt, content, category, emoji, theme, published))
        db.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/news_form.html', article=None, action='New')

@app.route('/admin/news/<int:nid>/edit', methods=['GET','POST'])
@admin_required
def admin_news_edit(nid):
    db = get_db()
    article = db.execute('SELECT * FROM news WHERE id=?',(nid,)).fetchone()
    if not article:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        title    = request.form.get('title','').strip()
        excerpt  = request.form.get('excerpt','').strip()
        content  = request.form.get('content','').strip()
        category = request.form.get('category','Company')
        emoji    = request.form.get('emoji','📰')
        theme    = request.form.get('theme','dark1')
        published= 1 if request.form.get('published') else 0
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute('''UPDATE news SET title=?,excerpt=?,content=?,category=?,emoji=?,
                      theme=?,published=?,updated_at=? WHERE id=?''',
                   (title, excerpt, content, category, emoji, theme, published, now, nid))
        db.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/news_form.html', article=article, action='Edit')

@app.route('/admin/news/<int:nid>/delete', methods=['POST'])
@admin_required
def admin_news_delete(nid):
    db = get_db()
    db.execute('DELETE FROM news WHERE id=?',(nid,))
    db.commit()
    return jsonify({'success': True})

@app.route('/admin/news/<int:nid>/toggle', methods=['POST'])
@admin_required
def admin_news_toggle(nid):
    db = get_db()
    article = db.execute('SELECT published FROM news WHERE id=?',(nid,)).fetchone()
    if article:
        new_val = 0 if article['published'] else 1
        db.execute('UPDATE news SET published=? WHERE id=?',(new_val, nid))
        db.commit()
        return jsonify({'success': True, 'published': new_val})
    return jsonify({'success': False}), 404

@app.route('/admin/change-password', methods=['POST'])
@admin_required
def change_password():
    current = request.form.get('current_password','')
    new_pw  = request.form.get('new_password','')
    confirm = request.form.get('confirm_password','')
    if new_pw != confirm:
        flash('Passwords do not match')
        return redirect(url_for('admin_dashboard'))
    curr_hash = hashlib.sha256(current.encode()).hexdigest()
    new_hash  = hashlib.sha256(new_pw.encode()).hexdigest()
    db = get_db()
    result = db.execute('UPDATE admin SET password_hash=? WHERE username=? AND password_hash=?',
                        (new_hash, session['admin_user'], curr_hash))
    db.commit()
    if result.rowcount:
        flash('Password changed successfully!')
    else:
        flash('Current password is incorrect')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    print('\n' + '='*55)
    print('  GWU Technologies Server Starting...')
    print('  Website  → http://localhost:5000')
    print('  Admin    → http://localhost:5000/admin')
    print('  Login    → admin / GWU@2026')
    print('='*55 + '\n')
    app.run(debug=True, host='0.0.0.0', port=5000)
