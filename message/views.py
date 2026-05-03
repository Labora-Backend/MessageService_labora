from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Message
from .serializers import MessageSerializer
from .permissions import IsAdmin, IsClient, IsFreelancer


@api_view(["GET"])
@permission_classes([IsAuthenticated, (IsClient | IsFreelancer | IsAdmin)])
def chat_history(request):
    job_id = request.query_params.get("job_id")
    user_id = request.user.id

    if not job_id:
        return Response( {"error": "job_id is required"}, status=status.HTTP_400_BAD_REQUEST  )

    messages = Message.objects.filter(
        job_id=job_id
    ).filter(
        sender_id=user_id
    ) | Message.objects.filter(
        job_id=job_id,
        receiver_id=user_id
    )

    messages = messages.order_by("created_at")

    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
