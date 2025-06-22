from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum
from .models import (
    User, Branch, Member, AccountType, Account, Transaction, 
    LoanProduct, LoanApplication, Loan, LoanPayment, SharePrice, 
    ShareTransaction, FixedDeposit, Dividend, DividendPayment, 
    Committee, CommitteeMember, Meeting, Notification, 
    SystemConfiguration, AuditLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_member', 'is_staff_member', 'is_active')
    list_filter = ('is_member', 'is_staff_member', 'is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'national_id')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Personal Information', {
            'fields': ('phone_number', 'national_id', 'date_of_birth', 'address', 'next_of_kin', 'next_of_kin_phone', 'profile_picture')
        }),
        ('Banking Status', {
            'fields': ('is_member', 'is_staff_member')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ('national_id',)
        return self.readonly_fields


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'manager', 'phone_number', 'is_active', 'members_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'address', 'phone_number')
    ordering = ('name',)
    
    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Members Count'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_number', 'user_full_name', 'branch', 'status', 'membership_date', 'total_shares', 'accounts_count')
    list_filter = ('status', 'branch', 'membership_date')
    search_fields = ('member_number', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('-membership_date',)
    readonly_fields = ('total_savings', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Member Information', {
            'fields': ('user', 'member_number', 'branch', 'membership_date', 'status')
        }),
        ('Financial Information', {
            'fields': ('monthly_contribution', 'total_shares', 'total_savings')
        }),
        ('Guarantors', {
            'fields': ('guarantor_1', 'guarantor_2'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Full Name'
    
    def accounts_count(self, obj):
        return obj.accounts.count()
    accounts_count.short_description = 'Accounts'


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'minimum_balance', 'interest_rate', 'monthly_fee', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'member_name', 'account_type', 'balance', 'status', 'date_opened')
    list_filter = ('account_type', 'status', 'date_opened')
    search_fields = ('account_number', 'member__user__first_name', 'member__user__last_name')
    ordering = ('-date_opened',)
    readonly_fields = ('date_opened', 'last_transaction_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Account Information', {
            'fields': ('account_number', 'member', 'account_type', 'status')
        }),
        ('Balance Information', {
            'fields': ('balance', 'available_balance', 'interest_earned')
        }),
        ('Timestamps', {
            'fields': ('date_opened', 'last_transaction_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_name(self, obj):
        return obj.member.user.get_full_name()
    member_name.short_description = 'Member Name'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'account_number', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at', 'processed_at')
    search_fields = ('transaction_id', 'account__account_number', 'reference_number', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('transaction_id', 'created_at', 'processed_at')
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'account', 'transaction_type', 'amount', 'status')
        }),
        ('Balance Information', {
            'fields': ('balance_before', 'balance_after')
        }),
        ('Transfer Information', {
            'fields': ('destination_account',),
            'classes': ('collapse',)
        }),
        ('Processing Information', {
            'fields': ('description', 'reference_number', 'processed_by', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def account_number(self, obj):
        return obj.account.account_number
    account_number.short_description = 'Account Number'


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'interest_rate', 'minimum_amount', 'maximum_amount', 'is_active')
    list_filter = ('is_active', 'collateral_required')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'member_name', 'loan_product', 'amount_requested', 'status', 'application_date')
    list_filter = ('status', 'loan_product', 'application_date')
    search_fields = ('application_number', 'member__user__first_name', 'member__user__last_name')
    ordering = ('-application_date',)
    readonly_fields = ('application_date', 'created_at')
    
    fieldsets = (
        ('Application Information', {
            'fields': ('application_number', 'member', 'loan_product', 'amount_requested', 'period_months', 'purpose')
        }),
        ('Approval Information', {
            'fields': ('amount_approved', 'status', 'reviewed_by', 'review_date', 'review_comments')
        }),
        ('Guarantors', {
            'fields': ('guarantor_1', 'guarantor_2'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('application_date', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_name(self, obj):
        return obj.member.user.get_full_name()
    member_name.short_description = 'Member Name'


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_number', 'member_name', 'principal_amount', 'balance', 'status', 'next_payment_date', 'days_overdue_display')
    list_filter = ('status', 'loan_product', 'disbursement_date')
    search_fields = ('loan_number', 'member__user__first_name', 'member__user__last_name')
    ordering = ('-disbursement_date',)
    readonly_fields = ('created_at', 'updated_at', 'days_overdue')
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('loan_number', 'application', 'member', 'loan_product')
        }),
        ('Financial Details', {
            'fields': ('principal_amount', 'interest_rate', 'period_months', 'monthly_payment', 'total_payable')
        }),
        ('Payment Information', {
            'fields': ('amount_paid', 'balance', 'status')
        }),
        ('Dates', {
            'fields': ('disbursement_date', 'maturity_date', 'next_payment_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_name(self, obj):
        return obj.member.user.get_full_name()
    member_name.short_description = 'Member Name'
    
    def days_overdue_display(self, obj):
        days = obj.days_overdue
        if days > 0:
            return format_html('<span style="color: red;">{} days</span>', days)
        return 'Current'
    days_overdue_display.short_description = 'Days Overdue'


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ('loan_number', 'amount', 'principal_amount', 'interest_amount', 'payment_date', 'processed_by')
    list_filter = ('payment_date', 'processed_by')
    search_fields = ('loan__loan_number', 'loan__member__user__first_name', 'loan__member__user__last_name')
    ordering = ('-payment_date',)
    readonly_fields = ('created_at',)
    
    def loan_number(self, obj):
        return obj.loan.loan_number
    loan_number.short_description = 'Loan Number'


@admin.register(SharePrice)
class SharePriceAdmin(admin.ModelAdmin):
    list_display = ('price_per_share', 'effective_date', 'is_current', 'set_by', 'created_at')
    list_filter = ('is_current', 'effective_date')
    ordering = ('-effective_date',)
    readonly_fields = ('created_at',)


@admin.register(ShareTransaction)
class ShareTransactionAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'transaction_type', 'number_of_shares', 'price_per_share', 'total_amount', 'transaction_date')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('member__user__first_name', 'member__user__last_name')
    ordering = ('-transaction_date',)
    readonly_fields = ('created_at',)
    
    def member_name(self, obj):
        return obj.member.user.get_full_name()
    member_name.short_description = 'Member Name'


@admin.register(FixedDeposit)
class FixedDepositAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'principal_amount', 'interest_rate', 'term_months', 'maturity_date', 'status')
    list_filter = ('status', 'start_date', 'maturity_date', 'auto_renew')
    search_fields = ('account__account_number', 'account__member__user__first_name')
    ordering = ('-start_date',)
    readonly_fields = ('created_at',)
    
    def account_number(self, obj):
        return obj.account.account_number
    account_number.short_description = 'Account Number'


@admin.register(Dividend)
class DividendAdmin(admin.ModelAdmin):
    list_display = ('year', 'rate_percentage', 'total_amount', 'declaration_date', 'payment_date', 'is_paid')
    list_filter = ('is_paid', 'declaration_date', 'payment_date')
    ordering = ('-year',)
    readonly_fields = ('created_at',)


@admin.register(DividendPayment)
class DividendPaymentAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'dividend_year', 'shares_held', 'amount', 'payment_date')
    list_filter = ('dividend__year', 'payment_date')
    search_fields = ('member__user__first_name', 'member__user__last_name')
    ordering = ('-payment_date',)
    readonly_fields = ('created_at',)
    
    def member_name(self, obj):
        return obj.member.user.get_full_name()
    member_name.short_description = 'Member Name'
    
    def dividend_year(self, obj):
        return obj.dividend.year
    dividend_year.short_description = 'Dividend Year'


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'members_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at',)
    
    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Members Count'


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'committee', 'position', 'start_date', 'end_date', 'is_active')
    list_filter = ('position', 'is_active', 'committee', 'start_date')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'committee__name')
    ordering = ('-start_date',)
    readonly_fields = ('created_at',)
    
    def member_name(self, obj):
        return obj.member.user.get_full_name()
    member_name.short_description = 'Member Name'


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_type', 'committee', 'date', 'venue', 'is_completed')
    list_filter = ('meeting_type', 'is_completed', 'committee', 'date')
    search_fields = ('title', 'venue')
    ordering = ('-date',)
    readonly_fields = ('created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    ordering = ('-created_at',)
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_preview', 'updated_by', 'updated_at')
    search_fields = ('key', 'description')
    ordering = ('key',)
    readonly_fields = ('updated_at',)
    
    def value_preview(self, obj):
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value
    value_preview.short_description = 'Value'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'model_name', 'object_id', 'timestamp', 'ip_address')
    list_filter = ('action_type', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name', 'object_id', 'description')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    
    def has_add_permission(self, request):
        return False  # Audit logs should not be manually created
    
    def has_change_permission(self, request, obj=None):
        return False  # Audit logs should not be modified
    
    def has_delete_permission(self, request, obj=None):
        return False  # Audit logs should not be deleted


# Customize admin site headers
admin.site.site_header = "Cooperative Banking System Administration"
admin.site.site_title = "Banking Admin"
admin.site.index_title = "Welcome to Banking System Administration"