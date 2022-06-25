from django.urls import path

from .views import SignUpView, ActivateView, Login, Verification, ProfileView, AfterLogin

app_name = 'accounts'
urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", Login.as_view(), name="login"),
    path("afterlogin/", AfterLogin, name="after_login"),
    path("verification/", Verification.as_view(), name="verification"),
    path("activate/<uidb64>/<token>/", ActivateView.as_view(), name="activate"),
    path("profile/", ProfileView, name="profile"),
]