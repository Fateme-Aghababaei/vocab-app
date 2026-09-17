from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.throttling import AnonRateThrottle
from .email_codes import send_code, check_code
from .models import EmailCode
from .serializers import EmailSerializer, VerifyCodeSerializer, ResetPasswordSerializer
# accounts/views.py
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserProfile
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserSerializer,
)


class AuthThrottle(AnonRateThrottle):
    rate = "20/hour"


class PublicAuthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [AuthThrottle]


class RegisterView(PublicAuthView):
    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_code(user, "signup")
        return Response({"email": user.email, "detail": "Check your email for a verification code."}, status=201)


class SendCodeView(PublicAuthView):
    purpose = "signup"

    @transaction.atomic
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.select_for_update().filter(username=serializer.validated_data["email"]).first()
        if user and ((self.purpose == "reset" and user.is_active) or (
            self.purpose == "signup" and not user.is_active
            and EmailCode.objects.filter(user=user, purpose="signup").exists()
        )):
            send_code(user, self.purpose)
        return Response({"detail": "If this email is eligible, a code has been sent. Wait 60 seconds before requesting another."})


class ForgotPasswordView(SendCodeView):
    purpose = "reset"


class VerifyEmailView(PublicAuthView):
    @transaction.atomic
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = User.objects.select_for_update().filter(username=data["email"], is_active=False).first()
        if not user or not check_code(user, "signup", data["code"]):
            return Response({"detail": "Invalid or expired code. Request a new code if needed."}, status=400)
        user.is_active = True
        user.save(update_fields=["is_active"])
        EmailCode.objects.filter(user=user, purpose="signup").delete()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class ResetPasswordView(PublicAuthView):
    @transaction.atomic
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = User.objects.select_for_update().filter(username=data["email"], is_active=True).first()
        if not user or not check_code(user, "reset", data["code"]):
            return Response({"detail": "Invalid or expired code. Request a new code if needed."}, status=400)
        user.set_password(data["password"])
        user.save(update_fields=["password"])
        EmailCode.objects.filter(user=user, purpose="reset").delete()
        Token.objects.filter(user=user).delete()
        return Response({"detail": "Password updated. Log in with your new password."})


class LoginView(PublicAuthView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

# در accounts/views.py:
from django.conf import settings
from .models import PushSubscription


class VapidPublicKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"publicKey": settings.VAPID_PUBLIC_KEY})


class PushSubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        endpoint = request.data.get("endpoint")
        keys = request.data.get("keys", {})
        p256dh = keys.get("p256dh")
        auth = keys.get("auth")

        if not endpoint or not p256dh or not auth:
            return Response({"detail": "Invalid subscription payload"}, status=status.HTTP_400_BAD_REQUEST)

        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={"user": request.user, "p256dh": p256dh, "auth": auth},
        )
        return Response({"status": "subscribed"}, status=status.HTTP_201_CREATED)