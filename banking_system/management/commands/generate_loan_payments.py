from django.core.management.base import BaseCommand
from banking_system.models import Loan, LoanPayment, Transaction, User
from django.utils import timezone
from random import randint, choice
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate loan payment records for active loans'

    def handle(self, *args, **kwargs):
        loans = Loan.objects.filter(status='active')
        users = list(User.objects.all())
        total_created = 0

        for loan in loans:
            num_payments = randint(1, 6)
            last_balance = loan.balance
            payments = []

            for i in range(num_payments):
                if last_balance <= 0:
                    break

                processor = choice(users)
                principal = (loan.monthly_payment * Decimal('0.8')).quantize(Decimal('0.01'))
                interest = (loan.monthly_payment * Decimal('0.2')).quantize(Decimal('0.01'))
                total_amount = principal + interest

                if total_amount > last_balance:
                    principal = (last_balance * Decimal('0.8')).quantize(Decimal('0.01'))
                    interest = (last_balance * Decimal('0.2')).quantize(Decimal('0.01'))
                    total_amount = principal + interest

                balance_after = last_balance - total_amount

                # Create a corresponding Transaction
                txn = Transaction.objects.create(
                    account=loan.member.accounts.first(),
                    transaction_type='loan_repayment',
                    amount=total_amount,
                    balance_before=last_balance,
                    balance_after=balance_after,
                    description=f"Loan payment for {loan.loan_number}",
                    reference_number=f"LOANPAY{randint(100000, 999999)}",
                    status='completed',
                    processed_by=processor,
                    processed_at=timezone.now()
                )

                payment_date = loan.disbursement_date + timedelta(days=(i+1) * 30)

                LoanPayment.objects.create(
                    loan=loan,
                    amount=total_amount,
                    principal_amount=principal,
                    interest_amount=interest,
                    penalty_amount=Decimal('0.00'),
                    balance_before=last_balance,
                    balance_after=balance_after,
                    payment_date=payment_date,
                    processed_by=processor,
                    transaction=txn
                )

                last_balance = balance_after
                total_created += 1

            # Update loan record
            loan.amount_paid = loan.total_payable - last_balance
            loan.balance = last_balance
            loan.next_payment_date = timezone.now().date() + timedelta(days=30)
            loan.save()

        self.stdout.write(self.style.SUCCESS(f"Created {total_created} loan payment records."))
