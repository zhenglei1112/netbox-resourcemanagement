import os
import django
from django.core.management import call_command

# 设置 Django 环境 (假设 netbox 已安装在环境中)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')
django.setup()

print("Running makemigrations for netbox_rms...")
try:
    call_command('makemigrations', 'netbox_rms')
    print("makemigrations successful.")
except Exception as e:
    print(f"Error running makemigrations: {e}")
    exit(1)

print("Running migrate...")
try:
    call_command('migrate')
    print("migrate successful.")
except Exception as e:
    print(f"Error running migrate: {e}")
    exit(1)
