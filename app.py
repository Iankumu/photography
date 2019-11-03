import os
import uuid
from flask_change_password import flask_change_password, ChangePasswordForm, ChangePassword, SetPasswordForm
from flask_security import reset_password_instructions_sent, password_reset
from flask_mail import Mail
from comparison import image_comparison
import methods
from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wtforms import Form, PasswordField, validators, StringField, BooleanField, SubmitField
from wtforms.validators import InputRequired, ValidationError

UPLOAD_FOLDER = 'C:/Users/User/Documents/Strathmore/ICS/Academic Work/Year 2/Semester 2/IS Project/photography/static'
CLIENT_FOLDER = 'C:/Users/User/Documents/Strathmore/ICS/Academic Work/Year 2/Semester 2/IS Project/photography/static/Client_Uploads'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

# config MYSQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'photography'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# initialize MYSQL
mysql = MySQL(app)

# smtp
app.config['MAIL_SERVER'] = 'stmp.goolemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

mail = Mail(app)

# config image format
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CLIENT_FOLDER'] = CLIENT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

app.config['SECURITY_RECOVERABLE'] = True


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


# Registration Form Class
class RegistrationForm(Form):
    name = StringField('FullName', [validators.length(min=1, max=50)])
    username = StringField('UserName', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password does not match')
    ])
    confirm = PasswordField('Confirm Password')


# Login Form
class LoginForm(Form):
    emailLogin = StringField('Email', [validators.length(min=6, max=50)], validators=[InputRequired()])
    passwordLogin = PasswordField(validators.length(min=8, max=50), validators=[InputRequired()])
    remember = BooleanField('Remember Me')


# Update Form
class UpdateForm(Form):
    name = StringField('FullName')
    username = StringField('UserName')
    email = StringField('Email')


class RequestResetForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    submit = SubmitField('Request Password Reset')

    @staticmethod
    def validate_email(email):
        cur = mysql.connection.cursor()
        cur.execute('SELECT Email FROM users')
        id = cur.fetchall()
        for row in id:
            user = row['Email']
            if user == email:
                raise ValidationError('There is no account with that Email.. You must Register First')


class PasswordResetForm(Form):
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message='Password does not match')])
    confirmPassword = PasswordField('Confirm Password')
    submit = SubmitField('Reset Password')


# Registration


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
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

        # Get Email and Password
        result = cur.execute("SELECT * FROM users WHERE Email = %s", [email])
        if result > 0:
            # Get stored hash password
            data = cur.fetchone()
            password = data['Password']

            # Compare Passwords
            if check_password_hash(password, password_got):
                # Password matched
                session['Logged_in'] = True
                session['name'] = data['FullName']
                session['id'] = data['UserID']
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
    # Fetching the image paths from mysql
    if login:
        user = session['id']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM photos WHERE photographerid=%s", [user])

        rows = cur.fetchall()
        temp = []
        for row in rows:
            data = row['photo']
            date = row['date_posted']
            temp.append(data)
        mysql.connection.commit()
        cur.close()
        if not result:
            return render_template('dashboard.html')

    return render_template('dashboard.html', image_names=temp, date=date)


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now Logged out', 'success')
    return redirect(url_for('home'))


# uploading files
app.config["ALLOWED_EXTENSIONS"] = ['JPG']


# checks if a file is of the allowed extension
def allowed_file(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit('.', 1)[1]
    if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False


# renders the upload html page
@app.route('/uploads')
def upload_form():
    return render_template('uploads.html')


@app.route('/uploads', methods=['POST', 'GET'])
@is_logged_in
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files.getlist('file')[0]
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_name = file.filename
            flash("Image Uploaded Successfully", "success")

            # inserting file path to the database
            if login:
                user = session['id']
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO photos (photo,photographerid)VALUES (%s,%s)", [file_name, user])
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('dashboard'))

        else:
            flash('Allowed file types are .png, .jpg, .jpeg')
            return redirect(request.url)


@app.route('/client_uploads', methods=['POST', 'GET'])
def client_upload():
    if request.method == 'POST':
        # check if the post request has any files
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        # check if filename is empty
        if file.filename == '':
            flash('No file selected for uploading', 'danger')
            # render the form again
            return redirect(request.url)
        # check if the file type is allowed
        elif allowed_file(file.filename):
            # get the secure filename
            filename = secure_filename(file.filename)
            # get the file path
            file_path = os.path.join(app.config['CLIENT_FOLDER'], filename)
            # save file
            file.save(file_path)
            # initiate cursor
            cur = mysql.connection.cursor()
            # get all photos
            cur.execute("SELECT * FROM photos")
            # get all photos after ranking then
            photos = cur.fetchall()
            ranked_photos = image_comparison(file_path, photos)
            # map the photos with the photographer and return the photographer name ranked in order of average
            # return list of photographer objects structure {name,link )
            # return a page will all the ranked photos
            return render_template('Comparison.html', photos=ranked_photos, current_photo="Client_Uploads/" + filename)
        # warn user of invalid type
        else:
            flash('Invalid file type', 'danger')
            # render the form again
            return redirect(request.url)
    else:
        return render_template('Comparison.html')


@app.route('/edit', methods=['POST', 'GET'])
@is_logged_in
def edit():
    if login:
        userid = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM photos WHERE photographerid = %s', [userid])
        id = cur.fetchall()
        photos = []
        photoid = []
        for row in id:
            data = row['photoid']
            name = row['photo']
            photoid.append(data)
            photos.append(name)
        mysql.connection.commit()
        cur.close()
        allImages = dict(zip(photoid, photos))
        print(allImages)

        # os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return redirect('dashboard')


@app.route('/Reset_Password', methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if not is_logged_in(verify=True):
        form = RequestResetForm()
        if form.validate():
            email = request.form['Email']
            cur = mysql.connection.cursor()
            cur.execute("SELECT * From Users WHERE email =%s", [email])
            data = cur.fetchone()
            userid = data['UserID']
            user = methods.get_reset_token(userid=userid)
            print(email)
            methods.send_reset_email(user)
            flash('An Email has been sent with instructions to reset the password', 'info')
            return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/Reset_Password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if is_logged_in(verify=True):
        return redirect(url_for('dashboard'))

    if not is_logged_in():
        user = methods.verify(token)
        if user is None:
            flash('That is an invalid or expired token ', 'warning')
        return redirect(url_for('reset_request '))
    form = PasswordResetForm()
    if form.validate():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET Password = %s", [hashed_password])
        mysql.connection.commit()
        cur.close()
        flash('Your passsword has been updated', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    form = UpdateForm(request.form)
    if form.validate():
        username = form.username.data
        Fullname = form.name.data
        email = form.email.data
    if request.method == 'GET':
        if login:
            user = session['id']
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM users WHERE UserID=%s', [user])
            rows = cur.fetchall()
            for row in rows:
                uname = row['UserName']
                name = row['FullName']
                mail = row['Email']

                form.username.data = uname
                form.email.data = mail
                form.name.data = name
            mysql.connection.commit()
            cur.close()
    elif request.method == 'POST':
        if login:
            user = session['id']
            cur = mysql.connection.cursor()
            cur.execute('UPDATE users SET UserName=%s, FullName = %s, Email = %s WHERE UserID = %s',
                        [username, Fullname, email, user])
            mysql.connection.commit()
            cur.close()
        flash('Your account has been updated!', 'success')

        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)


# Server Startup
if __name__ == '__main__':
    # debug prevents the one from restarting each time you want to test it
    app.run(debug=True)
