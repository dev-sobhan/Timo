from django.urls import path
from .views import (RegisterApiView, ProfileViewSet)

app_name = 'users'

urlpatterns = [
    path("register/", RegisterApiView.as_view(), name="register"),
    path("profile/", ProfileViewSet.as_view({
        "patch": "partial_update",
        "get": "list"
    }), name="profile"),
]
