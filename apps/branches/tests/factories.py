import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.branches.models import Branch


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True


class BranchFactory(DjangoModelFactory):
    class Meta:
        model = Branch

    name = factory.Sequence(lambda n: f"Branch {n}")
    address = factory.Faker("street_address")
    city = factory.Iterator(["Bogota", "Medellin", "Cali", "Barranquilla"])
    phone = factory.Sequence(lambda n: f"+57 300 000 {n:04d}")
    email = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '')}@clinic.test")
    is_active = True
