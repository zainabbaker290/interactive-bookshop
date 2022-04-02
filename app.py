from flask import Flask, render_template, url_for, session, redirect, g, request
from database import get_db, close_db
from forms import BookForm, RegistrationForm, EventForm, ReviewsForm, LoginForm, DeleteForm, CanChangePasswordForm, ChangePasswordForm, CheckoutForm, DiscountForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from datetime import datetime
from functools import wraps
import random
from sqlite3 import IntegrityError

#Captcha code = bonus points?
#Discount code at cart = bonus points
#when logging in, if you enter the incorrect password three times, you will be redirected to change your password
#when checking out make sure your card number is 16 characters and your cvv is 3
# if you save your details, your form for the checkout should be automatically filled out for next time
    #(except for the expiry date and the cvv for security reasons )
'''
#captcha
#what i used to make the captcha 
#the captcha answer is: bonus points?
from captcha.image import ImageCaptcha
image = ImageCaptcha(width = 280, height = 90)
data = image.generate('bonuspoints?')
image.write('bonuspoints?', 'bonus.png')
'''


app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.teardown_appcontext
def close_db_at_end_of_request(e=None):
    close_db(e)

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_name", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return(redirect(url_for("login", next=request.url)))
        return view(**kwargs)
    return wrapped_view


#starting point
@app.route("/", methods = ["POST", "GET"])
def home():
    return render_template("mainpage.html")


#shows you all the books
@app.route("/browse", methods = ["POST", "GET"])
def browse():
    db = get_db()
    books = db.execute("""SELECT * FROM books;""").fetchall()
    return render_template("browse.html", caption ="All Books", books=books)

# when see details of book 
@app.route("/book/<int:book_id>", methods = ["GET", "POST"])
def book(book_id):
    db = get_db()
    book = None
    book = db.execute("""SELECT * FROM books WHERE book_id = ?;""", (book_id,)).fetchone()
    return render_template("book.html", book=book)


#shows you books that are like the name you submitted 
@app.route("/book_by_name", methods = ["GET", "POST"])
def book_by_name():
    form = BookForm()
    books = None

    if form.validate_on_submit():
        name = form.name.data
        db = get_db()
        books = db.execute("""SELECT *
                            FROM books
                            WHERE name LIKE ?""", ('%'+name+'%',)).fetchall()

        #if the book does not appear to exist in the db
        if len(books) == 0:
            form.name.errors.append("book is not available")
            return render_template("book_by_name.html", books = books, form = form )

        
    return render_template("book_by_name.html", books = books, form = form)


#register 
@app.route("/register", methods=["GET","POST"])
def register():
    form = RegistrationForm()

    security_questions = ["what is your mothers maiden name?", "what is the name of your first pet?", "what is your favourite book?"]
    security_question = (random.choice(security_questions))

    # we need to store a new security question if a. not there before, or b. we are visting the page again.
    if "security_question" not in session or not form.validate_on_submit():
        session["security_question"] = security_question

    if form.validate_on_submit():

        reload_q = form.reload_q.data
        user_name = form.user_name.data
        password = form.password.data
        password2 = form.password2.data
        email = form.email.data
        security_question_answer = form.security_question_answer.data
        db = get_db()


        if reload_q == True:
            # we need to pick a new security question and then save it to session, and send it to form.
            security_question = (random.choice(security_questions))
       
            session["security_question"] = security_question

        #if the username already exists 

        elif db.execute("""SELECT * FROM users
                        WHERE user_name = ?;""", (user_name,)).fetchone() is not None:
            form.user_name.errors.append("User name already taken! Please use another")

        #if all is good, you should be registered 
        else:
            try:
                db.execute('''INSERT INTO users (user_name,password,email,security_question,security_question_answer)
                                VALUES (?,?,?,?,?);''',(user_name,generate_password_hash(password), email, session["security_question"], security_question_answer))
                db.commit()
            except IntegrityError:
                return("an error has occured", url_for("home"))
            return redirect(url_for("login"))
    return render_template("register.html", form=form, security_question = session["security_question"])

