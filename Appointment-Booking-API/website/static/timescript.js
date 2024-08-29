document.addEventListener('DOMContentLoaded', function() {
    const slotContainer = document.querySelector('.time-slot-container');
    let lastSelectedSlot = null;

    function genTimeSlots(startHour, endHour, increment) {
        for (let hour = startHour; hour < endHour; hour++) {
            for (let minute = 0; minute < 60; minute += increment) {
                let hour12 = hour % 12 || 12;
                let amPm = hour < 12 ? 'AM' : 'PM';
                const time = `${hour12}:${String(minute).padStart(2, '0')} ${amPm}`;
                const slotItem = document.createElement('div');
                slotItem.className = 'slot-item';
                slotItem.dataset.time = time;
                slotItem.textContent = time;
                slotItem.addEventListener('click', function() {
                    toggleConfirmButton(slotItem, time);
                });

                slotContainer.appendChild(slotItem);
            }
        }
    }

    function toggleConfirmButton(slot, time) {
        const isConfirming = slot.classList.toggle('confirming');
        if (isConfirming) {
            const button = document.createElement('button');
            button.className = 'confirm-btn';
            button.textContent = 'Confirm';
            button.onclick = function() {
                alert('Confirmed time slot: ' + time);
                slot.classList.remove('confirming');
                if (button) {
                    button.remove();
                }
            };
            slot.appendChild(button);
        } else {
            const button = slot.querySelector('.confirm-btn');
            if (button) {
                button.remove();
            }
        }

        slotContainer.querySelectorAll('.slot-item.confirming').forEach(function(otherSlot) {
            if (otherSlot !== slot) {
                otherSlot.classList.remove('confirming');
                const button = otherSlot.querySelector('.confirm-btn');
                if (button) {
                    button.remove();
                }
            }
        });

        lastSelectedSlot = slot;
    }

    genTimeSlots(9, 17, 30);
});

flatpickr("#calendar", {
    inline: true,
    altInput: true,
    altFormat: "F j, Y",
    dateFormat: "Y-m-d",
    onChange: function(selectedDates, dateStr, instance) {
        const timeSlotsWrapper = document.querySelector('.time-slots-wrapper');
        const selectedDateContainer = document.querySelector('.selected-date');
        if (selectedDates.length > 0) {
            selectedDateContainer.textContent = `${instance.altInput.value}`;
            timeSlotsWrapper.style.display = 'flex'; 
            timeSlotsWrapper.classList.add('active'); 
            document.querySelector('.time-slot-container').style.display = 'block'; 
        } else {
            selectedDateContainer.textContent = '';
            timeSlotsWrapper.style.display = 'none'; 
            timeSlotsWrapper.classList.remove('active');
        }
    }
});
