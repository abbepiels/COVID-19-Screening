import flask
from enum import unique
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, redirect, url_for,flash, session,request
from flask_bootstrap import Bootstrap
from flask_login import login_user, LoginManager, logout_user, login_required
from forms import LoginForm, RegisterForm, ContactForm, ContactEntry
from flask_wtf import FlaskForm
from wtforms import ValidationError
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import exc, insert,update
from forms import SymptomForm, AccountForm, ContactNumForm
import phonenumbers
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zhupasAngels'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '19covidscreen@gmail.com'
app.config['MAIL_PASSWORD'] = 'zhupasangels'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


s = URLSafeTimedSerializer('Thisisasecret!')

login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)
db = SQLAlchemy(app)
socketio = SocketIO(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.VARCHAR, unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True)
    fever = db.Column(db.Boolean, default= False, nullable=False)
    cough = db.Column(db.Boolean, default= False, nullable=False)
    fatigue = db.Column(db.Boolean, default= False, nullable=False)
    nausea = db.Column(db.Boolean, default= False, nullable=False)
    headache = db.Column(db.Boolean, default= False, nullable=False)
    bodyaches = db.Column(db.Boolean, default= False, nullable=False)
    throat = db.Column(db.Boolean, default= False, nullable=False)
    difficulty = db.Column(db.Boolean, default= False, nullable=False)
    gender =  db.Column(db.String(), nullable=True)
    firstname = db.Column(db.String(20), unique=True,nullable=True)
    lastname = db.Column(db.String(20), unique=True,nullable=True)
    DOB =  db.Column(db.Date, nullable=True)
    email =  db.Column(db.String(120), unique = True, nullable=True)
    PE = db.Column(db.String(1000), unique = True, nullable=True)
    doctor = db.Column(db.String(), default="", nullable=True)
    num_contact = db.Column(db.Integer(), default=0, nullable=True)
    contacts = db.Column(db.String(), default="", nullable=True)  
    token = db.Column(db.String(80), unique = True)
    def is_active(self):
        return True
    def is_authenticated(self):
        return self.authenticated
    def get_id(self):
        return self.id

ht = {}    
          
@app.before_request
def setup():
    session.permanent = False
@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/profile/<int:id>",methods=['GET'])
@login_required
def profile(id):
    return render_template('Profile.html',id=id)

@app.route("/profile/<int:id>/symptoms",methods=['GET'])
@login_required
def symptom(id):
    profile = User.query.filter_by(id=id).first()
    return render_template('symptoms.html',id=id,profile=profile)

@app.route("/profile/<int:id>/info",methods=['GET'])
@login_required
def info(id):
    profile = User.query.filter_by(id=id).first()
    if id in ht:
        contacts =  ht[id]
    else:
        contacts = "None"
    return render_template('viewinfo.html',id=id,profile=profile, contacts=contacts)    

@app.route("/profile/<int:id>/edit",methods=['GET','POST'])
@login_required
def account(id):
    form = AccountForm()
    user_id = {'ID': id}
    if form.validate_on_submit():
        user = User.query.filter_by(id=id).first()
        user.DOB=form.DOB.data
        user.gender=form.gender.data 
        user.PE=form.PE.data
        user.email=form.email.data
        user.firstname=form.firstname.data.capitalize()
        user.lastname=form.lastname.data.capitalize()
        db.session.commit()
        return redirect(url_for('profile',id=id))
    print(form.errors)
    return render_template('account.html',form=form,user_id=user_id)    

@app.route("/<int:id>/screening", methods=['GET','POST'])
@login_required
def screen(id):
    form = SymptomForm()
    user_id = {'ID': id}
    if form.validate_on_submit():
        print("Success")
        user = User.query.filter_by(id=id).first()
        user.doctor = form.doctor.data
        user.fever=form.fev.data
        user.cough=form.cough.data 
        user.throat=form.throat.data
        user.headache=form.headache.data
        user.nausea=form.nausea.data
        user.fatigue=form.fatigue.data
        user.difficulty=form.difficulty.data
        user.bodyaches=form.bodyaches.data
        user.extra=form.extra.data
        db.session.commit()

        return redirect(url_for('profile',id=id))
    
    return render_template('screening.html',form=form,user_id=user_id)

@app.route("/<int:id>/tracer/", methods=['GET','POST'])
@login_required
def trace(id):
    form = ContactEntry()
    user_id = {'ID': id}
    user = User.query.filter_by(id=id).first()
    session['num_contact'] = user.num_contact
    if id in ht:
        contact = ht[id]
    else:
        ht[id] = " "
    if request.method == 'POST':
        add_contact = request.form.get('add')
        if form.validate_on_submit() and not add_contact:
            contact += "Name: " + form.first_name.data.capitalize() + " "+ form.last_name.data.capitalize() + ", Email: " + form.contactemail.data + ", Phone: " +form.phone.data
            ht[id] += contact
            print("submitting ",ht[id])
            return redirect(url_for('profile',id=id))
        elif form.validate_on_submit() and add_contact:
            contact += "Name: " + form.first_name.data.capitalize() + form.last_name.data.capitalize()  + ", Email: " + form.contactemail.data + ", Phone: " +form.phone.data
            ht[id] += contact
            print("adding", ht[id])
            return redirect(url_for('trace',id=id))
    print(form.errors)
    return render_template('contacttracer.html',form=form,user_id=user_id)

@app.route("/<int:id>/num", methods=['GET','POST'])
@login_required
def num_trace(id):
    form = ContactNumForm()
    user_id = {'ID': id}
    user = User.query.filter_by(id=id).first()
    if form.validate_on_submit():
        user.num_contact = form.num.data
        db.session.commit()
        return redirect(url_for('trace',id=id))
    print(form.errors)
    return render_template('num.html',form=form,user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data).first()
        
        if user:
            if check_password_hash(user.password, form.password.data):
                user.authenticated = True
                session['username'] = user.username
                login_user(user)
                return redirect(url_for('profile',id=user.id))
        return 'Incorrect username or password'
    return render_template('login.html', form=form)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    user = User.query.filter_by(
            token=token).first()
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    return redirect(url_for('profile', id=user.id))


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return render_template('logout.html')
    
@login_manager.unauthorized_handler
def unauthorized_callback(): 
    return render_template('401.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data)
        email = request.form['email']
        token = s.dumps(email, salt='email-confirm')
        
        user = User(username=form.username.data, email = form.email.data, password=hashed,fever=False,
        throat=False,cough=False,fatigue=False,headache=False,difficulty=False,nausea=False,bodyaches=False, token=token)
        
        msg = Message('Confirm Email', sender='19covidscreen@gmail.com', recipients=[email])
        link = url_for('confirm_email', token=token, _external=True) 
        msg.body = 'Your link is {}'.format(link)
        mail.send(msg)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))
        except exc.IntegrityError:
            db.session.rollback()
            return "<h1>Username or email already exists</h1>"
    return render_template('register.html', form=form)



@socketio.on('disconnect')
def disconnect_user():
    logout_user()
    session.pop('zhupasAngels', None)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
