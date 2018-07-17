"""Views that don't fit anywhere else."""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets

from roles.helpers import login_required_ajax
from bodies.models import Body
from bodies.serializer_min import BodySerializerMin
from events.models import Event
from events.serializers import EventSerializer
from events.prioritizer import get_prioritized
from users.models import UserProfile
from users.serializers import UserProfileSerializer
from other.notifications import NotificationSerializer
from helpers.misc import query_search

class OtherViewset(viewsets.ViewSet):

    @staticmethod
    def search(request):
        """EXPENSIVE: Search with query param `query` throughout the database."""
        MIN_LENGTH = 3

        req_query = request.GET.get("query")
        if not req_query or len(req_query) < MIN_LENGTH:
            return Response({"message": "No query or too short!"}, status=400)

        # Search bodies by name and description
        bodies = query_search(request, MIN_LENGTH, Body.objects, ['name', 'description'])

        # Search events by name and description
        events = get_prioritized(query_search(request, MIN_LENGTH, Event.objects, ['name', 'description']), request)

        # Search users by only name: don't add anything else here
        users = query_search(request, MIN_LENGTH, UserProfile.objects, ['name'])

        return Response({
            "bodies": BodySerializerMin(bodies, many=True).data,
            "events": EventSerializer(events, many=True).data,
            "users": UserProfileSerializer(users, many=True).data
        })

    @classmethod
    @login_required_ajax
    def get_notifications(cls, request):
        """Get unread notifications for current user."""
        notifications = request.user.notifications.unread()
        return Response(NotificationSerializer(notifications, many=True).data)

    @classmethod
    @login_required_ajax
    def mark_notification_read(cls, request, pk):
        """Mark one notification as read."""
        notification = get_object_or_404(request.user.notifications, id=pk)
        notification.mark_as_read()
        return Response(status=204)

    @classmethod
    @login_required_ajax
    def mark_all_notifications_read(cls, request):
        """Mark all notifications as read."""
        request.user.notifications.mark_all_as_read()
        return Response(status=204)
