from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('students/', views.student_list, name='student_list'),  # ✅ Add this
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/<int:student_id>/progress/', views.add_progress, name='add_progress'),

    path('', views.home, name='home'),
]
