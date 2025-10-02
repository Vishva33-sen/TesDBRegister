document.addEventListener("DOMContentLoaded", function() {
    const courseSelect = document.getElementById("id_course");
    const staffSelect = document.getElementById("id_staff");

    if (!courseSelect || !staffSelect) return;

    function populateStaff() {
        const courseId = courseSelect.value;
        if (!courseId) {
            staffSelect.innerHTML = '';
            return;
        }

        // Absolute URL for admin endpoint
        const url = '/admin/myapp/student/get_staff/?course_id=' + courseId;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                staffSelect.innerHTML = '';
                if (data.length === 0) {
                    const option = document.createElement('option');
                    option.text = 'No staff assigned';
                    option.value = '';
                    staffSelect.appendChild(option);
                    return;
                }

                data.forEach(staff => {
                    const option = document.createElement('option');
                    option.value = staff.id;       // must match view JSON 'id'
                    option.text = staff.name;
                    staffSelect.appendChild(option);
                });

                // Preserve currently selected staff
                if (staffSelect.getAttribute('data-current')) {
                    staffSelect.value = staffSelect.getAttribute('data-current');
                }
            })
            .catch(err => {
                console.error('Error fetching staff:', err);
                staffSelect.innerHTML = '';
                const option = document.createElement('option');
                option.text = 'Error loading staff';
                option.value = '';
                staffSelect.appendChild(option);
            });
    }

    // Store currently selected staff on edit page
    if (staffSelect.value) {
        staffSelect.setAttribute('data-current', staffSelect.value);
    }

    courseSelect.addEventListener('change', populateStaff);

    // Populate staff immediately
    populateStaff();
});
