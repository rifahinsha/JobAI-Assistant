import getpass
from django.core.management.base import BaseCommand
from admin_panel.models import Admin

class Command(BaseCommand):
    help = "Create an admin_panel Admin account."

    def handle(self, *args, **options):
        username = input("Admin username: ").strip()
        if Admin.objects.filter(username=username).exists():
            self.stderr.write(self.style.ERROR(f"Admin '{username}' already exists."))
            return
        password = getpass.getpass("Admin password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            self.stderr.write(self.style.ERROR("Passwords do not match."))
            return
        admin = Admin(username=username)
        admin.set_password(password)
        admin.save()
        self.stdout.write(self.style.SUCCESS(f"Admin '{username}' created."))