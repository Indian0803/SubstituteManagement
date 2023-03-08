from unicodedata import name
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from multiselectfield import MultiSelectField

# Class for managing users


class UserManager(BaseUserManager):
    # creating normal user
    def create_user(self, email, first_name, middle_name, last_name, role, subject, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            role=role,
            subject=subject,
            count=0
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    # creating admin user
    def create_superuser(self, email, first_name, middle_name, last_name, role, subject, password):
        user = self.create_user(
            email=email,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            role=None,
            subject=None,
            password=password,
            count=0,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

# Stores user information


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    ROLE = (
        ("Elementary", "Elementary"),
        ("Middle", "Middle"),
        ("High", "High")
    )

    SUBJECT = (
        ("English", "English"),
        ("Math", "Math"),
        ("Science", "Science"),
        ("Japanese", "Japanese"),
        ("Spanish", "Spanish"),
        ("French", "French"),
        ("Computer Science", "Computer Science")
    )

    first_name = models.CharField(max_length=200, null=True)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True)
    role = MultiSelectField(choices=ROLE, null=True)
    subject = MultiSelectField(choices=SUBJECT, null=True)
    count = models.PositiveSmallIntegerField(null=True, default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'middle_name',
                       'last_name', 'role', 'subject']

    def __str__(self):
        if self.middle_name == None:
            return str(self.first_name) + " " + str(self.last_name)
        else:
            return str(self.first_name) + " " + str(self.middle_name) + " " + str(self.last_name)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

# Stores lesson information


class Lesson(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, null=True)
    room = models.CharField(max_length=200, null=True)
    day = models.CharField(max_length=200, null=True)
    period = models.CharField(max_length=200, null=True)
    start = models.CharField(max_length=200, null=True)
    end = models.CharField(max_length=200, null=True)
    year = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

# Stores teachers available for substitution for each time slots


class SubstituteSchedule(models.Model):
    day = models.CharField(max_length=200, null=True)
    period_one = models.ManyToManyField(
        User, related_name="period_one", blank=True)
    period_two = models.ManyToManyField(
        User, related_name="period_two", blank=True)
    period_three = models.ManyToManyField(
        User, related_name="period_three", blank=True)
    period_four = models.ManyToManyField(
        User, related_name="period_four", blank=True)
    period_five = models.ManyToManyField(
        User, related_name="period_five", blank=True)
    period_six = models.ManyToManyField(
        User, related_name="period_six", blank=True)
    morning_recess = models.ManyToManyField(
        User, related_name="morning_recess", blank=True)
    lunch_one = models.ManyToManyField(
        User, related_name="lunch_one", blank=True)
    lunch_two = models.ManyToManyField(
        User, related_name="lunch_two", blank=True)
    lunch_three = models.ManyToManyField(
        User, related_name="lunch_three", blank=True)

    def __str__(self):
        return self.day

# Holidays present in the academic calendar


class Holiday(models.Model):
    start = models.DateField()
    end = models.DateField(null=True)
    type = models.CharField(max_length=200, null=True)

# Substitute lesson information


class Substitute(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    verified = models.BooleanField(null=True)
