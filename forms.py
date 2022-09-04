from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField,DateField, FormField, FieldList, ValidationError, IntegerField
from wtforms.validators import InputRequired, Length, DataRequired, Email,EqualTo
from wtforms.fields import EmailField
import phonenumbers


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80), EqualTo('password_confirm', message='Passwords must match!')])
    password_confirm = PasswordField('Confirm Password', validators=[
                           InputRequired(), Length(min=4, max=15)])
        
            
class SymptomForm(FlaskForm):
    doctor = StringField('Name of Doctor', validators=[Length(min=0, max=1000)])
    fev = BooleanField('Fever')
    cough = BooleanField('Cough')
    fatigue = BooleanField('Fatigue')
    nausea = BooleanField('Nausea')
    headache = BooleanField('Headache')
    bodyaches = BooleanField('Body Aches')
    throat = BooleanField('Sore Throat')
    difficulty = BooleanField('Difficulty Breathing')
    extra = StringField('Any other symptoms not listed above?', validators=[Length(min=0, max=1000)])

class AccountForm(FlaskForm):
    firstname = StringField('First Name', validators=[
                           InputRequired()])
    lastname = StringField('Last Name', validators=[
                           InputRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    gender = SelectField('Gender', validators=[DataRequired()], choices=[('Male'),('Female'),('Transgender'),('Non-binary/non-conforming'),('Prefer not to respond')])
    PE = StringField('Pre Exisiting Conditions')
    DOB = DateField('DOB (YYYY-MM-DD)', validators=[InputRequired()])

class ContactEntry(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    contactemail = EmailField('Email', validators=[DataRequired(), Email()])

class ContactForm(FlaskForm):
    contactList = FieldList(FormField(ContactEntry), min_entries=1)
class ContactNumForm(FlaskForm):
    num = IntegerField('Number of Contacts:',validators=[
                           InputRequired()])

    