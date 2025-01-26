from django import template

register = template.Library()

@register.filter
def get_room_id(match_request, user):
    user1_id = match_request.sender.id
    user2_id = match_request.receiver.id
    return f"chat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}" 