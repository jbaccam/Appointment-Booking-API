import binascii, os, uuid
from flask import Blueprint, abort, flash, redirect, render_template, url_for, request, session
from flask_login import login_required, current_user
from . import db
from .models import User, Business, Appointment, Availability

views = Blueprint('views', __name__)

# Create home page
@login_required
@views.route('/')
def home():
    return render_template("home.html", user=current_user)

# Create dashboard page
@login_required
@views.route('/dashboard')
def dashboard():
    business_id = session.get('business_id')
    if not business_id or str(current_user.business_id) != str(business_id):
        flash('Unauthorized access.', category='error')
        return redirect(url_for('views.home'))

    validate_business_id(business_id)

    business = Business.query.get(business_id)
    return render_template('dashboard.html', business=business)


# Create appointments page
@login_required
@views.route('/appointment')
def appointment():
    return render_template("time-scheduler.html", user=current_user)

# Create manager page
@login_required
@views.route('/manager', methods=['GET', 'POST'])
def manager():
    if current_user.role == 'manager':
        if request.method == 'POST':
            make_admin_email = request.form.get('make_admin_email')
            remove_admin_email = request.form.get('remove_admin_email')

            if make_admin_email:
                user = User.query.filter_by(email=make_admin_email).first()
                if user:
                    user.role = 'admin'
                    db.session.commit()
                    flash(f'User {make_admin_email} is now an admin.', category='success')
                else:
                    flash('No user found with that email.', category='error')

            if remove_admin_email:
                user = User.query.filter_by(email=remove_admin_email).first()
                if user:
                    user.role = 'user'
                    db.session.commit()
                    flash(f'User {remove_admin_email} is no longer an admin.', category='success')
                else:
                    flash('No user found with that email.', category='error')
            #removing users that joined via invite code
            remove_user_email = request.form.get('remove_user_email')
            if remove_user_email:
                user = User.query.filter_by(email=remove_user_email).first()
                if user:
                    # check if the user is associated with the current manager's business
                    if user.business_id == current_user.business_id:
                        # remove the user's access
                        db.session.delete(user)
                        db.session.commit()
                        flash(f'User {remove_user_email} account has been deleted.', category='success')
                        return redirect(url_for('views.home'))  # redirect to the home page
                    else:
                        flash('User does not belong to your business.', category='error')
                else:
                    flash('No user found with that email.', category='error')
            else:
                flash('No user found with that email.', category='error')
                return redirect(url_for('views.home'))  #redirect to the home page

        return render_template("manager.html", user=current_user)
    else:
        flash("Must be manager to access this page", category="error")
        return redirect(url_for('views.home'))

#Create admin page
@login_required
@views.route('/admin')
def admin():
    if current_user.role in ['admin', 'manager']:
        appointments = Appointment.query.all()
        availability = Availability.query.first()  # fetch the first availability 
        if not availability:
            flash("No availability settings found. Please set up your availability.", category="info")
        return render_template("admin.html", user=current_user, appointments=appointments, availability=availability)
    else:
        flash("Must be admin to access this page", category="error")
        return redirect(url_for('views.home'))

#for invite codes
@views.route('/manager/generate-invite-code', methods=['POST'])
@login_required
def generate_invite_code():
    if current_user.role == 'manager':
        # assumes the manager has only one business associated
        business = Business.query.filter_by(id=current_user.business_id).first()
        if business:
            # generate a new invite code
            business.invite_code = binascii.hexlify(os.urandom(24)).decode()
            db.session.commit()
            flash('New invite code generated.', category='success')
        else:
            flash('Business not found.', category='error')
    else:
        flash('Unauthorized action.', category='error')
    return redirect(url_for('views.manager'))

#helper method to validate business ID
def validate_business_id(business_id):
    if current_user.business_id == business_id:
        # check if the business_id is a valid UUID
        try:
            uuid.UUID(business_id, version=4)
        except ValueError:
            return "Invalid business ID", 400

        business = Business.query.get(business_id)
        if business:
            return render_template('dashboard.html', business=business)
        else:
            return "Business not found", 404
    else:
        return "Access Denied", 403

