from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    CreateManagerView,
    UserListView,
    ConfirmUserView,
    ActivateUserView,
    PasswordResetView,
    PasswordResetConfirmView,
    ChangePasswordView, CustomTokenObtainPairView, UserProfileView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('create-manager/', CreateManagerView.as_view(), name='create-manager'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('activate/', ActivateUserView.as_view(), name='activate-user'),
    path('confirm/<int:pk>/', ConfirmUserView.as_view(), name='confirm-user'),
    # JWT авторизация и вход
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # смена пароля
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
