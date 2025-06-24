import os
import sys
import django

# Projektordner zum Pfad hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Django-Settings aktivieren
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from profile_app.models import BusinessProfile, CustomerProfile
from django.contrib.auth.hashers import make_password

# Gastkunde
if not User.objects.filter(username='andrey').exists():
    user_customer = User.objects.create(
        username='andrey',
        password=make_password('asdasd'),
        email='andrey@guest.de',
    )
    CustomerProfile.objects.create(
        user=user_customer,
        username='andrey',
        first_name='',
        last_name='',
        location='',
        tel='',
        description='',
        working_hours='',
        type='customer'
    )
    print("Gastkunde 'andrey' erstellt.")
else:
    print("Gastkunde 'andrey' existiert bereits.")

# Gastfirma
if not User.objects.filter(username='kevin').exists():
    user_business = User.objects.create(
        username='kevin',
        password=make_password('asdasd24'),
        email='kevin@guest.de',
    )
    BusinessProfile.objects.create(
        user=user_business,
        username='kevin',
        first_name='',
        last_name='',
        location='',
        tel='',
        description='',
        working_hours='',
        type='business'
    )
    print("Gastfirma 'kevin' erstellt.")
else:
    print("Gastfirma 'kevin' existiert bereits.")
