__all__ = [
    'validate_isbn',
    'validate_isbn_13_check_digit',
]

import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

isbn_re = re.compile(r'^[0-9xX]+\Z')
validate_isbn = RegexValidator(
    regex=isbn_re,
    message=_('ISBN may only contain digits and "X".'),
    code='invalid'
)


def validate_isbn_13_check_digit(value) -> None:
    """Validation using the ISBN algorithm.

    Example:
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
