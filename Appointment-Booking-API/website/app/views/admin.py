from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import Appointment, Availability # The double dot (..) means its a relative import, which pretty much means "go up one directory level"

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin():
    if current_user.role in ['admin', 'manager']:
        appointments = Appointment.query.all()
        availability = Availability.query.first() 
        if not availability:
            flash("No availability settings found. Please set up your availability.", category="info")
        return render_template("admin.html", appointments=appointments, availability=availability)
    else:
        flash("Must be admin to access this page", category="error")
        return redirect(url_for('home_bp.home'))
