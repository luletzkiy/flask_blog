import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask import Flask, redirect, jsonify, render_template, flash, url_for, request
from flask import Blueprint, after_this_request
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from app.auth import auth
from app.bookmarks import bookmarks
from app.blogposts import blogposts
from app.database import db, Bookmark, User, Blogpost
from flask_jwt_extended import JWTManager
from app.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from app.forms import UserForm, LoginForm, PostForm, SearchForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import get_jwt, unset_jwt_cookies, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_url_path='/static')
    #Улучшенный редактор текста
    ckeditor = CKEditor(app)

    

    #Общие настройки приложения
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY"),
            JWT_TOKEN_LOCATION = os.environ.get("JWT_TOKEN_LOCATION"),
            JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1),
            UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")
        )
    else:
        app.config.from_mapping(test_config)
    
    db.app = app
    db.init_app(app)

    JWTManager(app)

    #Настройки Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.context_processor
    def base():
        form = SearchForm()
        return dict(form=form)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    app.register_blueprint(blogposts)

    #Главная страница
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            user = True
        else:
            user = False
        return render_template('index.html', user=user)
    
    #Страница поиска
    @app.route('/search', methods=['POST'])
    def search():
        form = SearchForm()
        posts = Blogpost.query
        if form.validate_on_submit():
            post.searched = form.searched.data

            posts = posts.filter(Blogpost.content.like('%' + post.searched + '%'))
            posts = posts.order_by(Blogpost.name).all()

            return render_template("search.html", form=form, searched = post.searched, posts = posts)
    
    #Добавление постов
    @app.route('/add-post', methods=['GET', 'POST'])
    @login_required
    def add_post():
        form = PostForm()
        if current_user.is_authenticated:
            user = True
        else:
            user = False

        if form.validate_on_submit():
            poster = current_user.id

            if request.files['image']:
                image = request.files['image']
                pic_filename = secure_filename(image.filename)
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                file = form.image.data
            
            post = Blogpost(name=form.title.data, content=form.content.data, user_id=poster, image=pic_name)
               

            #Очищаем форму
            form.title.data = ''
            form.content.data = ''
            
            #Добавляем пост в базу данных
            db.session.add(post)
            db.session.commit()
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], pic_name))

            #Возвращаем сообщение
            flash("Blog Post Submitted Successfully!")
        
        return render_template("add_post.html", form=form, user=user)
    
    #Страница со всеми постами
    @app.route('/posts')
    def posts():
        if current_user.is_authenticated:
            user = True
        else:
            user = False
        posts = Blogpost.query.order_by(Blogpost.created_at)
        return render_template("posts.html", posts=posts, user=user)
    
    #Страница с отдельным постом
    @app.route('/posts/<int:id>')
    def post(id):
        post = Blogpost.query.get_or_404(id)
        return render_template('post.html', post=post)
    
    #Редактирование поста
    @app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_post(id):
        if current_user.is_authenticated:
            user = True
        else:
            user = False
        post = Blogpost.query.get_or_404(id)
        form = PostForm()
        if form.validate_on_submit():
            post.name = form.title.data
            post.content = form.content.data
            db.session.add(post)
            db.session.commit()
            flash("Пост успешно отредактирован!")
            return redirect(url_for('post', id=post.id))
        
        if current_user.id == post.user_id:
            form.title.data = post.name
            form.content.data = post.content
            return render_template('edit_post.html', form=form)
        else:
            flash("Вы не можете редактировать этот пост")
            posts = Blogpost.query.order_by(Blogpost.created_at)
            return render_template("posts.html", posts=posts, user=user)


    #Удаление поста    
    @app.route('/posts/delete/<int:id>')
    @login_required
    def delete_post(id):
        post_to_delete = Blogpost.query.get_or_404(id)
        id = current_user.id
        if id == post_to_delete.user_id:
            try:
                db.session.delete(post_to_delete)
                db.session.commit()

                flash("Пост успешно удалён!")

                posts = Blogpost.query.order_by(Blogpost.created_at)
                return render_template("posts.html", posts=posts)
            except:
                flash("Что-то пошло не так")

                posts = Blogpost.query.order_by(Blogpost.created_at)
                return render_template("posts.html", posts=posts)
        else:
            flash("Вы не можете удалить этот пост!")
            
            posts = Blogpost.query.order_by(Blogpost.created_at)
            return render_template("posts.html", posts=posts)
    
    


    
    #Регистрация
    @app.route('/register/', methods=['GET', 'POST'])
    def register():
        
        name = None
        form = UserForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                hashed_pw = generate_password_hash(form.password_hash.data)
                user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
                db.session.add(user)
                db.session.commit()
            form.username.data = ''
            form.email.data = ''
            form.password_hash.data = ''
            form.password_hash2.data = ''
            
            flash("Вы зарегистрированы!")
        if current_user.is_authenticated:
            user = True
        else:
            user = False
        return render_template('register.html', form = form, user=user)
    
    #Авторизация
    @app.route('/login/', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    flash("Неверный пароль!")
            else:
                flash("Такого пользователя не существует")
        if current_user.is_authenticated:
            user = True
        else:
            user = False
        return render_template('login.html', form=form, user=user)

    #Выход
    @app.route('/logout/', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    #Обработка коротких ссылок
    @app.get('/<short_url>')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        
        if bookmark:
            bookmark.visits = bookmark.visits + 1
            db.session.commit()

            return redirect(bookmark.url)
    
    #Обработка ошибок
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({
            'error': "Not found"
        }), HTTP_404_NOT_FOUND
    
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({
            'error': "Something went wrong, we are working on it"
        }), HTTP_500_INTERNAL_SERVER_ERROR


    return app
