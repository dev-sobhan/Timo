from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from utils.response import success_response

from ..mongo.message_repository import MessageRepository


class ChatMessageListApi(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, chat_id):
        messages = MessageRepository.fetch_messages(
            chat_id=chat_id,
            limit=int(request.query_params.get("limit", 100)),
            before=request.query_params.get("before"),
        )
        return success_response(messages)
