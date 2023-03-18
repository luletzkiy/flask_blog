from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

class UserForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Пароль', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Подвердите пароль', validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")

class LoginForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")

class PostForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    content = CKEditorField('Содержание', validators=[DataRequired()])
    image = FileField("Изображение")
    submit = SubmitField("Разместить")

class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")