from django.urls import path
from .views import *

urlpatterns = [
    path("", UserView.as_view(), name='user-view'),
    path("register/", UserRegistrationView.as_view(), name='user-registration'),
    path("update/", UserUpdateView.as_view(), name='user-update'),
    path("reset_password/", PasswordReset.as_view(), name="request-password-reset"),
    path("password-reset/<str:encoded_pk>/<str:token>/", ResetPasswordAPI.as_view(), name="reset-password"),
]
