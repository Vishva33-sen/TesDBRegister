from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Staff, Course, Student, CourseTopic, StudentTopicProgress, Attendance , StudentAttendance
from django.urls import path
from django.http import JsonResponse

# ----------------------------
# Course With Staff Filter
# ----------------------------
class CourseWithStaffFilter(admin.SimpleListFilter):
    title = _('course')
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        qs = Course.objects.all().order_by('course_name')
        return [
            (c.pk, f"{c.course_name} ({', '.join([s.staff_name for s in c.staffs.all()])})")
            for c in qs
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(course__pk=value)
        return queryset


# ----------------------------
# Student Form (show staff in course name)
# ----------------------------

class StudentAdminForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True)
    staff = forms.ModelChoiceField(queryset=Staff.objects.none(), required=True)

    class Meta:
        model = Student
        fields = ('student_name', 'join_date', 'end_date', 'course', 'staff', 
                  'student_email', 'student_contact', 'batch', 'mode')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                self.fields['staff'].queryset = Staff.objects.filter(courses__course_id=course_id)

            except (ValueError, TypeError):
                self.fields['staff'].queryset = Staff.objects.none()
        elif self.instance.pk and self.instance.course:
            self.fields['staff'].queryset = self.instance.course.staffs.all()




# ----------------------------
# Staff Admin
# ----------------------------
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'staff_name', 'contact', 'staff_email','get_courses')
    list_filter = ('staff_id', 'staff_name')

    def get_courses(self, obj):
        # Join all course names assigned to this staff
        return ", ".join([course.course_name for course in obj.courses.all()])
    get_courses.short_description = "Courses"


# ----------------------------
# Course Admin
# ----------------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'get_staff_names')

    def get_staff_names(self, obj):
        return ", ".join([s.staff_name for s in obj.staffs.all()])
    get_staff_names.short_description = "Staff"


# ----------------------------
# Staff by Course Filter
# ----------------------------
class StaffByCourseFilter(admin.SimpleListFilter):
    title = _('staff')
    parameter_name = 'staff'

    def lookups(self, request, model_admin):
        course_id = request.GET.get('course')
        if course_id:
            staffs = Staff.objects.filter(courses__course_id=course_id).distinct()
        else:
            staffs = Staff.objects.all().distinct()
        return [(staff.pk, staff.staff_name) for staff in staffs]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(staff_id=value)
        return queryset


# ----------------------------
# Student Admin
# ----------------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ('student_id', 'student_name', 'join_date', 'course', 'staff')
    list_filter = (CourseWithStaffFilter,)
    search_fields = ('student_name',)

    class Media:
        js = ("myapp/student_admin.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get_staff/', self.admin_site.admin_view(self.get_staff), name='get_staff'),
        ]
        return custom_urls + urls

    def get_staff(self, request):
        course_id = request.GET.get('course_id')
        staff_list = []
        if course_id:
            staffs = Staff.objects.filter(courses__course_id=course_id)
            staff_list = [{"id": s.staff_id, "name": s.staff_name} for s in staffs]
        return JsonResponse(staff_list, safe=False)




# ----------------------------
# Course Topic Admin
# ----------------------------
@admin.register(CourseTopic)
class CourseTopicAdmin(admin.ModelAdmin):
    list_display = ('topic_id', 'course', 'module_name', 'topic_name')
    list_filter = ('course', 'module_name')


# ----------------------------
# Attendance Admin
# ----------------------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("staff", "date", "time", "wifi_verified")
    list_filter = ("staff", "date", "wifi_verified")
    search_fields = ("staff__staff_name",)



@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "student_course", "student_staff", "date", "status")
    list_filter = ("status", "date", "student__course__course_name", "student__staff__staff_name")
    search_fields = ("student__student_name", "student__staff__staff_name", "student__course__course_name")

    def student_course(self, obj):
        return obj.student.course.course_name
    student_course.admin_order_field = "student__course__course_name"

    def student_staff(self, obj):
        return obj.student.staff.staff_name
    student_staff.admin_order_field = "student__staff__staff_name"
