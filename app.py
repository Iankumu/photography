from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore

from comparison import image_comparison
from config import Config
from database import db_session
from forms import RegistrationForm, PhotoUploadForm, ClientPhotoForm
from models import User, Role, Photo, Photographer

app = Flask(__name__)
# set up the configurations
app.config.from_object(Config)
# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore, register_form=RegistrationForm)
# Set Up the Email
mail = Mail()
mail.init_app(app)
login_manager = LoginManager()


# checks if a file is of the allowed extension
def allowed_file(filename):
    if not "." in filename:
        return False
    ext = filename.split('.', 1)[1]
    if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False


# renders the home page
@app.route('/')
def home():
    return render_template('home.html')


# renders the about page
@app.route('/about')
def about():
    return render_template('about.html')


# renders the users profile page

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    # get a current user object
    user = current_user
    # render a profile page of the user
    return render_template('profile.html', user=user)


# renders the users profile page
@app.route('/photographer/register', methods=['GET', 'POST'])
def photographer_register():
    if request.method == "POST":
        # check if the current user has photographer linked to him or her
        if not current_user.photographer:
            # create a photographer with the current user id
            photographer = Photographer(user_id=current_user.id)
            # save to db
            db_session().add(photographer)
            db_session().commit()
            flash("You are now registered as a Photographer.Welcome {}".format(current_user.first_name))
        # show error message and redirect to dashboard
        flash("You are now registered as a photographer")
        return redirect('/dashboard')
    # render the photographer register template
    return render_template('photographer_register.html')


# Show the dashboard of a photographer
@login_required
@app.route('/dashboard')
def dashboard():
    # get all the photos belonging to the photographer
    photos = Photo.query.filter_by(photographer_id=current_user.id)
    return render_template('dashboard.html', photos=photos)


# Show the photographer profile page
@login_required
@app.route('/photographer/profile/<username>')
def photographer_profile(username):
    # get user object from username
    user = User.query.get(username=username)
    # get photos owned by the photographer
    photos = Photo.query.filter_by(photographer_id=user.photographer.id)
    return render_template('photographer_profile.html', user=user, photos=photos)


@login_required
@app.route('/photographer/uploads', methods=['POST', 'GET'])
def photographer_upload():
    # if request method is post
    if request.method == 'POST':
        form = PhotoUploadForm(request.form)
        if form.validate():
            # get the photographer id from the user
            # save the image and link to photographer
            photo = Photo(
                name=form.name.data,
                photographer_id=current_user.photographer.id,
                file=form.file.data.read()
            )
            # save photo to db
            db_session().add(photo)
            db_session().commit()
            # success message
            flash("Image Uploaded Successfully", "success")
            return redirect(url_for('dashboard'))
        else:
            flash('Allowed file types are .png, .jpg, .jpeg')
            return redirect(request.url)
    # if the request is any other than get
    return render_template('photographer_uploads.html')


@login_required
@app.route('/upload', methods=['GET'])
def client_upload():
    # initialize form
    form = ClientPhotoForm(request.form)
    # check if form is valid
    if form.validate() and allowed_file(form.file.data.filename):
        # store the current image in
        session["current_image"] = form.file.data.read()
        # get all the photos from database
        photos = Photo.query.all()
        # get all photos ranked
        ranked_photos = image_comparison(session["current_image"], photos)
        return render_template('comparison.html', photos=ranked_photos, current_photo="Client_Uploads/" + filename)
    else:
        return render_template('comparison.html')


# as a photographer edit a photo
@login_required
@app.route('/edit/<photo_id>', methods=['POST', 'GET'])
def edit(photo_id):
    if request.method == "GET":
        # show the edit photo page
        return redirect('dashboard')
    if request.method == "POST":
        # save the edited images
        pass


# Server Startup
if __name__ == '__main__':
    # debug prevents the one from restarting each time you want to test it
    app.run(debug=True)
