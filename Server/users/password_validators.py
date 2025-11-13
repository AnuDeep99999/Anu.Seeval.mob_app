import re

from django.core.exceptions import ValidationError


class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                self.get_help_text(),
                code='password_no_number',
            )

    def get_help_text(self):
        return "Your password must contain at least 1 digit, 0-9."


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                self.get_help_text(),
                code='password_no_upper',
            )

    def get_help_text(self):
        return "Your password must contain at least 1 uppercase letter, A-Z."


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                self.get_help_text(),
                code='password_no_lower',
            )

    def get_help_text(self):
        return "Your password must contain at least 1 lowercase letter, a-z."


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                self.get_help_text(),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return "Your password must contain at least 1 symbol: " + \
        "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"


class MatchPassword(object):
    def validate(self, password, cpassword, user=None):
        if password != cpassword:
            raise ValidationError(
                self.get_help_text(),
            )

    def get_help_text(self):
        return "Your password and confirm password does not match"


class MinLength(object):
    def validate(self, password, user=None):
        print('min--', len(password))
        if len(password) < 8:
            raise ValidationError(
                self.get_help_text(),
            )

    def get_help_text(self):
        return "Your password minimum length is 8"


class MaxLength(object):
    def validate(self, password, user=None):
        print("max---", len(password))
        if len(password) > 16:
            raise ValidationError(
                self.get_help_text(),
            )

    def get_help_text(self):
        return "Your password maximum length is 16!"