#to login
@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        db = get_db()
        user = db.execute('''SELECT * FROM users
                            WHERE user_name = ?;''',(user_name,)).fetchone()
        if user is None:
            form.user_name.errors.append("Incorrect credentials!") #dont want to give away anything in database

        #if its the wrong password 
        elif not check_password_hash(user["password"],password):
            if "login_retries" not in session:
              session["login_retries"] = 1
            else:
                session["login_retries"] += 1
            form.password.errors.append("Incorrect credentials!") #dont want to give away anything in database
            if session["login_retries"] >= 3:
                return redirect(url_for("can_change_password"))
               # if password put in more than 3 times
               # show change password
        else:
            session.clear()
            session["user_name"] = user_name
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("home")
            return redirect(next_page)

    return render_template("login.html", form=form)
        
#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

#checks to see if you are valid to change the password 
@app.route("/can_change_password", methods=["GET","POST"])
def can_change_password():
    form = CanChangePasswordForm()
    user_data = None

    if form.validate_on_submit():
        user_name = form.user_name.data
        email = form.email.data
        db = get_db()

        #checks to see if username matches email
        user_data = db.execute('''SELECT security_question 
                                FROM users
                                WHERE user_name = ? and email = ?;''',(user_name,email)).fetchone()

        #if the username exists 
        if user_data != None:

            #gets the security answer in the db
            answer = form.answer.data
            real_answer = db.execute('''SELECT security_question_answer
                                FROM users
                                WHERE user_name = ? and email = ?;''',(user_name,email)).fetchone()

            #if the answers match, valid to change password 
            if answer != "":
                for a in real_answer:
                    if answer == a:
                        return redirect(url_for("change_password"))
                    else:
                        form.answer.errors.append("Incorrect")

        else:
            return render_template("can_change_password.html", form=form, user_data= user_data, message = "incorrect data")
        
        return render_template("can_change_password.html", user_data = user_data, form=form)

    return render_template("can_change_password.html", form=form, user_data= user_data)

#change password here 
@app.route("/change_password", methods=["GET","POST"])
def change_password():
    form = ChangePasswordForm()
    user_data = None
    message = ""


    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        password2 = form.password2.data

        db = get_db()

        user_data = db.execute('''SELECT *
                                FROM users
                                WHERE user_name = ?;''',(user_name,)).fetchone()

        #if the user exists, you can change your password
        if user_data != None:

            user_data = db.execute('''Update users
                                    SET password = ?
                                    WHERE user_name = ?;''',(generate_password_hash(password),user_name)).fetchone()
            
            db.commit()
            return(render_template("change_password.html", form=form, user_data= user_data, message = "Password succesfully changed"))
        
        else:
            return(render_template("change_password.html", form=form, user_data= user_data, message = "Password NOT succesfully changed"))



    return(render_template("change_password.html", form=form, user_data= user_data, message = ""))

#deleting account
@app.route("/delete_account", methods=["GET","POST"])
@login_required
def delete_account():
    form = DeleteForm()
    user = None
    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        are_you_sure = form.are_you_sure.data
        #if you are sure and you are in the db with the correct password: delete
        if are_you_sure == True:
            db = get_db()
            user = db.execute('''Select *
                                FROM users
                                WHERE user_name = ?;''',(user_name,)).fetchone()

            #if the user doesnt exist
            if user is None:
                form.user_name.errors.append("Unknown user")

            #or if the password does not match 
            elif not check_password_hash(user["password"],password):     
                form.password.errors.append("Incorrect credentials!")

            else:
                user = db.execute('''Delete
                                    FROM users
                                    WHERE user_name = ?;''',(user_name,)).fetchone()
                
                db.commit()
               
                return render_template("delete_account.html", form=form, message = "account successfully deleted, please logout" )
            
        else: 
            return render_template("delete_account.html", form=form, message ="account not deleted, as you were unsure", user = user)


    return render_template("delete_account.html", form=form, message = "", user=user)


