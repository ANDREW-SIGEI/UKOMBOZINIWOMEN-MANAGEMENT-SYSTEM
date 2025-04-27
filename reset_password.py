import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ukomboziniwomen.settings")
django.setup()

from django.contrib.auth.models import User

# Reset the admin password
admin_user = User.objects.get(username='admin')
admin_user.set_password('admin123')
admin_user.save()
print("Password for 'admin' has been reset to 'admin123'") 