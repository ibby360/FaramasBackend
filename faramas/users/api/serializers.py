from rest_framework import serializers

from dj_rest_auth.registration.serializers import RegisterSerializer

from faramas.users.models import User
from faramas.profiles.api.serializers import UserProfileSerializer


class UserSerializer(serializers.ModelSerializer[User]):
    user_profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ["full_name", "url", "email", "phone_number", "user_profile"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }

class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration serializer to add extra fields to the registration process.
    """

    username = None
    full_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    def get_cleaned_data(self):
        """
        Override to include extra fields in the cleaned data.
        """
        return {
            "full_name": self.validated_data.get("full_name"),
            "email": self.validated_data.get("email"),
            "phone_number": self.validated_data.get("phone_number"),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
        }

    def save(self, request):
        user = super().save(request)
        user.full_name = self.validated_data.get("full_name")
        user.phone_number = self.validated_data.get("phone_number")
        user.save()
        return user
