from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)

# 🔹 مسیر فولدر آپلود داخل static
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = '2982377731'

# 🔹 فایل JSON برای ذخیره پست‌ها
DATA_FILE = 'posts.json'
POSTS_FILE = "posts.json"

# 🔹 بارگذاری اولیه پست‌ها و اضافه کردن id در صورت نبود
if os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)
else:
    posts = {
        'letters': [],
        'future': [],
        'goals': [],
        'inspiration': [],
        'story': [],
        'ach': []
    }

for category, category_posts in posts.items():
    for idx, post in enumerate(category_posts, start=1):
        if 'id' not in post:
            post['id'] = idx

with open(POSTS_FILE, "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=4)

print("All posts now have 'id'!")

# 🔹 توابع کمکی
def load_posts():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_posts():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

# 🏷️ Routes

# صفحه اصلی
@app.route('/')
def home():
    return render_template('index.html')

# صفحه about
@app.route('/about')
def about():
    return render_template('about.html')

# صفحه letters
@app.route('/letters')
def letters():
    page_posts = posts['letters']
    return render_template('letters.html', posts=page_posts)

# صفحه future
@app.route('/future')
def future():
    page_posts = posts['future']
    return render_template('future.html', posts=page_posts)

# صفحه goals
@app.route('/goals')
def goals():
    page_posts = posts['goals']
    return render_template('goals.html', posts=page_posts)

# صفحه inspiration
@app.route('/inspiration')
def inspiration():
    page_posts = posts['inspiration']
    return render_template('inspiritions.html', posts=page_posts)

# صفحه vision
@app.route('/vision')
def vision():
    return render_template('vision_board.html')

# صفحه ach
# نمایش پست‌های ach
@app.route('/ach')
def ach():
    posts = load_posts()          # فایل JSON رو بخون
    page_posts = posts.get('ach', [])  # از get استفاده کن که هیچ اروری نده
    return render_template('ach.html', posts=page_posts)

# صفحه story
@app.route('/story')
def story():
    page_posts = posts['story']
    return render_template('future_story.html', posts=page_posts)

# صفحه admin اصلی
@app.route('/admin_main')
def admin_main():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template('admin_main.html')

# صفحه admin panel
@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template('login.html') + '<h1 style="color:pink; font-size:200px; text-shadow:12px 12px 15px darkred;">Welcome!</h1>'

# نمایش همه پست‌ها برای admin
@app.route("/admin_posts")
def admin_posts():
    posts = load_posts()
    return render_template("admin_posts.html", posts=posts)

# اضافه کردن پست
# اضافه کردن پست
@app.route('/add_posts', methods=['GET', 'POST'])
def add_posts():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        page = request.form.get('page')
        file = request.files.get('file')
        filename = None

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        global posts
        posts = load_posts()

        if posts[page]:
            new_id = max([p.get('id', 0) for p in posts[page]]) + 1
        else:
            new_id = 1

        posts[page].append({
            'id': new_id,
            'title': title,
            'content': content,
            'file': filename
        })

        save_posts()

        return render_template('login.html') + '<h1 style="color:pink; font-size:200px; text-shadow:12px 12px 15px darkred;">Post Added!</h1>'

    return render_template('add_p.html')


@app.route("/posts/<category>/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(category, post_id):
    global posts
    posts = load_posts()

    post = next((p for p in posts.get(category, []) if p['id'] == post_id), None)
    if not post:
        return "Post not found", 404

    if request.method == "POST":
        post['title'] = request.form.get("title")
        post['content'] = request.form.get("content")
        save_posts()
        return redirect(url_for("admin_posts"))

    return render_template("edit.html", category=category, post=post)

# حذف پست
@app.route("/posts/<category>/<int:post_id>/delete", methods=["POST"])
def delete_post(category, post_id):
    global posts
    posts = load_posts()
    posts[category] = [p for p in posts.get(category, []) if p['id'] != post_id]
    save_posts()
    return redirect(url_for("admin_posts"))

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username', '').strip()
        pas = request.form.get('password', '').strip()

        if user == 'BMW' and pas == 'BMW':
            session['admin'] = True
            return redirect(url_for('admin_main'))
        else:
            return render_template('login.html') + '<h1 style="color:pink; font-size:150px; text-shadow:12px 12px 15px darkred;">Wrong Password or Username!</h1>'
    return render_template('login_m.html')

# logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# اجرای برنامه
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
