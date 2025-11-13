from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.forms.models import model_to_dict

from .manager import UserManager
from .password_validators import MatchPassword

from django.conf import settings
from django.utils import timezone


        

class User(AbstractUser):
    """
    Abstract User of django auth user model.
    """
    email = models.EmailField(_("email address"), unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },)
    country_code_regex = RegexValidator(regex=r"^\+\d{1,4}$")  # Country code can be 1 to 4 digits long, prefixed with +
    country_code = models.CharField(validators=[country_code_regex], max_length=5, default="+91")  # Max length includes the '+' sign
    phone_number_regex = RegexValidator(regex = r"^\d{10}$")
    phone_number = models.CharField(validators = [phone_number_regex], max_length=10, unique = True)
    last_logout = models.DateTimeField(null=True)
    is_user = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)  # or True if you want


    
    
    def _str_(self):
        return self.first_name + " " + self.last_name
    
    def is_otp_expired(self):
        if not self.otp_created_at:
            return True
        expiry_time = self.otp_created_at + timezone.timedelta(minutes=10)
        return timezone.now() > expiry_time

    def reset_password(self, password, confirm_password):
        match = MatchPassword()
        match.validate(password, confirm_password)
        self.set_password(password)
        self.save()

    class Meta:
        ordering = '-id',
    
    def _init_(self, *args, **kwargs):
        super(User, self)._init_(*args, **kwargs)
        self.__initial = self._dict
    
    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                                           self._meta.fields])
