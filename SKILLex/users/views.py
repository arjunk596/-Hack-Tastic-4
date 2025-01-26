from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .models import Profile, Skill, MatchRequest, Message, Notification
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm
from django.db.models import Q

def register(request):
    """
    Handles the user registration process.
    If the request method is POST, it processes the form data and creates a new user.
    If the request method is GET, it renders the registration form.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    """
    Renders the home template.
    This is the main landing page of the application.
    """
    return render(request, 'users/home.html')

@login_required
def respond_to_request(request, notification_id):
    notification = get_object_or_404(MatchRequest, id=notification_id, receiver=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            notification.status = 'accepted'
        elif action == 'decline':
            notification.status = 'declined'
        notification.save()
    return redirect('notifications')

@login_required
def received_requests(request):
    """
    Displays the match requests received by the logged-in user.
    """
    received_requests = MatchRequest.objects.filter(receiver=request.user, status='pending')
    return render(request, 'users/received_requests.html', {'received_requests': received_requests})

@login_required
def dashboard(request):
    """
    Renders the dashboard template for the logged-in user.
    This is the main dashboard where the user can see an overview of their activities.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')
    else:
        profile_form = ProfileForm(instance=profile)
    
    user_skills = Skill.objects.filter(user=request.user)
    return render(request, 'users/dashboard.html', {'profile_form': profile_form, 'user_skills': user_skills})

@login_required
def add_skill(request):
    """
    Handles the addition of a new skill by the user.
    If the request method is POST, it processes the form data and creates a new skill.
    If the request method is GET, it renders the add skill form.
    """
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        level = request.POST.get('level')
        if skill_name and level:
            Skill.objects.create(user=request.user, skill_name=skill_name, level=level)
            messages.success(request, "Skill added successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please enter a valid skill name and level.")
    return render(request, 'users/add_skill.html')

@login_required
def match_users(request):
    """
    Handles the matching of users based on their skills.
    This view will find users with matching skills and create match requests.
    """
    matches = None
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        if skill_name:
            matches = Skill.objects.filter(skill_name__icontains=skill_name).exclude(user=request.user)
            if not matches:
                messages.info(request, "No matches found.")
        else:
            messages.error(request, "Please enter a valid skill name.")
    return render(request, 'users/match_users.html', {'matches': matches})

@login_required
def request_match(request):
    """
    Handles the creation of a trade request between users.
    """
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        sender_skill_id = request.POST.get('sender_skill_id')
        receiver_skill_id = request.POST.get('requested_skill_id')
        
        try:
            receiver = get_object_or_404(User, id=receiver_id)
            sender_skill = get_object_or_404(Skill, id=sender_skill_id)
            receiver_skill = get_object_or_404(Skill, id=receiver_skill_id)
            
            # Add debug prints
            print(f"Creating match request:")
            print(f"Sender: {request.user.username}")
            print(f"Receiver: {receiver.username}")
            print(f"Sender Skill: {sender_skill.skill_name}")
            print(f"Receiver Skill: {receiver_skill.skill_name}")
            
            # Create match request
            match_request = MatchRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                sender_skill=sender_skill,
                receiver_skill=receiver_skill,
                status='Pending'
            )
            
            print(f"Match request created with ID: {match_request.id}")
            messages.success(request, f"Trade request sent to {receiver.username}")
            return redirect('notifications')
            
        except Exception as e:
            print(f"Error creating match request: {str(e)}")
            messages.error(request, f"Error creating match request: {str(e)}")
            return redirect('match_users')
            
    return redirect('match_users')

@login_required
def notifications(request):
    """
    Display user notifications including sent and received match requests
    """
    # Get match requests received by the user
    received_requests = MatchRequest.objects.filter(
        receiver=request.user
    ).select_related('sender', 'sender_skill', 'receiver_skill').order_by('-created_at')
    
    # Get match requests sent by the user
    sent_requests = MatchRequest.objects.filter(
        sender=request.user
    ).select_related('receiver', 'sender_skill', 'receiver_skill').order_by('-created_at')
    
    return render(request, 'users/notifications.html', {
        'received_notifications': received_requests,
        'sent_notifications': sent_requests
    })

@login_required
def mark_notification_as_read(request, notification_id):
    """
    Marks a notification as read.
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def chat(request, match_id):
    match = get_object_or_404(MatchRequest, id=match_id)
    if request.user != match.sender and request.user != match.receiver:
        return redirect('home')
    
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=match.receiver) |
        Q(sender=match.receiver, receiver=request.user)
    ).order_by('timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=match.receiver if request.user == match.sender else match.sender,
                content=content
            )
        return redirect('chat', match_id=match.id)
    
    return render(request, 'users/chat.html', {
        'match': match,
        'messages': messages
    })

@login_required
def send_message(request):
    """
    Handles sending a message from one user to another.
    If the request method is POST, it processes the form data and creates a new message.
    """
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        receiver = get_object_or_404(User, id=receiver_id)
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            messages.success(request, "Message sent successfully.")
            return redirect('notifications')
        else:
            messages.error(request, "Please enter a valid message.")
    return render(request, 'users/send_message.html')

@login_required
def profile(request, user_id):
    """
    Renders the profile template for the specified user.
    This view will display the profile and skills of the specified user.
    """
    user_profile = get_object_or_404(Profile, user_id=user_id)
    user_skills = Skill.objects.filter(user=user_profile.user)
    return render(request, 'users/profile.html', {'profile': user_profile, 'skills': user_skills})

@login_required
def request_trade(request):
    """
    Handle skill trade requests between users
    """
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        sender_skill_id = request.POST.get('sender_skill_id')
        requested_skill_id = request.POST.get('requested_skill_id')
        
        recipient = get_object_or_404(User, id=recipient_id)
        sender_skill = get_object_or_404(Skill, id=sender_skill_id, user=request.user)
        requested_skill = get_object_or_404(Skill, id=requested_skill_id, user=recipient)
        
        # Create notification for trade request
        notification = Notification.objects.create(
            sender=request.user,
            recipient=recipient,
            notification_type='trade_request',
            sender_skill=sender_skill,
            requested_skill=requested_skill,
            status='pending'
        )
        
        messages.success(request, f"Trade request sent to {recipient.username}")
        return redirect('notifications')
    
    return redirect('match_users')

@login_required
def respond_to_trade(request, notification_id):
    """
    Handle responses to trade requests
    """
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user,
        notification_type='trade_request'
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            notification.status = 'accepted'
            notification.notification_type = 'request_accepted'
            notification.save()
            
            # Create a chat room for the users
            room_id = Message.get_room_id(notification.sender.id, notification.recipient.id)
            
            # Create acceptance notification for sender
            Notification.objects.create(
                sender=request.user,
                recipient=notification.sender,
                notification_type='request_accepted',
                sender_skill=notification.requested_skill,
                requested_skill=notification.sender_skill,
                status='accepted'
            )
            
            messages.success(request, f"You have accepted the trade request from {notification.sender.username}")
            return redirect('chat', room_id=room_id)
            
        elif action == 'decline':
            notification.status = 'declined'
            notification.notification_type = 'request_declined'
            notification.save()
            
            messages.info(request, f"You have declined the trade request from {notification.sender.username}")
            
        notification.is_read = True
        notification.save()
        
    return redirect('notifications')

def logout_view(request):
    """
    Handle user logout and redirect to home page
    """
    logout(request)
    return redirect('home')