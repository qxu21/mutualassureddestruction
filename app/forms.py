from flask_wtf import FlaskForm 
from wtforms import StringField, BooleanField, PasswordField, RadioField, IntegerField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, Length

def IsInteger():
    def _IsInteger(form, field):
        try:
            int(field.data)
        except:
            if field.data is not "":
                raise ValidationError("Integer needed!")

    return _IsInteger

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    username = StringField('username', validators=[DataRequired(),Length(max=30,message="Username must be at most 30 characters!")])
    password = PasswordField('password', validators=[DataRequired(),Length(min=8,message="Please choose a password longer than 8 characters!")])

class NewGameForm(FlaskForm):
    name = StringField('name')
    gametype = RadioField('type', choices=[
        ("beta","Beta"),
        ("standard","Standard")])
    nojoin = BooleanField('nojoin', default=False)

class JoinGameForm(FlaskForm):
    playername = StringField('name', validators=[DataRequired()])

class ComposeMessageForm(FlaskForm):
    dests = StringField('dests', validators=[DataRequired()]) #TODO: validate playernames
    body = TextAreaField('body')
    blind = BooleanField('blind', default=False)
