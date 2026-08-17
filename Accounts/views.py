from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .throttles import LoginThrottle, RegisterThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegisterSerializer, UserSerializer

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import PasswordResetConfirmSerializer, RequestPasswordResetSerializer
from .throttles import PasswordResetConfirmThrottle, PasswordResetThrottle


class RegisterView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle] 
  
class MeView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user




class RequestPasswordResetView(APIView):
    """Step 1: send a signed reset link to the given email (if the user exists)."""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = CustomUser.objects.filter(email__iexact=email).first()

        if not user:
            # Same message for existing/non-existing emails -> prevents user enumeration
            return Response({"detail": "If an account exists with this email, a reset link has been sent."})

        token = default_token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_URL}/confirm-reset?email={user.email}&token={token}"

        send_mail(
            subject="Password Reset",
            message=f"Click this link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=f'<p>Click <a href="{reset_url}">here</a> to reset your password.</p>',
        )

        return Response({"detail": "Password reset link sent."})


class PasswordResetConfirmView(APIView):
    """Step 2: validate token + email, then set the new password."""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetConfirmThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = CustomUser.objects.filter(email__iexact=data["email"]).first()

        if not user or not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        user.set_password(data["new_password"])
        user.save(update_fields=["password"])

        return Response({"detail": "Password changed successfully."})