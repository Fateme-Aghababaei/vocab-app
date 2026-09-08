from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer, StudyLanguageSerializer
from .models import StudyProfile
from .languages import LANGUAGES
from django.db import transaction


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
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


    def patch(self, request):
        serializer = StudyLanguageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        language = serializer.validated_data["language"]
        with transaction.atomic():
            profile, _ = StudyProfile.objects.select_for_update().get_or_create(user=request.user)
            if language not in profile.languages:
                profile.languages = [*profile.languages, language]
            profile.active_language = language
            profile.save(update_fields=["languages", "active_language"])
        return Response(UserSerializer(request.user).data)


class LanguagesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response([{"code": code, "name": name} for code, name in LANGUAGES.items()])
