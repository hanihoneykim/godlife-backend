import uuid
import secrets
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from config.utils import compress_image, upload_path
from common.models import CommonModel


def generate_hex(nbytes=32):
    return secrets.token_hex(nbytes)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.set_password(password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, blank=False)
    nickname = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to=upload_path)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.nickname})"

    def save(self, *args, **kwargs):
        if self.profile_image and self.pk:
            try:
                this = User.objects.get(pk=self.pk)
                if this.profile_image != self.profile_image:
                    print("profile_image changed")
                    self.profile_image = compress_image(
                        self.profile_image, size=(100, 100)
                    )
            except:
                pass
        if self.email:
            self.email = self.email.lower().strip()

        super().save(*args, **kwargs)


class AuthToken(CommonModel):
    id = models.CharField(default=generate_hex, max_length=64, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Member(CommonModel):
    id = models.CharField(default=generate_hex, max_length=64, primary_key=True)
    user = models.ForeignKey(
        User, related_name="team_member", null=True, on_delete=models.CASCADE
    )
    team = models.ForeignKey(
        "core.Team", related_name="member", null=True, on_delete=models.CASCADE
    )
    is_leader = models.BooleanField(default=False)
