from django.core.management.base import BaseCommand
from banking_system.models import AccountType
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create default account types for the cooperative banking system'

    def handle(self, *args, **kwargs):
        account_types = [
            {
                'name': 'Savings Account',
                'code': 'SAV001',
                'description': 'Standard savings account with interest accrual.',
                'minimum_balance': Decimal('500.00'),
                'interest_rate': Decimal('3.50'),
                'monthly_fee': Decimal('50.00'),
            },
            {
                'name': 'Current Account',
                'code': 'CUR001',
                'description': 'No interest account for frequent transactions.',
                'minimum_balance': Decimal('1000.00'),
                'interest_rate': Decimal('0.00'),
                'monthly_fee': Decimal('100.00'),
            },
            {
                'name': 'Fixed Deposit',
                'code': 'FD001',
                'description': 'Long-term fixed deposit with higher interest.',
                'minimum_balance': Decimal('10000.00'),
                'interest_rate': Decimal('7.00'),
                'monthly_fee': Decimal('0.00'),
            },
            {
                'name': 'Junior Account',
                'code': 'JUN001',
                'description': 'Account designed for minors and students.',
                'minimum_balance': Decimal('200.00'),
                'interest_rate': Decimal('2.00'),
                'monthly_fee': Decimal('20.00'),
            },
        ]

        created = 0
        for acct in account_types:
            if not AccountType.objects.filter(code=acct['code']).exists():
                AccountType.objects.create(**acct)
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created} account types."))
