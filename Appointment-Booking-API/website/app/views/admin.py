from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import Appointment, Availability # The double dot (..) means its a relative import, which pretty much means "go up one directory level"

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin():
    return render_template('admin.html')
