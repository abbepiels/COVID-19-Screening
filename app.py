from enum import unique
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from forms import LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import exc


app = Flask(__name__)
app.config['SECRET_KEY'] = 'zhupasAngels'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

Bootstrap(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80), unique=True)


@app.route("/")
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        current_user = User.query.filter_by(
            username=form.username.data).first()
        if current_user:
            if check_password_hash(current_user.password, form.password.data):
                return redirect(url_for('home'))
        return 'Incorrect username or password'
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))
        except exc.IntegrityError:
            db.session.rollback()
            return "<h1>Username already exists</h1>"
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