#leaving a review 
@app.route("/reviews", methods = ["POST", "GET"])
@login_required
def reviews():
    #shows all reviews 
    db = get_db()
    reviews = db.execute("""SELECT * FROM reviews ORDER BY book_name;""").fetchall()

    form = ReviewsForm()
    message = ""

    #to submit one 
    if form.validate_on_submit():
        book_name = form.book_name.data
        author = form.author.data
        stars = form.stars.data
        review = form.description.data

        #checks to see if the author matches the book in DB 
        valid = db.execute("""SELECT * 
                            FROM books 
                            WHERE name = ?
                            AND author = ?;""", (book_name, author)).fetchone()
        
        #if they match, insert into reviews
        if valid != None:
            db.execute("""INSERT INTO reviews (book_name, author, stars, review)
                            VALUES(?,?,?,?);""", (book_name, author, stars, review))
            db.commit()
            message = "review successfully added"

        #if not, return this
        else:
            message = "review not added :("
                
    return render_template("reviews.html", reviews=reviews, form = form, message=message)


#shows future events
@app.route("/events", methods = ["POST", "GET"])
def all_events():
    db = get_db()
    events = db.execute("""SELECT * 
                            FROM events
                            WHERE event_date >= DATE('now');""").fetchall()
    return render_template("events.html", events=events)

#submitting an event 
@app.route("/submit_event", methods = ["GET", "POST"])
@login_required
def submit_event():
    form = EventForm()
    message = ""
    if form.validate_on_submit():
        event_name = form.event_name.data
        event_date = form.event_date.data
        captcha = form.captcha.data

        #if event is in past

        if event_date <= datetime.now().date():
            form.event_date.errors.append("date must be in the future")

        else:
            db = get_db()

            #if event clashes another

            if db.execute("""SELECT * FROM events
                            WHERE event_date = ?""", (event_date,)).fetchone() is not None:
               
                form.event_date.errors.append("event clashes with another")
            
            #if the captcha does not match 

            elif captcha != "bonus points?":
                form.captcha.errors.append("why dont you want to give me bonus points?")

            #if all is good, insert it
            else:
                db.execute("""INSERT INTO events (event_name, event_date)
                            VALUES (?,?);""", (event_name,event_date))
                db.commit()
                message = "new event successfully inserted"
    return render_template("submit_event.html", message=message, form= form)


#cart 
@app.route("/cart", methods = ["GET", "POST"])
@login_required
def cart():
    if "cart" not in session:
        session["cart"] = {}
    names = {}
    prices = {}
    price_per_books = []
    total_price = 0
    db = get_db()
    for book_id in session["cart"]:
        #gets you name of book
        name = db.execute("""SELECT * FROM books
                        WHERE book_id = ?;""", (book_id,)).fetchone()["name"]
        names[book_id] = name

        #gets you price of book
        price = db.execute("""SELECT * FROM books
                        WHERE book_id = ?;""", (book_id,)).fetchone()["price"]
        prices[book_id] = price


        #total price of that book * quantity you want 
        total_price_per_book = round(price * (session["cart"][book_id]),2)

        price_per_books.append(total_price_per_book)
        
        # total price of everything 
        for book in price_per_books:
            book = round(book,2)
        total_price += book
        total_price = round(total_price,2)


    
    return render_template("cart.html", cart = session["cart"], names = names, prices = prices, price_per_books = price_per_books, total_price = total_price)

#adding to cart
@app.route("/add_to_cart/<int:book_id>")
def add_to_cart(book_id):
    if "cart" not in session:
        session["cart"] = {}

    if book_id not in session["cart"]:
        session["cart"][book_id] = 0 
    session["cart"][book_id] = session["cart"][book_id] + 1

    return redirect( url_for("cart") )

