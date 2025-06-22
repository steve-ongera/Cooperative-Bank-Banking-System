from django.core.management.base import BaseCommand
from banking_system.models import LoanApplication, Member, LoanProduct, User
from faker import Faker
from decimal import Decimal
from random import randint, choice, sample
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate loan applications for existing members'

    def handle(self, *args, **kwargs):
        fake = Faker()
        members = list(Member.objects.all())
        products = list(LoanProduct.objects.filter(is_active=True))
        users = list(User.objects.all())

        if not members or not products:
            self.stdout.write(self.style.ERROR("Ensure there are members and active loan products first."))
            return

        application_statuses = ['pending', 'under_review', 'approved', 'disbursed']
        created = 0

        for member in members:
            num_apps = randint(1, 2)  # Each member may have 1-2 loan applications
            for _ in range(num_apps):
                product = choice(products)
                amount = Decimal(randint(int(product.minimum_amount), int(product.maximum_amount)))
                period = randint(product.minimum_period_months, product.maximum_period_months)

                # Guarantors
                other_members = [m for m in members if m != member]
                guarantors = sample(other_members, min(len(other_members), product.guarantors_required))
                guarantor_1 = guarantors[0] if len(guarantors) > 0 else None
                guarantor_2 = guarantors[1] if len(guarantors) > 1 else None

                status = choice(application_statuses)
                application_number = f"APP{randint(100000, 999999)}"

                loan_app = LoanApplication.objects.create(
                    application_number=application_number,
                    member=member,
                    loan_product=product,
                    amount_requested=amount,
                    amount_approved=amount if status in ['approved', 'disbursed'] else None,
                    period_months=period,
                    purpose=fake.text(max_nb_chars=100),
                    status=status,
                    guarantor_1=guarantor_1,
                    guarantor_2=guarantor_2,
                    reviewed_by=choice(users) if status in ['approved', 'disbursed'] else None,
                    review_date=timezone.now() if status in ['approved', 'disbursed'] else None,
                    review_comments=fake.sentence() if status in ['approved', 'disbursed'] else "",
                )

                created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created} loan applications."))
