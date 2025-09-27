document.addEventListener('DOMContentLoaded', function () {
    var courseSel = document.getElementById('id_course');
    var staffSel = document.getElementById('id_staff');
    if (!courseSel || !staffSel) return;

    function updateStaffOptions(courseId, selectedStaffId) {
        if (!courseId) {
            staffSel.innerHTML = '';
            var opt = document.createElement('option');
            opt.value = '';
            opt.textContent = '---------';
            staffSel.appendChild(opt);
            return;
        }

        var url = '/admin/get_staff_by_course/?course_id=' + encodeURIComponent(courseId);
        fetch(url)
            .then(function(response) { return response.json(); })
            .then(function(data) {
                staffSel.innerHTML = '';
                if (data.staff.length === 0) {
                    var opt = document.createElement('option');
                    opt.value = '';
                    opt.textContent = 'No staff for selected course';
                    staffSel.appendChild(opt);
                    return;
                }
                data.staff.forEach(function(s) {
                    var opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = s.name;
                    if (selectedStaffId && selectedStaffId == s.id) opt.selected = true;
                    staffSel.appendChild(opt);
                });
            }).catch(function(err){
                console.error('Error fetching staff:', err);
            });
    }

    // Trigger update when course changes
    courseSel.addEventListener('change', function() {
        updateStaffOptions(this.value);
    });

    // If form already has course + staff selected (edit page), update to reflect that.
    if (courseSel.value) {
        updateStaffOptions(courseSel.value, staffSel.value);
    }
});
