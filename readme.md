# Название: 
Блог на Flask

# Описание: 
Небольшой блог на фреймворке Flask
Сейчас реализовано: 
- регистрация пользователей, 
- авторизация пользователей
- создание, редактирование и удаление постов
- добавление изображение к постам

Для того чтобы запустить сайт, нужно создать виртульное окружение и установить все зависимости указанные в requirements.txt, после чего из папки Blog_website запустить команду flask run

# Инструкция по пользованию сайтом:
- Для регистрации перейдите по ссылке "Регистрация" в навигационном меню и введите данные для регистрации
- Для авторизации перейдите по ссылке "Войти" в навигационном меню и введите данные которые вводили при регистрации
- Для того чтобы разместить пост на сайте перейдите по ссылке "Разместить пост" в навигационном меню
- Далее введите название поста и содержание, по желанию прикрепите картинку
- Для просмотра всех существующих постов перейдите по ссылке "Посты" в навигационном меню

# Для обращение к API используйте ссылку с api/v1/ в конце (например https://momentous-exciting-name.glitch.me/api/v1/blogposts), на данный момент с помощью API можно:
- получить список всех постов по ссылке api/v1/blogposts
- создать новый пост с помощью ссылки api/v1/create (отправить в json name, название, и content, содержание поста)
- получить отдельный пост по ссылке api/v1/blogposts/get/id(вместо id подставляется номер поста)
- отредактировать существующий пост с помощью ссылки api/v1/edit/id(вместо id подставляется номер поста, отправить в json name, название, и content, содержание поста)
- удалить существующий пост с помощью ссылки api/v1/delete/id(вместо id подставляется номер поста)
- зарегистрировать пользователя по ссылке api/v1/auth/register (отправить в json username, email и password, то есть имя пользователя, эл. почту и пароль соответсвенно)
- получить свой jwt access token для авторизации с помощью api/v1/auth/login

# Технологии в проекте: 
Проект написан на Flask c использованием SqlAlchemy. Так же потребуется библиотека flask-login. В реализации API используется также flask-jwt-extended.
Генерация страниц с использованием условных операторов и циклов.

# Техническое описание проекта: 
проект предлагается в **исходном коде**. 
**Исходный код** состоит из:
- точки входа __init__.py
- модели базы данных database.py
- реализации API blogposts.py, auth.py и bookmarks.py
- файла с формами Flask forms.py
- а также шаблонов страниц в папке templates