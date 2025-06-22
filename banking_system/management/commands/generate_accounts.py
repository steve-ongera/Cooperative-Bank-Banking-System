from django.core.management.base import BaseCommand
from banking_system.models import Account, Member, AccountType
from faker import Faker
from random import choice, randint, uniform
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate 500 accounts for real members'

    def handle(self, *args, **kwargs):
        fake = Faker()
        members = list(Member.objects.all())
        account_types = list(AccountType.objects.filter(is_active=True))

        if not members:
            self.stdout.write(self.style.ERROR("No members found. Please create members first."))
            return
        if not account_types:
            self.stdout.write(self.style.ERROR("No account types found. Please create account types first."))
            return

        account_statuses = ['active', 'dormant', 'closed', 'frozen']
        created = 0
        used_account_numbers = set(Account.objects.values_list('account_number', flat=True))

        for _ in range(500):
            member = choice(members)
            acc_type = choice(account_types)
            status = choice(account_statuses)

            # Generate a unique account number
            while True:
                acc_number = f"{randint(1000000000, 9999999999)}"
                if acc_number not in used_account_numbers:
                    used_account_numbers.add(acc_number)
                    break

            balance = Decimal(round(uniform(500, 500000), 2))
            available_balance = balance - Decimal(randint(0, 100))
            interest_earned = Decimal(round(uniform(0, 5000), 2))

            Account.objects.create(
                account_number=acc_number,
                member=member,
                account_type=acc_type,
                balance=balance,
                available_balance=available_balance,
                status=status,
                interest_earned=interest_earned,
                last_transaction_date=timezone.now()
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created} accounts."))
