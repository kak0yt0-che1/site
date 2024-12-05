from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from validate_email_address import validate_email

# Настройка Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

# Главная страница
@app.route('/')
def index():
    ads = Ad.query.all()
    return render_template('index.html', ads=ads)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Проверка корректности почты
        if not validate_email(email):
            flash('Пожалуйста, введите корректный адрес электронной почты.', 'danger')
            return render_template('register.html')

        # Проверяем, есть ли пользователь с таким email или именем
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято.', 'danger')
        else:
            # Добавляем пользователя
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash('Вы уже вошли в систему.', 'info')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                session['user_id'] = user.id
                flash('Вы успешно вошли!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Неверный пароль. Попробуйте снова.', 'danger')
        else:
            flash('Пользователь с таким email не найден. Зарегистрируйтесь.', 'warning')
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Войдите, чтобы получить доступ.', 'warning')
        return redirect(url_for('login'))
    
    user_ads = Ad.query.filter_by(user_id=session['user_id']).all()
    print("Объявления пользователя:", user_ads)
    return render_template('dashboard.html', ads=user_ads)





# Добавление объявления
@app.route('/add', methods=['GET', 'POST'])
def add_ad():
    if 'user_id' not in session:
        flash('Войдите, чтобы добавить объявление.', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        contact = request.form['contact']
        photo = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file.filename != '':
                photo = secure_filename(photo_file.filename)
                photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo))
        ad = Ad(title=title, description=description, contact=contact, photo=photo, user_id=session['user_id'])
        db.session.add(ad)
        db.session.commit()

        # Отладка
        print(f"Новое объявление: ID: {ad.id}, Title: {ad.title}, User ID: {ad.user_id}")
        
        flash('Объявление успешно добавлено!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add.html')


# Выход
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


@app.route('/delete_ad/<int:ad_id>', methods=['POST'])
def delete_ad(ad_id):
    if 'user_id' not in session:
        flash('Войдите, чтобы получить доступ.', 'warning')
        return redirect(url_for('login'))
    
    ad = Ad.query.get_or_404(ad_id)
    print(f"Попытка удалить объявление ID: {ad.id}, User ID: {ad.user_id}")
    
    if ad.user_id != session['user_id']:
        flash('Вы не можете удалить это объявление.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(ad)
    db.session.commit()
    flash('Объявление успешно удалено!', 'success')
    return redirect(url_for('dashboard'))


    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Используем порт из переменной окружения или 5000 по умолчанию
    app.run(host='0.0.0.0', port=port) 