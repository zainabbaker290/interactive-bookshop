from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, RadioField, SelectField, BooleanField, DateField
from wtforms.validators import InputRequired, EqualTo, NumberRange, Length
from wtforms.fields.html5 import DateField


class BookForm(FlaskForm):
    name = StringField("Book:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class EventForm(FlaskForm):
    event_name = StringField("Event Name:", validators=[InputRequired()])
    event_date = DateField("Event Date:", validators=[InputRequired()])
    captcha = StringField("enter captcha:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class RegistrationForm(FlaskForm):
    user_name = StringField("User Name:", validators=[InputRequired()])
    email = StringField("Email:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    security_question_answer = StringField("Security Question Answer", validators=[InputRequired()])
    submit = SubmitField("Submit")
    reload_q = BooleanField("Reload")
    submit2 = SubmitField("Submit")

class LoginForm(FlaskForm):
    user_name = StringField("User Name:", validators=[InputRequired()])
    password = PasswordField("password:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class DeleteForm(FlaskForm):
    user_name = StringField("User Name:", validators=[InputRequired()])
    password = PasswordField("password:", validators=[InputRequired()])
    are_you_sure = BooleanField("are you sure? This cannot be undone")
    submit = SubmitField("Submit")

class CanChangePasswordForm(FlaskForm):
    user_name= StringField("User Name:", validators=[InputRequired()])
    email = StringField("Email:", validators=[InputRequired()])
    submit = SubmitField("Submit")
    answer = StringField("Answer:")
    submit = SubmitField("Submit")

class ChangePasswordForm(FlaskForm):
    user_name = StringField("User Name:", validators=[InputRequired()])
    password = PasswordField("New Password:", validators=[InputRequired()])
    password2 = PasswordField("Confirm New Password:", validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Submit")

class ReviewsForm(FlaskForm):
    book_name = SelectField(
        choices = [("East of Eden", "East of Eden"),
                    ("Mythos", "Mythos"),
                    ("The Kite Runner", "The Kite Runner"),
                    ("Atonement", "Atonement"),
                    ("The Reader", "The Reader"),
                    ("The Cockroach", "The Cockroach"),
                    ("The Childrens Act", "The Childrens Act"),
                    ("The Great Gatsby", "The Great Gatsby"),
                    ("A Thousand Splendid Suns", "A Thousand Splendid Suns")],
        default = "5")
    author = StringField("Author", validators=[InputRequired()])
    stars = SelectField(
            choices = [("1", "1"),
                        ("2", "2"),
                        ("3", "3"),
                        ("4", "4"),
                        ("5", "5")],
            default = "5")
    description = StringField("Review:", validators=[InputRequired()])
    submit = SubmitField("Submit")


class CheckoutForm(FlaskForm):

    title = SelectField(
            choices=[("ms", "Ms"),
                    ("mr", "Mr"),
                    ("miss", "Miss"),
                    ("other", "other"),],
            default= "ms"
    )

    name = StringField("Name:", validators=[InputRequired()])
    surname = StringField("Surname:", validators=[InputRequired()])
    address = StringField("Address:", validators=[InputRequired()])
    country = SelectField(
                choices = [("ireland", "Republic of Ireland"),
                            ("northen ireland", "Northen Ireland"),
                            ("scotland", "Scotland"),],
                default = "ireland"
    )

    card_name = StringField("Name on card:", validators=[InputRequired()])
    card_number = StringField("Card Number:", validators=[InputRequired(), Length(min=16, max=16, message= "card format not recognised")])
    expired = DateField("Expiration Date:", validators=[InputRequired()])
    cvv = StringField("CVV:", validators=[InputRequired(), Length(min=3, max=3, message="card format not recognised")])
    card_details = BooleanField("would you like to save card details for next time?")
    submit = SubmitField("Submit")

class DiscountForm(FlaskForm):
    discount = StringField("Discount Code:")
    submit2 = SubmitField("Submit")

