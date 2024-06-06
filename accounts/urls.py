from django.urls import path
from .views import SignUpAPIView,verify_emial,PasswordResetAPIView,PasswordResetRequestAPIView

urlpatterns = [
    path('signup',SignUpAPIView.as_view(),name= 'signup'),
    path('verify/<str:token>/',verify_emial,name='verify_email'),
    path('request-reset/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('reset/<uidb64>/<token>/', PasswordResetAPIView.as_view(), name='password_reset'),
]
