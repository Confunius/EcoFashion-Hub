from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, PasswordField, FloatField, FileField, IntegerField, ValidationError
from wtforms.fields import EmailField, DateField
from wtforms.validators import EqualTo, InputRequired, ValidationError
from wtforms.widgets import PasswordInput, TextInput
from flask_wtf import FlaskForm, RecaptchaField

# def valid_phone_number(form, field):
#     if not field.data:
#         raise validators.ValidationError('Phone number is required.')
#
#     if not field.data.startswith('('):
#         raise validators.ValidationError('Invalid phone number format. Use (XX) XXXX XXXX')

class DelimitedNumberInput(TextInput):
    def __call__(self, field, **kwargs):
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        # Add the delimiter after every four characters
        value = kwargs['value']
        if value and len(value) > 4:
            value = '-'.join(value[i:i+4] for i in range(0, len(value), 4))

        kwargs['value'] = value
        return super(DelimitedNumberInput, self).__call__(field, **kwargs)

class createUser(FlaskForm):
    recaptcha = RecaptchaField()
    userFullName = StringField('Full Name: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userName = StringField('Username: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userEmail = EmailField('Email: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userPassword = PasswordField('Password: ', validators=[validators.Length(min=8, max=16), validators.DataRequired()], widget=PasswordInput(hide_value=False))
    userCfmPassword = PasswordField('Confirm Password: ', [EqualTo('userCfmPassword', message='Password do not match'), InputRequired()],  widget=PasswordInput(hide_value=False)) #validators=[validators.Length(min=8, max=16), validators.DataRequired()],
    userAddress = StringField('Address: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userPostalCode = StringField('Postal Code', validators=[validators.Length(min=6, max=6), validators.DataRequired()])

class userLogin(Form):
    userEmail = EmailField('Email: ', [validators.DataRequired()])
    userPassword = PasswordField('Password: ', validators=[validators.DataRequired()], widget=PasswordInput(hide_value=False))

class userEditInfo(Form):
    userFullName = StringField('Full Name: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userName = StringField('Username: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userEmail = EmailField('Email: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userAddress = StringField('Address: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userPostalCode = StringField('Postal Code', validators=[validators.Length(min=6, max=6), validators.DataRequired()])

class userChangePassword(Form):
    userPassword = PasswordField('New Password: ', validators=[validators.Length(min=8, max=16), validators.DataRequired()], widget=PasswordInput(hide_value=False))
    userCfmPassword = PasswordField('Confirm Password: ', [EqualTo('userCfmPassword', message='Password do not match'), InputRequired()],  widget=PasswordInput(hide_value=False))

class userPaymentMethod(Form):
    userFullName = StringField('Full Name: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userEmail = EmailField('Email: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userCardName = StringField('Card Holder Name', [validators.Length(min=1, max=50), validators.DataRequired()])
    userCardType = SelectField('Card Type',choices=[('visa', 'Visa'), ('mastercard', 'MasterCard'), ('amex', 'American Express')], validators=[validators.DataRequired()])
    userCardNumber = StringField('Card Number', validators=[validators.Length(min=16, max=16), validators.DataRequired()], widget=DelimitedNumberInput())
    userCardExp = StringField('Expiry Date', validators=[validators.InputRequired()])
    userCardSec = StringField('Security Code',validators=[validators.Length(min=3, max=4), validators.DataRequired()])
    userAddress = StringField('Address: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    userPostalCode = StringField('Postal Code', validators=[validators.Length(min=6, max=6), validators.DataRequired()])

class createAdmin(Form):
    adminUserName = StringField('Username: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    adminEmail = EmailField('Email: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    adminPassword = PasswordField('Password: ', validators=[validators.Length(min=8, max=16), validators.DataRequired()], widget=PasswordInput(hide_value=False))
    adminCfmPassword = PasswordField('Confirm Password: ', [EqualTo('adminPassword', message='Password do not match'), InputRequired()],  widget=PasswordInput(hide_value=False)) #validators=[validators.Length(min=8, max=16), validators.DataRequired()],
    adminFirstName = StringField('First Name: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    adminLastName = StringField('Last Name: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    adminPhoneNumber = StringField('Phone Number: ', validators=[validators.Length(min=8, max=18), validators.DataRequired()] )

class adminLogin(Form):
    adminEmail = EmailField('Email: ', [validators.DataRequired()])
    adminPassword = PasswordField('Password: ', validators=[validators.Length(min=8, max=16), validators.DataRequired()], widget=PasswordInput(hide_value=False))

class editAdminAccount(Form):
    adminEmail = EmailField('Email: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    adminFirstName = StringField('First Name: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    adminLastName = StringField('Last Name: ', validators=[validators.Length(min=1, max=150), validators.DataRequired()])
    adminPhoneNumber = StringField('Phone Number: ', validators=[validators.Length(min=8, max=18), validators.DataRequired()] )
