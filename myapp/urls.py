from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('get_batches/', views.getBatches, name='get_batches'),
    path('students/<int:batch_id>/', views.student_list, name='student_list'),  
    path('student/<int:student_id>/<int:batch_id>', views.student_detail, name='student_detail'),
    path('student/<int:student_id>/<int:batch_id>/progress/', views.add_progress, name='add_progress'),
    path("attendance/<int:batch_id>", views.mark_student_attendance, name="student_attendance"),
    path('add_batch/', views.add_batch, name='add_batch'),
    path('register_staff/', views.register_staff, name='register_staff'),

    path('', views.home, name='home'),
]
