from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User, Business
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

#login functionality
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                session['business_id'] = str(user.business_id) 
                return redirect(url_for('views.dashboard', business_id=session['business_id']))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html')

#logout
@auth.route('/logout')
@login_required
def logout():
    session.pop('business_id', None)  # rmove business_id from session
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('auth.login'))


#signup functionality
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        invite_code = request.form.get('invite_code')  

        if password1 != password2:
            flash('Passwords do not match.', category='error')
            return render_template("sign_up.html")
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', category='error')
            return render_template("sign_up.html")

        # handles the invite code for joining an existing business
        if invite_code:
            business = Business.query.filter_by(invite_code=invite_code).first()
            if business:
                new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1), business_id=business.id)
                new_user.role = 'admin' # if you use an invite code, you are an admin
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True) 
                session['business_id'] = str(new_user.business_id)  
                flash('Successfully joined the business.', category='success')
                return redirect(url_for('views.dashboard', business_id=session['business_id']))
            else:
                flash('Invalid invite code.', category='error')
                return render_template("sign_up.html")

        # new business creation
        business_name = request.form.get('business_name')
        business_phone = request.form.get('business_phone')
        business_email = request.form.get('business_email')

        if business_name and business_phone and business_email:
            new_business = Business(name=business_name, phone=business_phone, email=business_email)
            db.session.add(new_business)
            db.session.flush()  
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1), business_id=new_business.id)
            new_user.role = 'manager' # if you are the first user, you are an manager
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            session['business_id'] = new_user.business_id  # set business ID in session
            flash('New business created and you are now logged in!', category='success')
            return redirect(url_for('views.dashboard', business_id=session['business_id']))
        else:
            flash('Please fill in all fields to create a new business or provide an invite code to join an existing business.', category='error')

    return render_template("sign_up.html")