from django.core.management.base import BaseCommand
from banking_system.models import Loan, LoanApplication
from datetime import timedelta, date
from decimal import Decimal
from random import randint
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate loan records from disbursed loan applications'

    def handle(self, *args, **kwargs):
        applications = LoanApplication.objects.filter(status='disbursed')

        created = 0
        for app in applications:
            if Loan.objects.filter(application=app).exists():
                continue  # Skip if loan already exists

            principal = app.amount_approved or app.amount_requested
            rate = app.loan_product.interest_rate
            months = app.period_months

            # Calculate total interest and payments (simple interest)
            total_interest = (Decimal(rate) / Decimal(100)) * principal * Decimal(months) / Decimal(12)
            total_payable = principal + total_interest
            monthly_payment = total_payable / months

            disbursed_on = app.application_date
            maturity = disbursed_on + timedelta(days=30 * months)
            next_payment = disbursed_on + timedelta(days=30)

            loan_number = f"LN{randint(1000000, 9999999)}"

            loan = Loan.objects.create(
                loan_number=loan_number,
                application=app,
                member=app.member,
                loan_product=app.loan_product,
                principal_amount=principal,
                interest_rate=rate,
                period_months=months,
                monthly_payment=monthly_payment,
                total_payable=total_payable,
                amount_paid=Decimal('0.00'),
                balance=total_payable,
                status='active',
                disbursement_date=disbursed_on,
                maturity_date=maturity,
                next_payment_date=next_payment
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created} active loan records."))
