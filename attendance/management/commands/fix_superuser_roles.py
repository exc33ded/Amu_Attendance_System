from django.core.management.base import BaseCommand
from attendance.models import CustomUser

class Command(BaseCommand):
    help = 'Fix superuser roles to ensure they are set to admin'

    def handle(self, *args, **options):
        superusers = CustomUser.objects.filter(is_superuser=True)
        fixed_count = 0
        
        for user in superusers:
            if user.role != 'admin':
                user.role = 'admin'
                user.save()
                fixed_count += 1
                self.stdout.write(f'Fixed role for superuser: {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} superuser roles')) 