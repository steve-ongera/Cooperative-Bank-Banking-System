from django.core.management.base import BaseCommand
from banking_system.models import LoanProduct
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create default loan products for the cooperative banking system'

    def handle(self, *args, **kwargs):
        products = [
            {
                'name': 'Personal Loan',
                'code': 'LN001',
                'description': 'Unsecured personal loan for general use.',
                'interest_rate': Decimal('13.50'),
                'processing_fee_rate': Decimal('1.50'),
                'minimum_amount': Decimal('5000.00'),
                'maximum_amount': Decimal('500000.00'),
                'minimum_period_months': 6,
                'maximum_period_months': 36,
                'collateral_required': False,
                'guarantors_required': 2,
            },
            {
                'name': 'Business Loan',
                'code': 'LN002',
                'description': 'Loan to support small businesses and entrepreneurs.',
                'interest_rate': Decimal('12.00'),
                'processing_fee_rate': Decimal('1.00'),
                'minimum_amount': Decimal('20000.00'),
                'maximum_amount': Decimal('1000000.00'),
                'minimum_period_months': 12,
                'maximum_period_months': 60,
                'collateral_required': True,
                'guarantors_required': 2,
            },
            {
                'name': 'Emergency Loan',
                'code': 'LN003',
                'description': 'Quick disbursement loan for emergencies.',
                'interest_rate': Decimal('15.00'),
                'processing_fee_rate': Decimal('2.00'),
                'minimum_amount': Decimal('1000.00'),
                'maximum_amount': Decimal('50000.00'),
                'minimum_period_months': 1,
                'maximum_period_months': 12,
                'collateral_required': False,
                'guarantors_required': 1,
            },
            {
                'name': 'Agricultural Loan',
                'code': 'LN004',
                'description': 'Loan tailored for farmers and agricultural businesses.',
                'interest_rate': Decimal('10.00'),
                'processing_fee_rate': Decimal('0.50'),
                'minimum_amount': Decimal('10000.00'),
                'maximum_amount': Decimal('300000.00'),
                'minimum_period_months': 6,
                'maximum_period_months': 36,
                'collateral_required': True,
                'guarantors_required': 1,
            },
            {
                'name': 'Education Loan',
                'code': 'LN005',
                'description': 'Loan to support school fees and education-related costs.',
                'interest_rate': Decimal('11.50'),
                'processing_fee_rate': Decimal('1.25'),
                'minimum_amount': Decimal('5000.00'),
                'maximum_amount': Decimal('200000.00'),
                'minimum_period_months': 6,
                'maximum_period_months': 24,
                'collateral_required': False,
                'guarantors_required': 2,
            },
        ]

        created = 0
        for product in products:
            if not LoanProduct.objects.filter(code=product['code']).exists():
                LoanProduct.objects.create(**product)
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created} loan products."))
