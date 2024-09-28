from email.policy import default
from click import confirm
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import (BooleanField, MultipleFileField,
                                   PasswordField)
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError

from src import app


class TokenForm(FlaskForm):
    token = StringField("Authentication token: ", validators=[
                        Length(min=30, max=30, message="Incorrect token")])
    submit = SubmitField("Send")


class CreateShipmentForm(FlaskForm):
    driver = SelectField('Select driver', validators=[
                         DataRequired(message='Invalid input')])
    car = SelectField('Select car', validators=[
                      DataRequired(message='Invalid input')])
    docs = MultipleFileField('Documentation upload', validators=[
                             InputRequired(message='Document required')])
    arrival_date = DateField('Arrival Date', format='%Y-%m-%d',
                             validators=[DataRequired(message='Invalid input')])
    submit = SubmitField('Create')


class SignShipmentDocsForm(FlaskForm):
    sign = MultipleFileField('eSign upload', validators=[
                             InputRequired(message='eSign required')])
    confirm = BooleanField('Accept rules', default=False)


class DeleteShipmentForm(FlaskForm):
    secret_code = PasswordField('Input secret code', validators=[
                                Length(min=5, max=20, message='Invalid secret code')])
    confirm = BooleanField('Confirm', default=False)
    submit = SubmitField('Confirm')


class AcceptShimentForm(FlaskForm):
    confirm = BooleanField('Confirm', default=False)
    submit = SubmitField('Confirm')


class LoginForm(FlaskForm):
    psw = PasswordField('Input password to create shipments', validators=[
                        Length(min=5, max=25, message='Incorrect password')])
    stay_box = BooleanField('Stay in system')
    submit = SubmitField('Login')
