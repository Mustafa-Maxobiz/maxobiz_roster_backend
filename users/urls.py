from django.urls import path
from users.views.auth import LoginView, VerifyOTPView, ResendOTPView
from users.views.forget_password import ForgotPasswordView, ResetPasswordView
from users.views.social_auth import SocialLoginView
from users.views.accept_invite import AcceptInvitationView
from users.views.logout import LogoutView
from users.views.user import UserView
from users.views.invitation import InvitationView

urlpatterns = [
    path('auth/accept-invite/', AcceptInvitationView.as_view(), name='accept-invite'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('auth/social-login/', SocialLoginView.as_view(), name='social-login'),
    # path('auth/toggle-2fa/', toggle_2fa, name='toggle-2fa'),  # new endpoint\
    path("users/", UserView.as_view(), name="user-view"),
    path("invitations/", InvitationView.as_view(), name="invitation-view"),
    path("users/<int:user_id>/", UserView.as_view(), name="user-delete"),

]
