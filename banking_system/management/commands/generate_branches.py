from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
from banking_system.models import Branch, User
import random

# Kenya counties
KENYAN_COUNTIES = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Machakos", "Kiambu", "Kisii", "Nyeri", "Murang'a",
    "Meru", "Embu", "Tharaka-Nithi", "Kirinyaga", "Laikipia", "Nyandarua", "Baringo", "Uasin Gishu",
    "Trans Nzoia", "Bungoma", "Busia", "Siaya", "Homabay", "Migori", "Kericho", "Bomet", "Nandi", "Kakamega",
    "Vihiga", "Turkana", "West Pokot", "Samburu", "Marsabit", "Isiolo", "Garissa", "Wajir", "Mandera",
    "Tana River", "Lamu", "Taita Taveta", "Kilifi", "Kwale", "Kajiado", "Narok", "Migori", "Kitui", "Makueni"
]

class Command(BaseCommand):
    help = 'Generate 200 bank branches across Kenya counties'

    def handle(self, *args, **kwargs):
        fake = Faker()
        created = 0
        existing_codes = set(Branch.objects.values_list('code', flat=True))
        users = list(User.objects.filter(is_member=True))

        for i in range(200):
            county = random.choice(KENYAN_COUNTIES)
            name = f"{county} Branch {i+1}"
            code = f"BR{i+1:04d}"

            # Skip if code already exists
            if code in existing_codes:
                continue

            address = f"{fake.street_address()}, {county}, Kenya"
            phone = fake.unique.msisdn()[:15]
            manager = random.choice(users) if users else None

            Branch.objects.create(
                name=name,
                code=code,
                address=address,
                phone_number=phone,
                manager=manager
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created} branches.'))