#removing from cart
@app.route("/remove_from_cart/<int:book_id>")
def remove_from_cart(book_id):
    if "cart" not in session:
        session["cart"] = {}

    if book_id not in session["cart"]:
        session["cart"][book_id] = 0 
    session["cart"][book_id] = session["cart"][book_id] - 1

    if session["cart"][book_id] <= 0:
        session["cart"].pop(book_id)


    return redirect( url_for("cart") )



#checkout 
@app.route("/checkout", methods = ["GET", "POST"])
@login_required
def checkout():

    form = CheckoutForm()
    form2 = DiscountForm()
    user_name = session["user_name"]

    #recalculates total for security purposes 
    if "cart" not in session:
        session["cart"] = {}
    prices = {}
    price_per_books = []
    total_price = 0
    db = get_db()
    for book_id in session["cart"]:
        #gets you price of book
        price = db.execute("""SELECT * FROM books
                        WHERE book_id = ?;""", (book_id,)).fetchone()["price"]
        prices[book_id] = price


        #total price of that book * quantity you want 
        total_price_per_book = round(price * (session["cart"][book_id]),2)

        price_per_books.append(total_price_per_book)
        
        # total price of everything 
        for book in price_per_books:
            book = round(book,2)
        total_price += book
        total_price = round(total_price,2)

        # total price if discount for 10 % is right
        if form2.validate_on_submit():
            discount = form2.discount.data
            if discount == "bonus points":
                total_price = round(((total_price / 100) * 90),2)

    
    saved_details = db.execute("""SELECT card_number FROM orders
                                WHERE user_name = ?""", (user_name,)).fetchone()

    #if you had saved your details
    #still need to put in expiration date and cvv for security reasons
    if saved_details is not None:
        select_details = db.execute("""SELECT * FROM orders
                                    WHERE user_name = ?""", (user_name,)).fetchone()
        form.title.data = select_details["title"]
        form.name.data = select_details["name"]
        form.surname.data = select_details["surname"]
        form.address.data = select_details["address"]
        form.country.data = select_details["country"]
        form.card_name.data = select_details["card_name"]
        form.card_number.data = select_details["card_number"]


    if form.validate_on_submit():
        user_name = session["user_name"]
        title = form.title.data
        name = form.name.data
        surname = form.surname.data 
        address = form.address.data 
        country = form.country.data 
        card_name = form.card_name.data
        card_number = form.card_number.data
        expired = form.expired.data 
        cvv = form.cvv.data 
        card_details = form.card_details.data 

        #if card date is expired
        if expired <= datetime.now().date():
            form.expired.errors.append("date must be in future")

        #if the inputs are okay 
        else:
            #db = get_db()
            #if you want to save your card details for next time
            if card_details == True:
                db.execute("""INSERT INTO orders (title, user_name, name, surname, address, country, card_name, card_number, expired, cvv,cart)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?);""",(title, user_name, name, surname, address, country, card_name, card_number, expired, cvv, total_price))
                db.commit()
                
            #if not
            else:
                db.execute("""INSERT INTO orders (title, user_name,name, surname, address, country, card_name, cart)
                                VALUES (?,?,?,?,?,?,?,?);""",(title,user_name, name, surname, address, country, card_name, total_price))
                db.commit()
                
            

            return redirect(url_for("order_submitted"))
    return render_template("checkout.html", form=form, cart = session["cart"], prices = prices, price_per_books = price_per_books, total_price = total_price, form2 = form2)



#submitted order
#here your cart is cleared 
@app.route("/order_submitted" , methods = ["GET", "POST"])
def order_submitted():
    del session["cart"]
    return render_template("order_submitted.html")


#shows past orders for that user
# wont show you your card details in the html, for security reasons 
@app.route("/past_orders", methods = ["GET", "POST"])
@login_required
def past_orders():
    user_name = session["user_name"]
    db = get_db()
    past_orders = db.execute("""SELECT * FROM orders
                                WHERE user_name = ?;""",(user_name,)).fetchall()
    return render_template("past_orders.html", past_orders = past_orders)





























