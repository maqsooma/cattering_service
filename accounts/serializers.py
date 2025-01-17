from rest_framework import serializers
from .models import CustomUser,ChangePassword
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404

from .models import ChangePassword

class CustomUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'})  # Field for password input
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})  # Field for password confirmation

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role', 'date_of_birth', 'password1', 'password2']  # Include password fields

    def validate(self, data):
        """
        Ensure that the passwords are the same.
        """
        if data.get('password1') != data.get('password2'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        # Remove password1 and password2 from validated_data before creating the user
        validated_data.pop('password1')
        validated_data.pop('password2')
        return super().create(validated_data)
    


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePassword
        fields = ['user', 'verification_token', 'verification_expires_at']
        


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    

