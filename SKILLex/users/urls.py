from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_skill/', views.add_skill, name='add_skill'),
    path('match_users/', views.match_users, name='match_users'),
    path('request_match/', views.request_match, name='request_match'),
    path('notifications/', views.notifications, name='notifications'),
    path('chat/<int:match_id>/', views.chat, name='chat'),
    path('send_message/', views.send_message, name='send_message'),
    path('respond_to_request/<int:notification_id>/', views.respond_to_request, name='respond_to_request'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
]
