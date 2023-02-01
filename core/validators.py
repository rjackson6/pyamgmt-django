import datetime
import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


alphanumeric_re = re.compile(r'^[0-9a-zA-Z]*\Z')
validate_alphanumeric = RegexValidator(
    regex=alphanumeric_re,
    message=_('Only alphanumeric characters allowed.'),
    code='invalid'
)
digit_re = re.compile(r'^\d+\Z')
validate_digit = RegexValidator(
    regex=digit_re,
    message=_('Enter a valid digit.'),
    code='invalid'
)
isbn_re = re.compile(r'^[0-9xX]+\Z')
validate_isbn = RegexValidator(
    regex=isbn_re,
    message=_('ISBN may only contain digits and "X".'),
    code='invalid'
)


def validate_date_not_future(value):
    if value is not None and value > timezone.now().date():
        raise ValidationError(
            _('%(value)s may not be in the future.'),
            params={'value': value}
        )


def validate_isbn_13_check_digit(value):
    """Example...
    978-0-306-40615-?
    s = 9x1 + 7x3 + 8x1 + 0x3 + 3x1 + 0x2 + 6x1 + 4x3 + 0x1 + 6x3 + 1x1 + 5x3
      = 93
    93 / 10 = 9 remainder 3
    10 - 3 = 7  <-- check digit
    """
    value = str(value)
    digit_sum = 0
    for i, d in enumerate(value[:12]):
        if i % 2 == 0:
            digit_sum += int(d)
        else:
            digit_sum += 3 * int(d)
    if int(value[-1]) != 10 - digit_sum % 10:
        raise ValidationError(
            _('ISBN-13 invalid check digit'),
            params={'value': value}
        )


def validate_positive_timedelta(value):
    if value < datetime.timedelta(0):
        raise ValidationError(
            _('%(value)s may not be a negative duration.'),
            params={'value': value}
        )


def validate_year_not_future(value):
    if value > timezone.now().year:
        raise ValidationError(
            _('%(value)s may not be in the future'),
            params={'value': value}
        )
