from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

VERIFICATION_STATUS = [
    ("unverified", "Unverified"),
    ("pending", "Pending Review"),
    ("verified", "Verified"),
    ("rejected", "Rejected"),
]
# Create your models here.

class UserProfile(models.Model):
    """
    Profile model for storing additional information about users.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    verifica_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default="unverified",
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
    )
    passport_size = models.ImageField(
        upload_to="passport_sizes/",
        null=True,
        blank=True,
    )
    is_broker = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.full_name}'s profile"
