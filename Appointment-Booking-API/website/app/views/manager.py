from flask import Blueprint, render_template

# Define the blueprint
manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/manager')
def manager_dashboard():
    return render_template('manager.html')
