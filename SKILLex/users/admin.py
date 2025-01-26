from django.contrib import admin
from .models import Profile, Skill, MatchRequest, Message, Notification

# Register your models here.
admin.site.register(Profile)
admin.site.register(Skill)
admin.site.register(Message)
admin.site.register(Notification)

@admin.register(MatchRequest)
class MatchRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'sender_skill', 'receiver_skill', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username')
