from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json 
from flask_mail import Mail
import os
from werkzeug.utils import secure_filename
import math


print("welcome to app")
with open('config.json', 'r')as c:
    params = json.load(c) ["params"]
print(params)
local_server = True
app = Flask(__name__)
app.secret_key = 'this-is-the-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True
)
mail = Mail(app)

if(local_server):

    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),unique=False, nullable=False)
    email = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    phone_num = db.Column(db.String(100), nullable=False)
    msg = db.Column(db.String(120), unique=False, nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(40), nullable=False)
    subtitle = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    sub_heading = db.Column(db.String(30), nullable=True)
    content = db.Column(db.String(5000), nullable=False)
    img_file = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(6), nullable=True)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method=='POST':
        username = request.form.get('username')
        userpassword = request.form.get('password')

        if (username == params['admin_user'] and userpassword == params['admin_password']):
            # set the section variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
   
        else:
            return render_template("login.html", params=params)
    else:
        return render_template("login.html", params=params)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['noOfPost_onHomePage']))
    page = request.args.get('page')

    if (not str(page).isnumeric()):
        page = 1

    page =int(page)
    posts = posts[(page-1)*int(params['noOfPost_onHomePage']): (page-1)*int(params['noOfPost_onHomePage'])+int(params['noOfPost_onHomePage'])]
    
    # PAGINATION LOGIC
    if(page == 1):
        prev = "#"
        next = "/?page="+ str(page+1)

    elif(page == last):
        prev = "/?page="+ str(page-1)
        next = "#"

    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)

    return render_template("home.html", params=params, posts=posts, prev=prev, next=next)

@app.route("/about")
def about():
    return render_template("about.html", params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/add/<string:sno>", methods=['GET', 'POST'])
def add(sno):
    if ('user' in session and session['user'] == params['admin_user']):

        if request.method == 'POST':
            blog_sno = request.form.get('sno')
            blog_name = request.form.get('name')
            blog_title = request.form.get('title')
            blog_subtitle = request.form.get('subtitle')	
            blog_slug = request.form.get('slug')
            blog_sub_heading = request.form.get('sub_heading')
            blog_content = request.form.get('content')
            blog_img_file = request.form.get('img_file')
            blog_date = datetime.now()

            if sno == '0':
                post = Posts(sno=blog_sno, name=blog_name, title=blog_title, subtitle=blog_subtitle, slug=blog_slug, sub_heading=blog_sub_heading, content=blog_content, img_file=blog_img_file, date=blog_date)
                db.session.add(post)
                db.session.commit()

        return render_template('add.html', params=params, sno=sno)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:

        if request.method == 'POST':
            blog_sno = request.form.get('sno')
            blog_name = request.form.get('name')
            blog_title = request.form.get('title')
            blog_subtitle = request.form.get('subtitle')	
            blog_slug = request.form.get('slug')
            blog_sub_heading = request.form.get('sub_heading')
            blog_content = request.form.get('content')
            blog_img_file = request.form.get('img_file')
            blog_date = datetime.now()

            if sno == '0':
                post = Posts(sno=blog_sno, name=blog_name, title=blog_title, subtitle=blog_subtitle, slug=blog_slug, sub_heading=blog_sub_heading, content=blog_content, img_file=blog_img_file, date=blog_date)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.name = blog_name
                post.title = blog_title
                post.subtitle = blog_subtitle
                post.sub_heading = blog_sub_heading
                post.content = blog_content
                post.img_file = blog_img_file
                post.date = blog_date
                db.session.commit()
                return redirect('/edit/'+sno)
            
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)
    
@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:

        if(request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

            return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.pop('user')

    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):

    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()

    return redirect("/dashboard")

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method=='POST'):
      '''add entry to the data base'''
      name = request.form.get('name')
      email = request.form.get('email')
      phone = request.form.get('phone')
      message = request.form.get('message')

      entry = Contacts(name = name, email = email, date = datetime.now(), phone_num = phone, msg = message)

      db.session.add(entry)
      db.session.commit()
      mail.send_message(
          'New Message From ' + name,
           sender=email, recipients=[params['mail_username']],
           body = message + "\n" + phone
      )

    return render_template("contact.html", params=params)

app.run(debug=True)