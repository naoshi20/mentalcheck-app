import datetime

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.mail import send_mail
# Create your models here.

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(('username'), max_length=30, blank=True)
    email = models.EmailField(('email address'), unique=True)
    first_name = models.CharField(('first name'), max_length=30, blank=True)
    last_name = models.CharField(('last name'), max_length=150, blank=True)
    phone = models.CharField(('phone'), max_length=16, blank=True)
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        ('active'),
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(('date joined'), default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return str(self.id) + ": " + self.email
    
    #def email_user(self, subject, message, from_email=None, **kwargs):
    #    send_mail(subject, message, from_email, [self.email], **kwargs)

class Construct(models.Model):
    construct_name = models.CharField(max_length=100)
    construct_slug = models.CharField(max_length=100, null=True)
    construct_desc = models.CharField(max_length=100, null=True)
    result_statement_lowest = models.CharField(max_length=500, null=True)
    result_statement_lower = models.CharField(max_length=500, null=True)
    result_statement_moderate = models.CharField(max_length=500, null=True)
    result_statement_higher = models.CharField(max_length=500, null=True)
    result_statement_highest = models.CharField(max_length=500, null=True)
    criteria_point = models.IntegerField(null=True)
    avg = models.IntegerField(null=True)
    count = models.IntegerField(null=True)
    main_flag =  models.BooleanField(
        ('construct importance'),
        default=False,
        help_text=(
            'This fiels show that this construct is main or not. '
        ),
    )
    emotion_flag =  models.BooleanField(
        ('construct of emotion'),
        default=False,
        help_text=(
            'This fiels show that this construct is about emotion. '
        ),
    )
    personality_flag =  models.BooleanField(
        ('construct of personality'),
        default=False,
        help_text=(
            'This fiels show that this construct is about personality. '
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.construct_name

class Question(models.Model):
    construct_id = models.ForeignKey(Construct, on_delete=models.CASCADE,null=True)
    question_text = models.CharField(max_length=400)
    question_order = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.construct_id) + " - " + self.question_text

class StressQOL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + " - " + str(timezone.localtime(self.created_at))

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    construct = models.ForeignKey(
        Construct, on_delete=models.CASCADE, null=True)
    avg = models.IntegerField(null=True)
    created_at = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)

    stress_qol = models.ForeignKey(
        StressQOL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.user) + " - " + str(timezone.localtime(self.created_at))

class AnswerDetail(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_value = models.IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return str(self.answer) + " - " + str(self.question)