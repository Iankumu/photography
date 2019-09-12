from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from wtforms import Form, TextAreaField, PasswordField, validators, StringField

app = Flask(__name__)

# config MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'photography'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# initialize MYSQL

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


class RegisterForm(Form):
    name = StringField('FullName', [validators.length(min=1, max=50)])
    username = StringField('UserName', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password does not match')
    ])
    confirm = PasswordField('Confirm Password')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            name = form.name.data
            email = form.email.data
            username = form.username.data
            # encrypting password
            password = sha256_crypt.encrypt(str(form.username.data))


            # Creating Cursor

            cur = mysql.connection.cursor()
            # Execute Query
            cur.execute(
                "INSERT INTO users(FullName, UserName, Email, Password) VALUES (%s, %s, %s, %s)",
                (name, username, email, password))

            #Commit to DB
            mysql.connection.commit()

            #Close Connection
            cur.close()

            flash('You Are Registered Successfully and you can now log in', 'success')

            return redirect(url_for('login'))
        return render_template('register.html', form=form)


if __name__ == '__main__':
    # debug prevents the one from restarting each time you want to test it
    app.secret_key = 'secret123'
    app.run(debug=True)
