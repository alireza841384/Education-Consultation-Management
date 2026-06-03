from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("type", CustomUser.Types.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if not password:
            raise ValueError("Superuser must have a password.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    class Types(models.TextChoices):
        STUDENT = "student", "Student"
        ADMIN = "admin", "Admin"

    username = None
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=Types.choices, default=Types.STUDENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


national_id_validator = RegexValidator(r"^\d{10}$", "National ID must be exactly 10 digits.")


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    birth_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1900), MaxValueValidator(timezone.now().year)],
    )
    national_id = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[national_id_validator],
        db_index=True,
    )
    photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["national_id"],
                name="uniq_profile_national_id",
                condition=models.Q(national_id__isnull=False),
            )
        ]

    def __str__(self):
        return f"profile:{self.user_id}"


@receiver(post_save, sender=CustomUser, dispatch_uid="create_profile_for_user")
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
