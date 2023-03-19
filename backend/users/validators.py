import re
from django.core.exceptions import ValidationError


def validate_username(value):
    if value.lower() == "me":
        raise ValidationError(
            ('Использовать имя "me" в качестве username запрещено.'),
            params={"value": value},
        )


def validate_name(value):
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s]*$', value):
        raise ValidationError('Имя может содержать только буквы')
