from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, StudentTopicProgress, Staff, CourseTopic , Attendance , StudentAttendance
from django.contrib import messages
from django.forms import modelformset_factory
from django import forms
from django.utils.timezone import now,localdate,datetime
from django.utils import timezone
from django.urls import reverse
from datetime import date


def home(request):
    return render(request, 'home.html')

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    # ✅ Only allow staff to see their own students
    if hasattr(request.user, 'staff'):
        if student.staff != request.user.staff:
            return redirect('home')

    # ✅ Fetch all topics for the student's course
    # topics = CourseTopic.objects.filter(course=student.course).order_by('module_name', 'topic_name')
    topics = CourseTopic.objects.filter(course=student.course).order_by('topic_id')


    # ✅ Get progress for each topic (or None if not yet added)
    progress_dict = {
        p.topic_id: p for p in StudentTopicProgress.objects.filter(student=student)
    }

    # Build a list with topic + progress (if exists)
    topic_progress_list = []
    for topic in topics:
        topic_progress_list.append({
            "topic": topic,
            "progress": progress_dict.get(topic.pk)
        })

    return render(request, 'student_detail.html', {
        'student': student,
        'topic_progress_list': topic_progress_list
    })

@login_required
def student_list(request):
    staff = get_object_or_404(Staff, user=request.user)
    students = Student.objects.filter(staff=staff)

    today = localdate()
    attendance=Attendance.objects.filter(staff=staff,date=today).last()
    print(attendance)
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, pk=student_id, staff=staff)

        # Update batch and mode
        batch = request.POST.get('batch')
        mode = request.POST.get('mode')

        if batch in ['True', 'False']:
            student.batch = True if batch == 'True' else False
        if mode in ['True', 'False']:
            student.mode = True if mode == 'True' else False

        student.save()
        return redirect('student_list')
    return render(request, 'student_list.html', {'students': students , 'attendance':attendance})


@login_required
def add_progress(request, student_id):
    staff = get_object_or_404(Staff, user=request.user)
    student = get_object_or_404(Student, pk=student_id, staff=staff)

    # Ensure all topics exist for this student
    topics = CourseTopic.objects.filter(course=student.course).order_by('topic_id')
    for topic in topics:
        StudentTopicProgress.objects.get_or_create(
            student=student,
            topic=topic
        )

    class ProgressForm(forms.ModelForm):
        class Meta:
            model = StudentTopicProgress
            fields = ('start_date', 'end_date', 'marks')
            widgets = {
                'start_date': forms.DateInput(attrs={'type': 'date'}),
                'end_date': forms.DateInput(attrs={'type': 'date'}),
            }

    ProgressFormSet = modelformset_factory(
        StudentTopicProgress,
        form=ProgressForm,
        extra=0
    )

    queryset = StudentTopicProgress.objects.filter(student=student).order_by('topic__topic_id')

    if request.method == "POST":
        formset = ProgressFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            for form in formset.forms:
                progress = form.save(commit=False)
                if form.has_changed():
                    progress.sign = staff.staff_name
                progress.save()
                form.save_m2m()
            return redirect('student_detail', student_id=student.pk)
        else:
            print("Formset errors:", formset.errors)
            print("Non-form errors:", formset.non_form_errors())

    else:
        formset = ProgressFormSet(queryset=queryset)

    topic_form_pairs = list(zip(formset.forms, topics))

    return render(request, 'add_progress.html', {
        'student': student,
        'formset': formset,
        'topic_form_pairs': topic_form_pairs,
    })



def staff_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # ✅ Redirect staff to student list (not back to home)
            if hasattr(user, 'staff'):
                return redirect('student_list')
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'staff_login.html')

# def get_staff(self, request):
#     course_id = request.GET.get('course_id')
#     staff_list = []
#     if course_id:
#         staffs = Staff.objects.filter(courses__course_id=course_id)
#         staff_list = [{"id": s.staff_id, "name": s.staff_name} for s in staffs]
#     return JsonResponse(staff_list, safe=False)


@login_required
def mark_student_attendance(request):
    staff = get_object_or_404(Staff, user=request.user)
    students = Student.objects.filter(staff=staff)
    today = timezone.now().date()

    # --- Get the selected date (POST first, then GET) ---
    date_str = request.POST.get("date") or request.GET.get("date")
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    # Prevent future dates
    if selected_date > today:
        selected_date = today

    # --- Save attendance if POST ---
    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.student_id}")
            if status is not None:
                status_bool = True if status == "present" else False
                attendance, created = StudentAttendance.objects.get_or_create(
                    student=student,
                    date=selected_date,
                    defaults={"status": status_bool}
                )
                if not created:
                    attendance.status = status_bool
                    attendance.save()
        # Redirect back to the same selected date
        return redirect(f"{reverse('student_attendance')}?date={selected_date.strftime('%Y-%m-%d')}")

    # --- Load attendance for selected date ---
    attendance_records = {
        att.student_id: att
        for att in StudentAttendance.objects.filter(date=selected_date, student__in=students)
    }

    return render(request, "student_attendance.html", {
        "students": students,
        "attendance_records": attendance_records,
        "today": today.strftime("%Y-%m-%d"),
        "selected_date": selected_date.strftime("%Y-%m-%d"),
    })

def staff_logout(request):
    logout(request)
    return redirect('staff_login')