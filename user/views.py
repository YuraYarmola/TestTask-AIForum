from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics, response
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from AIForum.settings import HOST
from .models import CustomUser
from .serializers import UserRegistrationSerializer
from user import serializers
from utils import Email


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["user"])
    def get(self, request):
        user = CustomUser.objects.filter(id=request.user.id).first()
        resp = serializers.CustomUserSerializer(user)
        if user:
            return response.Response(resp.data, status=status.HTTP_200_OK)
        else:
            return response.Response(
                {"message": "User doesn't exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@swagger_auto_schema(tags=["user"])
class UserUpdateView(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.id)


class UserRegistrationView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=["user"])
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordReset(generics.GenericAPIView):
    """
    Request for Password Reset Link.
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.EmailSerializer

    @swagger_auto_schema(tags=["user"])
    def post(self, request):
        """
        Create token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]
        user = CustomUser.objects.filter(email=email).first()
        if user:
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = reverse(
                "reset-password",
                kwargs={"encoded_pk": encoded_pk, "token": token},
            )
            reset_link = f"http://{HOST}/{reset_url}"
            # myapp/views.py

            subject = 'AI FORUM password reset'
            message = f"Dear {user.first_name},\n" \
                      f"You are receiving this email because a request to reset your password has been made. " \
                      f"\nIf you did not make this request, please ignore this email.\n" \
                      f"To reset your password, click on the following link:\n" \
                      f"{reset_link}\n" \

            recipient_list = [user.email]  # Replace with the recipient's email addresses

            Email.send_email(subject, message, recipient_list)

            return response.Response(
                {
                    "message":
                    f"Your password was sent"
                },
                status=status.HTTP_200_OK,
            )
        else:
            return response.Response(
                {"message": "User doesn't exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordAPI(generics.GenericAPIView):
    """
    Verify and Reset Password Token View.
    """

    serializer_class = serializers.ResetPasswordSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=["user"])
    def patch(self, request, *args, **kwargs):
        """
        Verify token & encoded_pk and then reset the password.
        """
        serializer = self.serializer_class(
            data=request.data, context={"kwargs": kwargs}
        )
        try:
            serializer.is_valid(raise_exception=True)
            return response.Response(
                {"message": "Password reset complete"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return response.Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
