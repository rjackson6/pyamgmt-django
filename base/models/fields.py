from django.db.models.fields import CharField


class UpperCharField(CharField):
    """CharField which forces UPPERCASE format."""
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)
