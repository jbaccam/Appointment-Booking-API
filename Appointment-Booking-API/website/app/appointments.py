from datetime import datetime
from flask import Blueprint, request, flash, redirect, url_for
from .models import Appointment, Availability
from . import db

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/create-appointment', methods=['POST'])
def create_appointment():
    name = request.form.get('appointmentName')
    description = request.form.get('appointmentDescription')
    interval = request.form.get('interval')

    if not interval:
        flash('You must select an appointment duration.', 'error')
        return redirect(url_for('appointments.create_appointment'))

    try:
        interval = int(interval)  # convert interval to integer
    except ValueError:
        flash('Invalid duration selected.', 'error')
        return redirect(url_for('appointments.create_appointment'))

    new_appointment = Appointment(
        name=name,
        description=description,
        interval=interval
    )

    db.session.add(new_appointment)
    db.session.commit()

    flash('Appointment created successfully!', 'success')
    return redirect(url_for('views.admin'))

availability_bp = Blueprint('availability', __name__)



@appointments_bp.route('/delete-appointment/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('views.admin'))

@appointments_bp.route('/set-availability', methods=['POST'])
def set_availability():
    days = request.form.getlist('days')
    start_time = request.form.get('startTime')
    end_time = request.form.get('endTime')

    if not days or not start_time or not end_time:
        flash('All fields are required!', 'error')
        return redirect(url_for('views.admin'))

    start_time = datetime.strptime(start_time, '%H:%M').time()
    end_time = datetime.strptime(end_time, '%H:%M').time()

    availability = Availability.query.first()
    if availability:
        availability.available_days = ','.join(days)
        availability.start_time = start_time
        availability.end_time = end_time
    else:
        new_availability = Availability(available_days=','.join(days), start_time=start_time, end_time=end_time)
        db.session.add(new_availability)

    db.session.commit()
    flash('Availability updated successfully!', 'success')
    return redirect(url_for('views.admin'))
