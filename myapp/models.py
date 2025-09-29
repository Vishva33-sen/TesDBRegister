from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_name =models.CharField(max_length=100)
    contact=models.CharField(max_length=20,blank=True)
    staff_id = models.AutoField(primary_key=True)
    staff_email = models.EmailField(unique=True)

    def __str__(self):
        return self.staff_name

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.course_name

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=100)
    join_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='students')
    student_email = models.EmailField(unique=True)
    student_contact = models.CharField(max_length=20, blank=True)
    BATCH_CHOICES = [
        (True, 'Morning'),
        (False, 'Afternoon'),
    ]
    batch = models.BooleanField(choices=BATCH_CHOICES, default=True)

    MODE_CHOICES = [
        (True, 'Offline'),
        (False, 'Online'),
    ]
    mode = models.BooleanField(choices=MODE_CHOICES, default=True)


    def __str__(self):
        return f"{self.student_name} ({self.course.course_name} - {self.staff.staff_name})"

class CourseTopic(models.Model):
    topic_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    module_name = models.CharField(max_length=100)
    topic_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('course', 'module_name', 'topic_name')

    def __str__(self):
        return f"{self.module_name} - {self.topic_name}"

class StudentTopicProgress(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress')
    topic = models.ForeignKey(CourseTopic, on_delete=models.CASCADE, related_name='progress')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    marks = models.IntegerField(null=True, blank=True)
    sign = models.CharField(max_length=100, help_text="Staff full name")

    class Meta:
        unique_together = ('student', 'topic')

    def __str__(self):
        return f"{self.student.student_name} - {self.topic.topic_name}"







