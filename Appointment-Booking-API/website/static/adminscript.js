function displayAppointments() {
  var appointmentContainer = document.getElementById('appointment-container');
  var createAppointmentContainer = document.getElementById('create-appointment-container');
  var availabilityContainer = document.getElementById('availability-container');

  appointmentContainer.style.display = 'block';
  createAppointmentContainer.style.display = 'none';
  availabilityContainer.style.display = 'none';

}

function displayCreateAppointment() {
  var appointmentContainer = document.getElementById('appointment-container');
  var createAppointmentContainer = document.getElementById('create-appointment-container');
  var availabilityContainer = document.getElementById('availability-container');

  appointmentContainer.style.display = 'none';
  createAppointmentContainer.style.display = 'block';
  availabilityContainer.style.display = 'none';
}


function displayAvailability() {
  var appointmentContainer = document.getElementById('appointment-container');
  var createAppointmentContainer = document.getElementById('create-appointment-container');
  var availabilityContainer = document.getElementById('availability-container');

  appointmentContainer.style.display = 'none';
  createAppointmentContainer.style.display = 'none';
  availabilityContainer.style.display = 'block';
}


function goToNextStep(stepId) {
  const appointmentName = document.getElementById('appointmentName').value.trim();
  const appointmentDuration = document.getElementById('appointmentDuration').value;

  if (!appointmentName || !appointmentDuration) {
      alert('Please enter an appointment name and select a duration.');
      return;
  }

  document.querySelectorAll('.step-section').forEach(function(section) {
      section.style.display = 'none';
  });

  document.getElementById(stepId).style.display = 'block';
}

document.getElementById('availabilityForm').addEventListener('submit', function(event) {
  const startTime = document.getElementById('startTimePicker').value;
  const endTime = document.getElementById('endTimePicker').value;

  if (startTime >= endTime) {
      event.preventDefault();
      alert('Start time must be before the end time.');
  }

  var checkboxes = document.querySelectorAll('input[name="days"]:checked');
  if (checkboxes.length === 0) {
      event.preventDefault();
      alert('Please select at least one day.');
      return;
  }
});

document.getElementById('appointmentDuration').addEventListener('change', function() {
  var submitBtn = document.getElementById('submitAppointmentBtn');
  if (this.value !== "") {
      submitBtn.removeAttribute('disabled');
  } else {
      submitBtn.setAttribute('disabled', 'disabled');
  }
});

document.getElementById('appointmentForm').addEventListener('submit', function(event) {
  const appointmentName = document.getElementById('appointmentName').value.trim();
  const appointmentDuration = document.getElementById('appointmentDuration').value;

  if (!appointmentName || !appointmentDuration) {
      event.preventDefault();
      alert('Please enter an appointment name and select a duration.');
  }
});

document.addEventListener('DOMContentLoaded', function() {
  displayAppointments();
});