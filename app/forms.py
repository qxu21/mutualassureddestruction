from flask_wtf import FlaskForm 
from wtforms import StringField, BooleanField, PasswordField, RadioField, IntegerField, ValidationError
from wtforms.validators import DataRequired, Email

def IsInteger():
    def _IsInteger(form, field):
        try:
            int(field.data)
        except:
            if field.data is not "":
                raise ValidationError("Please input integers in fields!")

    return _IsInteger

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class NewGameForm(FlaskForm):
    name = StringField('name')
    gametype = RadioField('type', choices=[
        ("beta","Beta"),
        ("standard","Standard")])
    nojoin = BooleanField('nojoin', default=False)

class JoinGameForm(FlaskForm):
    playername = StringField('name', validators=[DataRequired()])
