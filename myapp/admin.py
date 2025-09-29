
from django.contrib import admin
from .models import Staff, Course, Student, CourseTopic, StudentTopicProgress
from django.utils.translation import gettext_lazy as _
from django import forms

# Custom list filter that shows course name with staff
class CourseWithStaffFilter(admin.SimpleListFilter):
    title = _('course')
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        # Return each course with staff name in label
        qs = Course.objects.all().order_by('course_name', 'staff__staff_name')
        return [(c.pk, f"{c.course_name} ({c.staff.staff_name})") for c in qs]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(course__pk=value)
        return queryset

class StudentAdminForm(forms.ModelForm):
    # We override the field to make sure we can set label_from_instance
    course = forms.ModelChoiceField(
        queryset=Course.objects.all().order_by('course_name', 'staff__staff_name'),
        required=True
    )
    class Meta:
        model = Student
        fields = ('student_name', 'join_date', 'end_date', 'course','student_email','student_contact','batch','mode')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show course as "Course Name (Staff Name)" in the dropdown
        # label_from_instance exists on ModelChoiceField and can be overridden
        self.fields['course'].label_from_instance = lambda obj: f"{obj.course_name} ({obj.staff.staff_name})"




@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    # form = StudentAdminForm
    list_display = ('staff_id', 'staff_name', 'contact','staff_email')
    list_filter = ('staff_id','staff_name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'staff')
    list_filter = ('staff',)


class StaffByCourseFilter(admin.SimpleListFilter):
    title = _('staff')
    parameter_name = 'staff'

    def lookups(self, request, model_admin):
        # First check if a course is selected in the filter
        course_id = request.GET.get('course')
        if course_id:
            # Get staff related to that course only
            staffs = Staff.objects.filter(course__course_id=course_id).distinct()

        else:
            # Show all staff if no course selected
            staffs = Staff.objects.all().distinct()

        return [(staff.pk, staff.staff_name) for staff in staffs]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(staff_id=value)
        return queryset



@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ('student_id', 'student_name', 'join_date', 'course', 'staff')
    list_filter = (CourseWithStaffFilter,)
    search_fields = ('student_name',)

    def save_model(self, request, obj, form, change):
        # ✅ Automatically assign staff based on selected course
        obj.staff = obj.course.staff
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('course', 'staff').distinct()



@admin.register(CourseTopic)
class CourseTopicAdmin(admin.ModelAdmin):
    list_display = ('topic_id', 'course', 'module_name', 'topic_name')
    list_filter = ('course', 'module_name')

