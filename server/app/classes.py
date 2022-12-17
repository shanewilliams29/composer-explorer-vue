from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.validators import Length, ValidationError, DataRequired
from wtforms import StringField, SubmitField, RadioField, FileField
from app.models import User


class Unique(object):
    def __init__(self, model, field, message=u'This name is already taken.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check and current_user.display_name != field.data:
            raise ValidationError(self.message)


class ChangeAvatar(FlaskForm):
    choice = RadioField('Select an option:', choices=[('remove', 'Remove photo'), ('restore', 'Restore Spotify photo'), ('upload', 'Upload image')], default='upload')
    link = StringField('Option 1: Paste URL to image', description='Must be a .jpg or .png file smaller than 5 MB.', validators=[Length(min=0, max=2064)])
    file = FileField('Option 2: Upload an image from device', description='Must be a .jpg or .png file smaller than 5 MB.', validators=[Length(min=0, max=2064)])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=0, max=64), Unique(User, User.display_name)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
