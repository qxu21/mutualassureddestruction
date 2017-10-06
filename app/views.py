from flask import render_template, flash, redirect, url_for, session, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, bcrypt
from .forms import LoginForm, RegisterForm
from .models import User #i think this imports from within the app

@app.route('/')
@app.route('/index')
def index():
    print('index page accessed')
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    #if g.user is not None and g.user.is_authenticated:
    #    return redirect(url_for('index')) #no double logins
    form=LoginForm()
    if form.validate_on_submit(): #so this is the backend processor, this'll be fun
        session['remember_me'] = form.remember_me.data
        
    return render_template('login.html',
            form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    #here goes nothin'
    print('beginning registration')
    form=RegisterForm()
    if form.validate_on_submit():
        print('form validated')
        #validate username
        #also validate email
        if User.query.filter_by(username=form.username.data).first():           
            #username was not unique, so bounce
            print('username or email not unique!')
            flash("This username already exists, pick a different one!")
            return redirect(url_for('register'))
        elif User.query.filter_by(email=form.email.data).first():
            #email not unique, bounce
            flash("This email is already in use!")
            return redirect(url_for('register'))
        else:
            print("user time!")
            print("Making user with username %s, email %s" % (form.username.data, form.email.data))
            newuser = User(username=form.username.data, email=form.email.data, password=bcrypt.generate_password_hash(form.password.data))
            db.session.add(newuser)
            db.session.commit()
            return redirect(url_for('index'))
    print("rendering form")
    return render_template('register.html', form=form)

#so this registers a user loader with flask-login
@lm.user_loader
def load_user(id):
    return User.query.get(int(id)) #convert to int from str
