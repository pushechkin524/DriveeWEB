from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import User, Role
from .serializers import UserSerializer, RoleSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrReadOnly]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-user_id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]
