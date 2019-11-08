import base64
from PIL import Image
from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore

from comparison import image_comparison
from config import Config
from database import db_session
from forms import RegistrationForm, PhotoUploadForm, ClientPhotoForm
from models import User, Role, Photo, Photographer, CurrentPhoto
from utils import photographer_required

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


@app.template_filter('render_image')
def render_image(binary_image):
    return base64.b64encode(binary_image).decode("utf-8")


# checks if a file is of the allowed extension
def allowed_file(filename):
    if "." not in filename:
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
@photographer_required
@app.route('/dashboard')
def dashboard():
    # get all the photos belonging to the photographer who is currently logged in
    photos = current_user.photographer.photos
    return render_template('dashboard.html', photos=photos)


# Show the photographer profile page
@login_required
@app.route('/photographer/profile/<username>')
def photographer_profile(username):
    # get user object from username
    user = User.query.filter_by(username=username).first()
    # get photos owned by the photographer
    photos = Photo.query.filter_by(photographer_id=user.photographer.id)
    return render_template('photographer_profile.html', user=user, photos=photos)


@login_required
@app.route('/photographer/uploads', methods=['POST', 'GET'])
def photographer_upload():
    # if request method is post
    if request.method == 'POST':
        form = PhotoUploadForm(name=request.form.get("name"), file=request.files.get("file"))
        if form.validate():
            # get the photographer id from the user
            # save the image and link to photographer
            image_file = form.file.data
            photo = Photo(
                name=form.name.data,
                photographer_id=current_user.photographer.id,
                file=image_file.read()
            )
            image = Image.open(image_file)
            file_type = image_file.headers.get("Content-Type")
            photo.add_image_data(*image.size, file_type)
            # save photo to db
            session_object = db_session()
            session_object.add(photo)
            session_object.commit()
            # success message
            flash("Image Uploaded Successfully", "success")
            return redirect(url_for('dashboard'))
        else:
            return render_template('photographer_uploads.html', form=form)
    # if the request is any other than get
    return render_template('photographer_uploads.html', form=PhotoUploadForm())


@login_required
@app.route('/upload', methods=['GET', 'POST'])
def client_upload():
    if request.method == "POST":
        # initialize form
        form = ClientPhotoForm(file=request.files.get("file"))
        # check if form is valid
        if form.validate():
            if not current_user.current_photo:
                # create a current photo linked to current user
                image_file = form.file.data
                current_photo = CurrentPhoto(
                    user_id=current_user.id,
                    file=image_file.read(),
                )
                image = Image.open(image_file)
                file_type = image_file.headers.get("Content-Type")
                current_photo.add_image_data(*image.size, file_type)
                # save to db
                db_session().add(current_photo)
                db_session().commit()

            # render the template
            flash("Upload Image  Successful", "success")
            return redirect("/find-photographer")
    # render the form
    return render_template('client_uploads.html', form=ClientPhotoForm())


@login_required
@app.route('/find-photographer', methods=['GET'])
def find_photographer():
    current_photo = current_user.current_photo
    photographers = []
    if current_photo:
        # get all the photos from database
        photos = Photo.query.all()
        # get all photos ranked
        ranked_photos = image_comparison(current_photo, photos)
        # create a dict of objects with items
        # "photographer_id":{photographer_object,euclidean average,number_of_photos}
        ranked_photographers = {}
        for photo in ranked_photos:
            image, euclidean_distance, photographer_id = photo
            # check if photographer id in ranked photographer to calculate the average
            if photographer_id in ranked_photographers:
                # get number of photos ranked
                number_of_photos = ranked_photographers.get(photographer_id).get("number_of_photos")
                # get the average of photographer
                average = ranked_photographers.get(photographer_id).get("euclidean_average")
                assert average
                # get the new average  after new photo consideration
                average = ((average * number_of_photos) + euclidean_distance) / (number_of_photos + 1)
                # get the new number of photos
                number_of_photos += 1
            # else create a new photographer object
            else:
                number_of_photos = 1
                average = euclidean_distance
            # update the dictionary with the object
            ranked_photographers.update({
                photographer_id: {
                    "photographer_id": photographer_id,
                    "photographer_object": Photographer.query.get(photographer_id),
                    "euclidean_average": average,
                    "number_of_photos": number_of_photos
                }}
            )
        # create a sortable list object to sort in order of euclidean distance
        photographers = sorted(ranked_photographers.values(), key=lambda item: item["euclidean_average"])
    return render_template('comparison.html', photographers=photographers,
                           current_photo=current_photo)


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
