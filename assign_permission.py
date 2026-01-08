# assign_permission.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from netbox_rms.models import ServiceOrder

User = get_user_model()

def assign_permission(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"User '{username}' does not exist.")
        return

    # Find the permission
    # format: app_label.codename
    perm_codename = 'can_check_resource'
    app_label = 'netbox_rms'
    
    try:
        permission = Permission.objects.get(
            content_type__app_label=app_label,
            codename=perm_codename
        )
    except Permission.DoesNotExist:
        print(f"Error: Permission '{app_label}.{perm_codename}' not found in database.")
        print("Please check if migrations have been applied.")
        return

    # Assign
    user.user_permissions.add(permission)
    print(f"Successfully assigned '{permission.name}' to user '{user.username}'.")
    
    # Check
    if user.has_perm(f"{app_label}.{perm_codename}"):
        print(f"Verification: User '{user.username}' HAS the permission.")
    else:
        print(f"Verification: User '{user.username}' does NOT have the permission (cache issue?).")

if __name__ == '__main__':
    target_username = input("请输入要授权的用户名 (Enter username): ").strip()
    if target_username:
        assign_permission(target_username)
