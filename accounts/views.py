from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .models import CustomUser,ChangePassword
from .serializers import CustomUserSerializer
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from datetime import timezone,datetime
from rest_framework.decorators import api_view
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from rest_framework.views import APIView

from .serializers import  PasswordResetSerializer,PasswordResetConfirmSerializer,PasswordResetConfirmSerializer



class SignUpAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.generate_verification_token()
            user.save()
         
            verification_link = f"http://127.0.0.1:8000/accounts/verify/{user.verification_token}/"
            
            send_mail(
                'Verify your email address',
                f'Click the following link to verify your email address: {verification_link}',
                'rapidev.alerts@gmail.com',  # Replace with your sender email address
                [user.email],
                fail_silently=False,
            )
           
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def verify_emial(self,token):
    
    user = CustomUser.objects.filter(verification_token=token).first()
    print(user)
    if not user:
        # Token is invalid
        return Response({"message": "No user found with this name"}, status=status.HTTP_400_BAD_REQUEST)

    if user.verification_expires_at < datetime.now(timezone.utc):
        # Token has expired
        return Response({"message": "User verification time is expired."},status=status.HTTP_400_BAD_REQUEST)

    # Mark user as verified
    user.is_verified=True
    user.verification_token = None  # Clear the verification token
    user.verification_expires_at = None  # Clear the expiry time
    user.save()

    return Response({"message": "User verified successfully."}, status=status.HTTP_200_OK)
    

class RequestPasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(CustomUser, email=email)
            change_password, created = ChangePassword.objects.get_or_create(user=user)
            change_password.generate_verification_token()

            # Send email with verification link
            reset_link = f"http://yourdomain.com/reset-password?token={change_password.verification_token}"
            send_mail(
                'Password Reset',
                f'Click the link to reset your password: {reset_link}',
                'your-email@gmail.com',
                [user.email],
                fail_silently=False,
            )
            
            return Response({"detail": "Password reset link sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            try:
                change_password = ChangePassword.objects.get(verification_token=token)
                if change_password.verification_expires_at < timezone.now():
                    return Response({"detail": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)

                user = change_password.user
                user.set_password(new_password)
                user.save()

                # Optionally, delete the token after successful password reset
                change_password.delete()

                return Response({"detail": "Password has been reset."}, status=status.HTTP_200_OK)
            except ChangePassword.DoesNotExist:
                return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)