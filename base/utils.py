import re

CAMEL_CASE_TO_SNAKE_CASE = re.compile(r'(?<!^)(?=[A-Z])')


def camel_case_to_snake_case(value: str) -> str:
    value = CAMEL_CASE_TO_SNAKE_CASE.sub('_', value).lower()
    return value
