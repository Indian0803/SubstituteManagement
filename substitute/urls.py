from django.urls import path
from django.contrib import admin
from django.conf.urls import include
from . import views

urlpatterns = [
    path('', views.loginPage, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('teacher/', views.teacher_home, name='teacher_home'),
    path('teacher/schedule', views.teacher_schedule, name='teacher_schedule'),
    path('teacher/absence', views.absence_report_day, name='absence_report_day'),
    path('teacher/absence/period', views.absence_report_period,
         name='absence_report_period'),
    path('confirm/<str:pk>', views.confirm, name='confirm'),
    path('deny/<str:pk>', views.deny, name='deny')
]
