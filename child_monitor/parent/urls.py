from django.contrib import admin
from django.urls import path, include
from . views import ParentView, choice, video_capture
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', ParentView.as_view(), name='signup'),
    path('ai/', views.ai, name='ai'),
    path('login/', auth_views.LoginView.as_view(template_name='parent/login.html'), name='login'),
    path('choice/', views.choice, name='choice'),
    path('videostreaming/' , views.video_capture, name='video'),
    path('audiorecording/', views.audiorecording, name='audio'),
    path('mail/', views.sendmail, name='mail'),
]
