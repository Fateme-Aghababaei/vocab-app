from django.urls import path
from .views import RegisterView, LoginView, LogoutView, MeView, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("profile/", ProfileView.as_view(), name="user-profile"),  # new
]