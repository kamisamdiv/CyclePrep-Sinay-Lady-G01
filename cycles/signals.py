from .models import DEFAULT_SYMPTOMS, Symptom


def seed_symptoms(sender, **kwargs):
    """Make sure the default symptom choices exist after every migrate."""
    for name in DEFAULT_SYMPTOMS:
        Symptom.objects.get_or_create(name=name)
