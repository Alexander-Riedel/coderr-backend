from django.db import migrations
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token as LiveToken

def create_guest_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    CustomerProfile = apps.get_model('profile_app', 'CustomerProfile')
    BusinessProfile = apps.get_model('profile_app', 'BusinessProfile')
    HistToken = apps.get_model('authtoken', 'Token')

    def safe_create_token_for(user):
        key = LiveToken.generate_key()
        HistToken.objects.create(user=user, key=key)

    # Gastkunde
    if not User.objects.filter(username='andrey').exists():
        u = User.objects.create(
            username='andrey',
            password=make_password('asdasd'),
            email='andrey@guest.de',
        )
        CustomerProfile.objects.create(
            user=u, username='andrey',
            first_name='Andrey',
            last_name='Guest',
            location='Hamburg', 
            tel='0123456789',
            description='Gast Account', 
            working_hours='9-17',
            type='customer'
        )
        safe_create_token_for(u)

    # Gastfirma
    if not User.objects.filter(username='kevin').exists():
        u = User.objects.create(
            username='kevin',
            password=make_password('asdasd24'),
            email='kevin@guest.de',
        )
        BusinessProfile.objects.create(
            user=u, username='kevin',
            first_name='Kevin', 
            last_name='Demo',
            location='Berlin', 
            tel='030123456',
            description='Demo Company', 
            working_hours='9-17',
            type='business'
        )
        safe_create_token_for(u)

class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('profile_app', '0001_initial'),
        ('authtoken', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_guest_users, reverse_code=migrations.RunPython.noop),
    ]
