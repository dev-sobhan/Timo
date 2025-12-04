from django.urls import path, include

urlpatterns = [
    path('api/users/', include('users.urls', namespace='users')),
    path('api/teams/', include('teams.urls', namespace='teams')),
]
