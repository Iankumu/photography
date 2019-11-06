import inspect

from flask import request, flash
from flask_security.forms import password_length, password_required, email_validator, email_required
from flask_security.utils import validate_redirect_url, get_message, text_type, string_types, _datastore
from markupsafe import Markup
from wtforms import FileField, validators, PasswordField, HiddenField, SubmitField, Field
from wtforms.validators import EqualTo, ValidationError
from wtforms.widgets import HiddenInput
from wtforms_alchemy import Form
from wtforms_alchemy.fields import StringField
from wtforms_alchemy.validators import Unique
from wtforms_components import ModelForm

from models import User


class BaseModelForm(ModelForm):
    def validate_on_submit(self):
        return (True if request.method in ('POST', 'PUT', 'PATCH', 'DELETE') else False) and self.validate()

    def hidden_tag(self, *fields):
        """Render the form's hidden fields in one call.

        A field is considered hidden if it uses the
        :class:`~wtforms.widgets.HiddenInput` widget.

        If ``fields`` are given, only render the given fields that
        are hidden.  If a string is passed, render the field with that
        name if it exists.

        .. versionchanged:: 0.13

           No longer wraps inputs in hidden div.
           This is valid HTML 5.

        .. versionchanged:: 0.13

           Skip passed fields that aren't hidden.
           Skip passed names that don't exist.
        """

        def hidden_fields(fields):
            for f in fields:
                if isinstance(f, string_types):
                    f = getattr(self, f, None)

                if f is None or not isinstance(f.widget, HiddenInput):
                    continue

                yield f

        return Markup(
            u'\n'.join(text_type(f) for f in hidden_fields(fields or self))
        )

    def to_dict(self):
        def is_field_and_user_attr(member):
            return isinstance(member, Field) and \
                   hasattr(_datastore.user_model, member.name)

        fields = inspect.getmembers(self, is_field_and_user_attr)
        return dict((key, value.data) for key, value in fields)


class RegistrationForm(BaseModelForm):
    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = request.args.get('next', '')

    first_name = StringField('First Name', [validators.length(min=2, max=50)])
    second_name = StringField('Last Name', [validators.length(min=2, max=50)])
    phone_number = StringField('Phone', [validators.length(min=10, max=18), Unique(User.phone_number)])
    username = StringField('Username', [validators.length(min=6, max=30), Unique(User.username)])
    email = StringField("Email", validators=[email_required, email_validator, Unique(User.email)])

    password = PasswordField("Password", validators=[password_required, password_length])

    password_confirm = PasswordField("Retype Password",
                                     validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
                                                 password_required])

    next = HiddenField()
    submit = SubmitField('Register')

    def validate_next(self, field):
        if field.data and not validate_redirect_url(field.data):
            field.data = ''
            flash(*get_message('INVALID_REDIRECT'))
            raise ValidationError(get_message('INVALID_REDIRECT')[0])


class PhotoUploadForm(Form):
    name = StringField('first_name', [validators.length(min=2, max=100)])
    file = FileField("Photo", [validators.required])


class ClientPhotoForm(Form):
    file = FileField("Photo", [validators.required])
