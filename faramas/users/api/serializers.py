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
            **super().get_cleaned_data(),
            "full_name": self.cleaned_data.get("full_name"),
            "phone_number": self.cleaned_data.get("phone_number"),
        }

    def save(self, request):
        user = super().save(request)
        user.full_name = self.cleaned_data.get("full_name")
        user.phone_number = self.cleaned_data.get("phone_number")
        user.save()
        return user
