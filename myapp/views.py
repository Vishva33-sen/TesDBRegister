from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, StudentTopicProgress, Staff, CourseTopic
from django.contrib import messages
from django.forms import modelformset_factory


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
    topics = CourseTopic.objects.filter(course=student.course).order_by('module_name', 'topic_name')

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
    return render(request, 'student_list.html', {'students': students})


@login_required
def add_progress(request, student_id):
    staff = get_object_or_404(Staff, user=request.user)
    student = get_object_or_404(Student, pk=student_id, staff=staff)

    # ✅ Get all topics for this student's course
    topics = CourseTopic.objects.filter(course=student.course).order_by('module_name', 'topic_name')

    # ✅ Get or create progress objects for each topic (so we always have a row to edit)
    progress_objects = []
    for topic in topics:
        progress, created = StudentTopicProgress.objects.get_or_create(
            student=student,
            topic=topic,
            defaults={'sign': staff.staff_name}
        )
        progress_objects.append(progress)

    # ✅ Create a formset for all progress objects
    ProgressFormSet = modelformset_factory(
        StudentTopicProgress,
        fields=('start_date', 'end_date', 'marks', 'sign'),
        extra=0
    )

    if request.method == "POST":
        formset = ProgressFormSet(request.POST, queryset=StudentTopicProgress.objects.filter(student=student))
        if formset.is_valid():
            formset.save()
            return redirect('student_detail', student_id=student.pk)
    else:
        formset = ProgressFormSet(queryset=StudentTopicProgress.objects.filter(student=student))

    return render(request, 'add_progress.html', {
        'student': student,
        'formset': formset,
        'topics': topics,
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



def staff_logout(request):
    logout(request)
    return redirect('staff_login')