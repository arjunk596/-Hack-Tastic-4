from django.db import models
from django.contrib.auth.models import User

# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Skill Model
class Skill(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('amateur', 'Amateur'),
        ('pro', 'Pro'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=100)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)

    def __str__(self):
        return f"{self.skill_name} ({self.level})"

# MatchRequest Model
class MatchRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    sender_skill = models.ForeignKey(Skill, related_name='sent_skill', on_delete=models.CASCADE)
    receiver_skill = models.ForeignKey(Skill, related_name='received_skill', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Declined', 'Declined')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} matched with {self.receiver.username} for {self.sender_skill.skill_name}"

    class Meta:
        ordering = ['-created_at']

# Message Model
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    room_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

    @staticmethod
    def get_room_id(user1_id, user2_id):
        return f"chat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

# Notification Model
class Notification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    NOTIFICATION_TYPES = [
        ('trade_request', 'Trade Request'),
        ('request_accepted', 'Request Accepted'),
        ('request_declined', 'Request Declined'),
    ]
    
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    sender_skill = models.ForeignKey(Skill, related_name='sent_trade_requests', on_delete=models.CASCADE, null=True)
    requested_skill = models.ForeignKey(Skill, related_name='received_trade_requests', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade request from {self.sender.username} to {self.recipient.username}"

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MatchRequest, Skill
from django.contrib.auth.models import User

@login_required
def request_match(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        sender_skill_id = request.POST.get('sender_skill_id')
        receiver_skill_id = request.POST.get('receiver_skill_id')
        
        receiver = get_object_or_404(User, id=receiver_id)
        sender_skill = get_object_or_404(Skill, id=sender_skill_id)
        receiver_skill = get_object_or_404(Skill, id=receiver_skill_id)
        
        MatchRequest.objects.create(
            sender=request.user,
            receiver=receiver,
            sender_skill=sender_skill,
            receiver_skill=receiver_skill,
            status='Pending'
        )
        return redirect('dashboard')
    return redirect('home')
