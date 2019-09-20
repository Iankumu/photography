from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, PasswordField, validators, StringField, BooleanField, SubmitField, FileField
from wtforms.validators import Email, Length, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# config MYSQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'photography'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# initialize MYSQL
mysql = MySQL(app)

# config image format
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ["PNG", "JPG", "JPEG"]

# initialize mail SMTP
mail = Mail(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


# Registration Form Class


class RegisterForm(Form):
    name = StringField('FullName', [validators.length(min=1, max=50)])
    username = StringField('UserName', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password does not match'),
        validators.length(min=8, max=50)

    ])
    confirm = PasswordField('Confirm Password')


# Login Form
class LoginForm(Form):
    emailLogin = StringField('Email', [validators.length(min=6, max=50)], validators=[InputRequired()])
    passwordLogin = PasswordField(validators.length(min=8, max=50), validators=[InputRequired()])
    remember = BooleanField('Remember Me')


# Registration


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        # encrypting password
        hashed_password = generate_password_hash(form.password.data, method='sha256')

        # Creating Cursor

        cur = mysql.connection.cursor()
        # Execute Query
        cur.execute("INSERT INTO users(FullName, UserName, Email, Password) VALUES (%s, %s, %s, %s)",
                    (name, username, email, hashed_password))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('You Are Registered Successfully and you can now log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User Login


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        # Getting form fields
        email = request.form['email']
        password_got = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()
        # username = cur.execute("SELECT FullName FROM users WHERE Email = %s", [email])

        # Get Username and Password
        result = cur.execute("SELECT * FROM users WHERE Email = %s", [email])

        if result > 0:
            # Get stored hash password
            data = cur.fetchone()
            password = data['Password']

            # Compare Passwords
            if check_password_hash(password, password_got):
                # Password matched
                session['Logged_in'] = True
                session['Email'] = email

                flash('Login Successful', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
            return render_template('login.html', error=error)
            # Close Connection

        else:
            error = 'User Not Found'
            return render_template('login.html', error=error)
    return render_template('login.html')


# Check if user is logged in
def is_logged_in(verify):
    @wraps(verify)
    def wrap(*args, **kwargs):
        if 'Logged_in' in session:
            return verify(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now Logged Out', 'success')
    return redirect(url_for('home'))


# uploading files
@app.route('/uploads', methods=['POST', 'GET'])
def upload():
    if request.method == "POST":

        if request.files:
            image = request.files["image"]
            print(image)
            return redirect(request.url)
    return render_template('uploads.html')


# Server Startup


if __name__ == '__main__':
    # debug prevents the one from restarting each time you want to test it
    app.secret_key = 'secret123'
    app.run(debug=True)
