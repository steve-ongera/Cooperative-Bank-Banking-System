from django.core.management.base import BaseCommand
from banking_system.models import Member, User, Branch
from faker import Faker
from random import choice, randint, sample
from datetime import timedelta, date
from decimal import Decimal

class Command(BaseCommand):
    help = 'Generate 300 cooperative members'

    def handle(self, *args, **kwargs):
        fake = Faker()
        users = list(User.objects.filter(is_member=True).exclude(member__isnull=False))
        branches = list(Branch.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("No available users marked as members."))
            return

        if not branches:
            self.stdout.write(self.style.ERROR("No branches found. Please create branches first."))
            return

        created = 0
        statuses = ['active', 'suspended', 'terminated', 'pending']

        for i in range(300):
            if not users:
                break

            user = users.pop()
            branch = choice(branches)
            member_number = f"M{randint(100000, 999999)}"
            membership_date = fake.date_between(start_date='-5y', end_date='today')
            status = choice(statuses)
            monthly_contribution = Decimal(randint(500, 5000))
            total_shares = Decimal(randint(10000, 200000))

            member = Member.objects.create(
                user=user,
                member_number=member_number,
                branch=branch,
                membership_date=membership_date,
                status=status,
                monthly_contribution=monthly_contribution,
                total_shares=total_shares,
            )

            # Assign guarantors randomly from existing members
            existing_members = list(Member.objects.exclude(id=member.id))
            if len(existing_members) >= 2:
                guarantors = sample(existing_members, 2)
                member.guarantor_1 = guarantors[0]
                member.guarantor_2 = guarantors[1]
                member.save()

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created} members."))
