from django.urls import path
from .views import RegisterView, LoginView, LogoutView, MeView, ProfileView, SendCodeView, VerifyEmailView, \
    ForgotPasswordView, ResetPasswordView, VapidPublicKeyView, PushSubscribeView

urlpatterns = [
    path("verify-email/", VerifyEmailView.as_view(), name="auth-verify-email"),
    path("resend-code/", SendCodeView.as_view(), name="auth-resend-code"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("profile/", ProfileView.as_view(), name="user-profile"),  # new
    path("vapid-key/", VapidPublicKeyView.as_view(), name="vapid-key"),
    path("push-subscribe/", PushSubscribeView.as_view(), name="push-subscribe"),
]