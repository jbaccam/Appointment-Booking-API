from datetime import date, datetime, time, timedelta
from flask import Blueprint, flash, redirect, render_template, url_for, request, jsonify
from flask_login import login_required, current_user 
from . import db
from .models import Categories, User, Business, Availability, Appointment

views = Blueprint('views', __name__)

# Create home page
@views.route('/')
@login_required
def home():
    # Fetch the user's upcoming appointments
    appointments = Appointment.query.filter_by(user_id=current_user.id).filter(Appointment.time_slot >= datetime.now()).order_by(Appointment.time_slot).all()

    return render_template("home.html", user=current_user, appointments=appointments)


# Create dashboard page
@views.route('/dashboard')
@login_required
def dashboard():
    business = Business.query.filter_by(id=current_user.id).first()
    
    if not business:
        flash('No business found.', category='error')

    # Query upcoming appointments for the current user
    upcoming_appointments = Appointment.query.filter_by(user_id=current_user.id).filter(Appointment.time_slot >= datetime.now()).order_by(Appointment.time_slot).all()

    return render_template("dashboard.html", user=current_user, business=business, upcoming_appointments=upcoming_appointments)


# Create manager page with the ability to set admin availability and manage business info
@views.route('/manager', methods=['GET', 'POST'])
@login_required
def manager():
    if current_user.role != 'manager':  # Only managers can access this route
        flash("Must be manager to access this page", category="error")
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # Handle Business Information Form
        business_name = request.form.get('business_name')
        business_phone = request.form.get('business_phone')
        business_email = request.form.get('business_email')

        # Check if the business info form was submitted
        if business_name or business_phone or business_email:
            if not business_name or not business_phone or not business_email:
                flash("All fields are required for Business Information", category="error")
            else:
                # Check if the business already exists for the current manager
                business = Business.query.filter_by(id=current_user.id).first()

                if business:
                    # Update the existing business info
                    business.name = business_name
                    business.phone = business_phone
                    business.email = business_email
                    flash('Business information updated successfully!', category='success')
                else:
                    # Create new business information
                    new_business = Business(
                        name=business_name,
                        phone=business_phone,
                        email=business_email,
                        id=current_user.id
                    )
                    db.session.add(new_business)
                    flash(f'Business "{business_name}" created successfully!', category='success')

                db.session.commit()

        # Handle Admin Availability Form
        selected_admin_id = request.form.get('selected_admin') or current_user.id  # If no admin is selected, default to current user (the manager)
        day = request.form.get('day')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        if selected_admin_id and day and start_time and end_time:
            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()

            availability = Availability.query.filter_by(admin_id=selected_admin_id, day=day).first()

            if availability:
                availability.start_time = start_time
                availability.end_time = end_time
                flash(f"Availability for {day} updated successfully!", 'success')
            else:
                new_availability = Availability(
                    admin_id=selected_admin_id,
                    day=day,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(new_availability)
                db.session.commit()
                flash(f"Availability for {day} added successfully!", 'success')

        # Handle Admin Management: Add and Remove Admins by Email
        if 'add_admin' in request.form:
            admin_email = request.form.get('admin_email')
            user = User.query.filter_by(email=admin_email).first()

            if user:
                if user.role != 'admin':  # Ensure the user is not already an admin
                    user.role = 'admin'
                    db.session.commit()
                    flash(f"User {user.first_name} has been successfully added as an admin!", 'success')
                else:
                    flash(f"User {user.first_name} is already an admin.", 'info')
            else:
                flash(f"No user found with the email {admin_email}.", 'error')

        if 'remove_admin' in request.form:
            admin_email = request.form.get('remove_admin_email')
            admin_to_remove = User.query.filter_by(email=admin_email).first()

            if admin_to_remove and admin_to_remove.role == 'admin':
                admin_to_remove.role = 'user'
                db.session.commit()
                flash(f"{admin_to_remove.first_name} has been successfully removed from the admin role.", 'success')
            else:
                flash(f"Admin not found or user is not an admin.", 'error')

        return redirect(url_for('views.manager'))

    # Get all admins, their availabilities, and business info to display in the form
    admins = User.query.filter(User.role == 'admin').all()  # Only admins will show up
    business = Business.query.filter_by(id=current_user.id).first()
    availabilities = Availability.query.filter_by(admin_id=current_user.id).all()

    return render_template("manager.html", user=current_user, business=business, admins=admins, availabilities=availabilities)


# Admin panel
@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin' and current_user.role != 'manager':
        flash("Must be admin or manager to access this page", category="error")
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # Handle User Appointment Removal
        if 'remove_appointment' in request.form:
            user_id = request.form.get('user_id')
            appointment_id = request.form.get('appointment_id')

            # Debugging: Flash to ensure user_id and appointment_id are captured
            flash(f'Removing appointment: user_id={user_id}, appointment_id={appointment_id}', 'info')

            appointment = Appointment.query.filter_by(user_id=user_id, id=appointment_id).first()

            if appointment:
                db.session.delete(appointment)
                db.session.commit()
                flash(f"Appointment for user {user_id} removed successfully.", 'success')
            else:
                flash(f"No appointment found for the selected user and appointment.", 'error')

        # Handle Appointment Creation
        if 'create_appointment' in request.form:
            create_appointment = request.form.get('create_appointment')
            appointment_description = request.form.get('appointment_description')

            if create_appointment:
                appointment = Categories.query.filter_by(name=create_appointment).first()
                if appointment:
                    flash(f'Appointment "{create_appointment}" already exists.', category='error')
                else:
                    new_appointment = Categories(name=create_appointment, description=appointment_description)
                    db.session.add(new_appointment)
                    db.session.commit()
                    flash(f'Appointment "{create_appointment}" created successfully.', category='success')
            else:
                flash('Please enter an appointment name.', category='error')

        # Handle Appointment Deletion
        if 'delete_appointment' in request.form:
            delete_appointment = request.form.get('delete_appointment')

            if delete_appointment:
                appointment = Categories.query.filter_by(name=delete_appointment).first()
                if appointment:
                    db.session.delete(appointment)
                    db.session.commit()
                    flash(f'Appointment "{delete_appointment}" deleted successfully.', category='success')
                else:
                    flash(f'Appointment "{delete_appointment}" does not exist.', category='error')
            else:
                flash('Please enter an appointment name to delete.', category='error')

        return redirect(url_for('views.admin'))

    # Get users with appointments, join explicitly on user_id
    users_with_appointments = db.session.query(User).join(Appointment, User.id == Appointment.user_id).all()

    # Get the appointments for each user
    user_appointments = {
        user.id: Appointment.query.filter_by(user_id=user.id).all() for user in users_with_appointments
    }

    return render_template("admin.html", user=current_user, users=users_with_appointments, user_appointments=user_appointments)




# A helper function to get the next date for a given weekday name
def get_next_weekday(weekday_name):
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    today = date.today()
    weekday_num = weekdays.index(weekday_name)  # Get the index of the weekday (0 = Monday)
    days_ahead = weekday_num - today.weekday()
    if days_ahead <= 0:  # If the day has already passed this week
        days_ahead += 7
    return today + timedelta(days=days_ahead)


#Booking Appointments
@views.route('/appointments', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if request.method == 'POST':
        category_id = request.form.get('category') 
        admin_id = request.form.get('admin_id')
        time_slot = request.form.get('time_slot')
        day = request.form.get('day')

        # Ensure both day and time_slot are captured
        if not day or not time_slot:
            flash("Please select both day and time for the appointment.", "error")
            return redirect(url_for('views.book_appointment'))

        # Ensure day is in 'YYYY-MM-DD' format
        try:
            day_datetime = datetime.strptime(day, '%Y-%m-%d') 
        except ValueError:
            flash("Invalid date format. Please select a valid day.", "error")
            return redirect(url_for('views.book_appointment'))

        # Ensure time_slot is in 'HH:MM' format
        try:
            time_slot_datetime = datetime.strptime(time_slot, '%H:%M').time() 
        except ValueError:
            flash("Invalid time format. Please select a valid time slot.", "error")
            return redirect(url_for('views.book_appointment'))

        # Combine the valid day and time into one datetime object
        appointment_datetime = datetime.combine(day_datetime.date(), time_slot_datetime)

        # Retrieve the category object
        category = Categories.query.get(category_id)
        if not category:
            flash('Invalid category selected.', 'error')
            return redirect(url_for('views.book_appointment'))

        # Check if the user has already booked an appointment for the same day
        existing_appointment = Appointment.query.filter(
            Appointment.user_id == current_user.id,
            db.func.date(Appointment.time_slot) == day_datetime.date()
        ).first()

        if existing_appointment:
            flash('You can only book one appointment per day.', 'error')
            return redirect(url_for('views.book_appointment'))

        # Check if the time slot is already booked by someone else
        conflicting_appointment = Appointment.query.filter_by(admin_id=admin_id, time_slot=appointment_datetime).first()
        if conflicting_appointment:
            flash('This time slot is already booked.', 'error')
            return redirect(url_for('views.book_appointment'))

        # Save the booking to the database, ensuring the category is the actual object
        new_booking = Appointment(
            user_id=current_user.id,
            admin_id=admin_id,
            time_slot=appointment_datetime,
            category=category  
        )
        db.session.add(new_booking)
        db.session.commit()
        flash('Your appointment has been booked successfully!', 'success')
        return redirect(url_for('views.book_appointment'))

    # Retrieve appointment categories and both admins and managers with availability
    categories = Categories.query.all()
    admins_and_managers = User.query.filter(User.role.in_(['admin', 'manager'])).all()  
    return render_template('appointments.html', categories=categories, admins=admins_and_managers)


# Available days for a specific admin
@views.route('/get-available-days/<int:admin_id>', methods=['GET'])
@login_required
def get_available_days(admin_id):
    availabilities = Availability.query.filter_by(admin_id=admin_id).all()

    # For each availability, provide both the day name and the actual date
    days = []
    for availability in availabilities:
        # Calculate the next upcoming date for the given day (e.g., the next Wednesday)
        next_date = get_next_date_for_weekday(availability.day)
        days.append({"day": availability.day, "date": next_date.strftime('%Y-%m-%d')})

    return jsonify({'days': days})

# Helper method that gets the date for the week day
def get_next_date_for_weekday(day_name):
    """ Given a weekday name (e.g., 'Wednesday'), return the next date for that day. """
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    today = datetime.today()
    day_index = weekdays.index(day_name)
    days_ahead = day_index - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7  # Get the next instance of the day
    return today + timedelta(days=days_ahead)


# Available time slots for a specific admin on a specific day
@views.route('/get-available-times/<int:admin_id>/<string:day>', methods=['GET'])
@login_required
def get_available_times(admin_id, day):
    # Find availability based on the actual date (converted from 'YYYY-MM-DD')
    try:
        day_date = datetime.strptime(day, '%Y-%m-%d').date()  # Parse the day into date format
    except ValueError:
        return jsonify({'times': []})  # Return empty if day format is invalid
    
    # Filter by day name instead of the date 
    weekday_name = day_date.strftime('%A')  # Convert date back to weekday name like "Wednesday"
    availability = Availability.query.filter_by(admin_id=admin_id, day=weekday_name).first()
    
    if availability:
        start_time = availability.start_time
        end_time = availability.end_time
        
        # Generate time slots in 1-hour increments
        time_slots = []
        current_time = start_time
        while current_time < end_time:
            time_slots.append(current_time.strftime('%H:%M'))
            current_time = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()
        
        return jsonify({'times': time_slots})
    
    return jsonify({'times': []})


# List User appointments
@views.route('/get-user-appointments/<int:user_id>', methods=['GET'])
@login_required
def get_user_appointments(user_id):
    appointments = Appointment.query.filter_by(user_id=user_id).all()
    appointment_list = [{'id': a.id, 'time_slot': a.time_slot.strftime('%Y-%m-%d %H:%M')} for a in appointments]
    return jsonify({'appointments': appointment_list})

