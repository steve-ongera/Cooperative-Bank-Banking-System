from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class User(AbstractUser):
    """Extended user model for the cooperative banking system"""
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    national_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    next_of_kin = models.CharField(max_length=100, blank=True)
    next_of_kin_phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_member = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.username}"


class Branch(models.Model):
    """Bank branches model"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_branches')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Member(models.Model):
    """Cooperative member model"""
    MEMBERSHIP_STATUS = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
        ('pending', 'Pending Approval')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_number = models.CharField(max_length=20, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='members')
    membership_date = models.DateField()
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending')
    guarantor_1 = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='guaranteed_members_1')
    guarantor_2 = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='guaranteed_members_2')
    monthly_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_shares = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.member_number}"

    @property
    def total_savings(self):
        return sum(account.balance for account in self.accounts.filter(account_type='savings'))


class AccountType(models.Model):
    """Different types of accounts available"""
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    minimum_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Annual percentage
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Account(models.Model):
    """Bank accounts model"""
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('current', 'Current Account'),
        ('fixed_deposit', 'Fixed Deposit'),
        ('shares', 'Shares Account'),
        ('loan', 'Loan Account')
    ]

    ACCOUNT_STATUS = [
        ('active', 'Active'),
        ('dormant', 'Dormant'),
        ('closed', 'Closed'),
        ('frozen', 'Frozen')
    ]

    account_number = models.CharField(max_length=20, unique=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default='active')
    date_opened = models.DateField(auto_now_add=True)
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    interest_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_number} - {self.member.user.get_full_name()}"

    def update_balance(self, amount, transaction_type):
        """Update account balance based on transaction type"""
        if transaction_type in ['deposit', 'credit']:
            self.balance += amount
            self.available_balance += amount
        elif transaction_type in ['withdrawal', 'debit']:
            self.balance -= amount
            self.available_balance -= amount
        self.last_transaction_date = timezone.now()
        self.save()


class Transaction(models.Model):
    """All financial transactions"""
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('loan_disbursement', 'Loan Disbursement'),
        ('loan_repayment', 'Loan Repayment'),
        ('interest_payment', 'Interest Payment'),
        ('fee_charge', 'Fee Charge'),
        ('dividend_payment', 'Dividend Payment'),
        ('share_purchase', 'Share Purchase')
    ]

    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed')
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_before = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    reference_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_transactions')
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # For transfers
    destination_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transfers')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.account.account_number}"


class LoanProduct(models.Model):
    """Different loan products offered"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual percentage
    processing_fee_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=12, decimal_places=2)
    minimum_period_months = models.IntegerField()
    maximum_period_months = models.IntegerField()
    collateral_required = models.BooleanField(default=False)
    guarantors_required = models.IntegerField(default=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.interest_rate}%"


class LoanApplication(models.Model):
    """Loan applications from members"""
    APPLICATION_STATUS = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed')
    ]

    application_number = models.CharField(max_length=20, unique=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loan_applications')
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.CASCADE)
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    period_months = models.IntegerField()
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    guarantor_1 = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='guaranteed_loans_1')
    guarantor_2 = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='guaranteed_loans_2')
    application_date = models.DateField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    review_date = models.DateTimeField(null=True, blank=True)
    review_comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application_number} - {self.member.user.get_full_name()} - {self.amount_requested}"


class Loan(models.Model):
    """Active loans"""
    LOAN_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('written_off', 'Written Off')
    ]

    loan_number = models.CharField(max_length=20, unique=True)
    application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.CASCADE)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    period_months = models.IntegerField()
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    total_payable = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='active')
    disbursement_date = models.DateField()
    maturity_date = models.DateField()
    next_payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.loan_number} - {self.member.user.get_full_name()} - {self.balance}"

    @property
    def days_overdue(self):
        if self.next_payment_date < timezone.now().date():
            return (timezone.now().date() - self.next_payment_date).days
        return 0


class LoanPayment(models.Model):
    """Loan payment records"""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loan.loan_number} - {self.amount} - {self.payment_date}"


class SharePrice(models.Model):
    """Share price history"""
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    set_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"Share Price: {self.price_per_share} - {self.effective_date}"


class ShareTransaction(models.Model):
    """Share purchase/sale transactions"""
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('dividend', 'Dividend Payment')
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='share_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    number_of_shares = models.DecimalField(max_digits=12, decimal_places=2)
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateField()
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.transaction_type} - {self.number_of_shares} shares"


class FixedDeposit(models.Model):
    """Fixed deposit accounts"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('matured', 'Matured'),
        ('premature_withdrawal', 'Premature Withdrawal'),
        ('renewed', 'Renewed')
    ]

    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    maturity_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    maturity_date = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FD-{self.account.account_number} - {self.principal_amount}"


class Dividend(models.Model):
    """Annual dividend declarations"""
    year = models.IntegerField(unique=True)
    rate_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    declaration_date = models.DateField()
    payment_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    declared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dividend {self.year} - {self.rate_percentage}%"


class DividendPayment(models.Model):
    """Individual dividend payments to members"""
    dividend = models.ForeignKey(Dividend, on_delete=models.CASCADE, related_name='payments')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='dividend_payments')
    shares_held = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.dividend.year} - {self.amount}"


class Committee(models.Model):
    """Management committees"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CommitteeMember(models.Model):
    """Committee membership"""
    POSITIONS = [
        ('chairperson', 'Chairperson'),
        ('vice_chairperson', 'Vice Chairperson'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('member', 'Member')
    ]

    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='members')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='committee_memberships')
    position = models.CharField(max_length=20, choices=POSITIONS)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['committee', 'member', 'position']

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.committee.name} - {self.position}"


class Meeting(models.Model):
    """Committee meetings"""
    MEETING_TYPES = [
        ('regular', 'Regular Meeting'),
        ('special', 'Special Meeting'),
        ('agm', 'Annual General Meeting'),
        ('board', 'Board Meeting')
    ]

    title = models.CharField(max_length=200)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES)
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='meetings')
    date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    agenda = models.TextField()
    minutes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d')}"


class Notification(models.Model):
    """System notifications"""
    NOTIFICATION_TYPES = [
        ('loan_approval', 'Loan Approval'),
        ('payment_due', 'Payment Due'),
        ('dividend_payment', 'Dividend Payment'),
        ('meeting_reminder', 'Meeting Reminder'),
        ('account_update', 'Account Update'),
        ('system_alert', 'System Alert')
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"


class AuditLog(models.Model):
    """Audit trail for important actions"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('transaction', 'Transaction'),
        ('loan_approval', 'Loan Approval'),
        ('member_approval', 'Member Approval')
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.model_name} - {self.timestamp}"