from django.core.management.base import BaseCommand
from banking_system.models import Transaction, Account, User
from faker import Faker
from random import choice, randint, uniform, sample
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate 2 to 5 random transactions per account'

    def handle(self, *args, **kwargs):
        fake = Faker()
        accounts = list(Account.objects.all())
        users = list(User.objects.all())
        transaction_types = [
            'deposit', 'withdrawal', 'transfer',
            'loan_disbursement', 'loan_repayment',
            'interest_payment', 'fee_charge',
            'dividend_payment', 'share_purchase'
        ]
        status_choices = ['completed', 'pending', 'failed']

        if not accounts:
            self.stdout.write(self.style.ERROR("No accounts found. Please create accounts first."))
            return

        total_created = 0

        for account in accounts:
            num_transactions = randint(2, 5)
            for _ in range(num_transactions):
                transaction_type = choice(transaction_types)
                amount = Decimal(round(uniform(100, 10000), 2))
                balance_before = account.balance
                balance_after = balance_before
                description = fake.sentence()
                processed_by = choice(users) if users else None
                reference = fake.uuid4()

                # Adjust balance for deposits and withdrawals
                if transaction_type in ['deposit', 'loan_disbursement', 'interest_payment', 'dividend_payment']:
                    balance_after += amount
                    account.update_balance(amount, 'credit')
                elif transaction_type in ['withdrawal', 'fee_charge', 'loan_repayment', 'share_purchase']:
                    if balance_before < amount:
                        amount = balance_before  # Avoid negative balance
                    balance_after -= amount
                    account.update_balance(amount, 'debit')
                elif transaction_type == 'transfer':
                    destination_accounts = [acc for acc in accounts if acc != account]
                    if destination_accounts:
                        destination_account = choice(destination_accounts)
                        if balance_before < amount:
                            amount = balance_before
                        balance_after -= amount
                        account.update_balance(amount, 'debit')
                        destination_account.update_balance(amount, 'credit')
                    else:
                        destination_account = None
                else:
                    destination_account = None

                txn = Transaction.objects.create(
                    account=account,
                    transaction_type=transaction_type,
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    description=description,
                    reference_number=str(reference),
                    status=choice(status_choices),
                    processed_by=processed_by,
                    processed_at=timezone.now(),
                    destination_account=destination_account if transaction_type == 'transfer' else None,
                )

                total_created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {total_created} transactions."))
