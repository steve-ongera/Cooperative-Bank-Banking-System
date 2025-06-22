from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate 100 fake users for the banking system'

    def handle(self, *args, **kwargs):
        fake = Faker()
        created_count = 0

        for _ in range(100):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1000, 9999)}"
            email = f"{username}@gmail.com"
            phone_number = fake.unique.msisdn()[:15]
            national_id = fake.unique.ssn()
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=70)
            address = fake.address()
            next_of_kin = fake.name()
            next_of_kin_phone = fake.unique.msisdn()[:15]

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='12345678',
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    national_id=national_id,
                    date_of_birth=date_of_birth,
                    address=address,
                    next_of_kin=next_of_kin,
                    next_of_kin_phone=next_of_kin_phone,
                    is_member=True
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} users.'))
