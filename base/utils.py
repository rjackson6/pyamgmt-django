import re

PASCAL_CASE_TO_SNAKE_CASE_1 = re.compile(r'(.)([A-Z][a-z]+)')
PASCAL_CASE_TO_SNAKE_CASE_2 = re.compile(r'([a-z0-9])([A-Z])')


def pascal_case_to_snake_case(value: str) -> str:
    value = PASCAL_CASE_TO_SNAKE_CASE_1.sub(r'\1_\2', value)
    value = PASCAL_CASE_TO_SNAKE_CASE_2.sub(r'\1_\2', value).lower()
    return value


def default_related_names(value: str) -> dict:
    """Create both related names in snake case."""
    related_query_name = pascal_case_to_snake_case(value)
    related_name = f'{related_query_name}_set'
    return {
        'related_name': related_name,
        'related_query_name': related_query_name
    }


if __name__ == '__main__':
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyamgmtDjango.settings')
    import django
    django.setup()

    # Many-to-many conventions
    print(pascal_case_to_snake_case('CatalogItemToInvoiceLineItem'))
    print(pascal_case_to_snake_case('CatalogItemAndInvoiceLineItem'))
    print(pascal_case_to_snake_case('CatalogItemXInvoiceLineItem'))  # This
    # "To" confuses me because it's directional.
    # Other terms are too verbose for a simple convention
    # If there's not a more appropriate name for what the many-to-many table
    # does, I think "X" is the most convenient separator to keep with Python's
    # class naming convention.
