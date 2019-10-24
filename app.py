import os
import comparison
from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, session, request, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wtforms import Form, PasswordField, validators, StringField, BooleanField
from wtforms.validators import InputRequired

UPLOAD_FOLDER = '/root/PycharmProjects/photography/static/'
CLIENT_FOLDER = '/root/PycharmProjects/photography/static/Client_Uploads'
app = Flask(__name__)
app.secret_key = 'secret123'

# config MYSQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'photography'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# initialize MYSQL
mysql = MySQL(app)

# config image format
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CLIENT_FOLDER'] = CLIENT_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


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
    name = StringField('FullName', [validators.length(min=1, max=50)])
    username = StringField('UserName', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=35)])


class ForgotForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])


class PasswordResetForm(Form):
    current_password = PasswordField('Current Password', [validators.data_required(), validators.Length(min=4, max=80)])


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
app.config["ALLOWED_EXTENSIONS"] = ['PNG', 'JPG', 'JPEG']


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
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
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


@app.route('/client_uploads')
def Client_Upload():
    return render_template('Client_Uploads.html')


@app.route('/client_uploads', methods=['POST', 'GET'])
def client_upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['CLIENT_FOLDER'], filename))
            filepath = os.path.join(app.config['CLIENT_FOLDER'], filename)
            comparisons = comparison.image_comparison(filepath)
            images = []
            if comparisons:
                for i in comparisons:
                    full_list = i
                    new_filename = os.path.basename(full_list[0])
                    images.append(new_filename)
                    print(new_filename)

                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM photos WHERE photo = %s", [new_filename])
                    rows = cur.fetchall()
                    for row in rows:
                        data = row['photographerid']
                    mysql.connection.commit()
                    cur.close()

                    cur = mysql.connection.cursor()
                    cur.execute("SELECT * FROM users WHERE UserID = %s", [data])
                    rows = cur.fetchall()
                    name = []
                    for row in rows:
                        Fullname = row['FullName']
                        name.append(Fullname)
                        print(Fullname)
                    cur.close()

        return render_template('Comparison.html', image_names=Fullname, photo=images)


@app.route('/edit', methods=['POST', 'GET'])
@is_logged_in
def edit():
    if login:
        userid = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM photos WHERE photographerid = %s', [userid])
        id = cur.fetchall()
        photos = []
        for row in id:
            data = row['photoid']
            date = row['date_posted']
            name = row['photo']
            # photos.append(data)
            photos.append(name)

        print(photos)

        if edit:
            cur = mysql.connection.cursor()
            result = cur.execute('SELECT photoid FROM photos where photo= %s', [name])
            print(result)
            if photos:
                flash('SUCCESS', 'success')
            else:
                flash('FAILURE', 'danger')
            # os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return redirect('dashboard')


'''


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm(request.form)
    error = None
    message = None
    return render_template('forgot.html', form=form, error=error, message=message)


'''


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    form = UpdateForm(request.form)
    if request.method == 'POST' or request.method == 'GET' and form.validate():
        username = form.username.data
        Fullname = form.name.data
        email = form.email.data
        if request.method == 'GET':
            if login:
                user = session['id']
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM users WHERE UserID=%s", [user])

                rows = cur.fetchone()
                temp = []
                '''for row in rows:
                    data = row
                    temp.append(data)
                    print(temp)
                '''
                print(rows)
                mysql.connection.commit()
                cur.close()
        elif request.method == 'POST':
            if login:
                user = session['id']
                cur = mysql.connection.cursor()
                cur.execute('UPDATE users SET UserName =%s,FullName = %s, Email =%s WHERE UserID =%s)',
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
