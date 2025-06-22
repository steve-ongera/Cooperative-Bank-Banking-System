from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Member, Transaction, Loan, Notification

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'auth/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Member, Transaction, Loan, Notification, Account, AccountType
import logging

# Add logging to help debug
logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    logger.info(f"Dashboard accessed by user: {request.user.username}")
    logger.info(f"User is_member: {request.user.is_member}")
    logger.info(f"User is_staff_member: {request.user.is_staff_member}")
    
    if request.user.is_member:
        try:
            member = Member.objects.get(user=request.user)
            logger.info(f"Member found: {member}")
            
            # Get recent transactions for all member's accounts
            recent_transactions = Transaction.objects.filter(
                account__member=member
            ).select_related('account', 'account__account_type').order_by('-created_at')[:5]
            logger.info(f"Recent transactions count: {recent_transactions.count()}")
            
            # Get active loans
            active_loans = Loan.objects.filter(
                member=member, 
                status='active'
            ).select_related('loan_product')
            logger.info(f"Active loans count: {active_loans.count()}")
            
            # Get notifications
            notifications = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).order_by('-created_at')[:5]
            logger.info(f"Notifications count: {notifications.count()}")
            
            # Get account summaries
            accounts_summary = []
            member_accounts = Account.objects.filter(
                member=member,
                status='active'
            ).select_related('account_type')
            logger.info(f"Member accounts count: {member_accounts.count()}")
            
            for account in member_accounts:
                accounts_summary.append({
                    'account': account,
                    'balance': account.balance,
                    'type': account.account_type.name,
                })
            
            # Calculate totals - Debug version
            total_savings = 0
            try:
                # Debug: Check what AccountTypes exist
                all_account_types = AccountType.objects.all()
                logger.info("Available AccountTypes:")
                for at in all_account_types:
                    logger.info(f"  ID: {at.id}, Name: '{at.name}', Code: '{at.code}'")
                
                # First try to find savings account type by name (case insensitive)
                savings_account_types = AccountType.objects.filter(
                    Q(name__icontains='savings') | 
                    Q(name__icontains='saving') |
                    Q(code__iexact='SAV') |
                    Q(code__iexact='SAVINGS')
                )
                
                logger.info(f"Found {savings_account_types.count()} savings account types")
                for sat in savings_account_types:
                    logger.info(f"  Savings type: {sat.name} ({sat.code})")
                
                if savings_account_types.exists():
                    savings_accounts = member_accounts.filter(account_type__in=savings_account_types)
                    logger.info(f"Member has {savings_accounts.count()} savings accounts")
                    
                    total_savings = savings_accounts.aggregate(total=Sum('balance'))['total'] or 0
                    logger.info(f"Total savings calculated: {total_savings}")
                else:
                    # If no specific savings account type found, try alternative approaches
                    logger.warning("No savings account types found, using fallback")
                    
                    # Try looking for accounts with 'savings' in the account type name
                    potential_savings = member_accounts.filter(
                        account_type__name__icontains='saving'
                    )
                    
                    if potential_savings.exists():
                        total_savings = potential_savings.aggregate(total=Sum('balance'))['total'] or 0
                        logger.info(f"Fallback savings calculation: {total_savings}")
                    else:
                        # Last fallback - sum all non-loan accounts
                        non_loan_accounts = member_accounts.exclude(
                            account_type__name__icontains='loan'
                        )
                        total_savings = non_loan_accounts.aggregate(total=Sum('balance'))['total'] or 0
                        logger.info(f"Final fallback - all non-loan accounts: {total_savings}")
                        
            except Exception as e:
                logger.error(f"Error calculating savings: {e}")
                total_savings = 0
            
            total_shares = member.total_shares
            logger.info(f"Total shares: {total_shares}")
            
            # Get loan summary
            loan_summary = {
                'total_loans': active_loans.count(),
                'total_balance': active_loans.aggregate(total=Sum('balance'))['total'] or 0,
                'overdue_loans': active_loans.filter(next_payment_date__lt=timezone.now().date()).count()
            }
            logger.info(f"Loan summary: {loan_summary}")
            
            context = {
                'member': member,
                'recent_transactions': recent_transactions,
                'active_loans': active_loans,
                'notifications': notifications,
                'accounts_summary': accounts_summary,
                'total_savings': total_savings,  # Make sure this is passed to template
                'total_shares': total_shares,
                'loan_summary': loan_summary,
            }
            
            logger.info("Rendering member dashboard template")
            return render(request, 'dashboard/member_dashboard.html', context)
        
        except Member.DoesNotExist:
            logger.error(f"Member profile not found for user: {request.user.username}")
            messages.error(request, "Member profile not found. Please contact administrator.")
            return redirect('logout')
        except Exception as e:
            logger.error(f"Error in member dashboard: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('logout')
    
    elif request.user.is_staff_member:
        try:
            logger.info("Loading staff dashboard")
            # Staff dashboard logic with proper aggregations
            today = timezone.now().date()
            
            # Get branch statistics
            branch_stats = {
                'total_members': Member.objects.filter(status='active').count(),
                'active_loans': Loan.objects.filter(status='active').count(),
                'todays_transactions': Transaction.objects.filter(
                    created_at__date=today,
                    status='completed'
                ).count(),
                'pending_approvals': (
                    Member.objects.filter(status='pending').count() +
                    Loan.objects.filter(status='pending').count()
                ),
            }
            
            # Get pending loan applications
            pending_loan_approvals = Loan.objects.filter(
                status='pending'
            ).select_related('member', 'member__user')[:5]
            
            # Get pending member applications
            pending_member_approvals = Member.objects.filter(
                status='pending'
            ).select_related('user')[:5]
            
            # Combine pending approvals
            pending_approvals = []
            
            for loan in pending_loan_approvals:
                pending_approvals.append({
                    'type': 'Loan',
                    'details': f'{loan.loan_number} - {loan.member.user.get_full_name()}',
                    'created_at': loan.created_at.strftime('%Y-%m-%d'),
                    'link': f'/loans/{loan.id}/',  # Update with your actual URL
                    'amount': loan.principal_amount
                })
            
            for member in pending_member_approvals:
                pending_approvals.append({
                    'type': 'Member',
                    'details': f'{member.user.get_full_name()} - {member.member_number}',
                    'created_at': member.created_at.strftime('%Y-%m-%d'),
                    'link': f'/members/{member.id}/',  # Update with your actual URL
                })
            
            # Get recent activities (recent transactions)
            recent_activities = Transaction.objects.filter(
                created_at__gte=today - timedelta(days=7),
                status='completed'
            ).select_related('account', 'account__member', 'account__member__user', 'processed_by').order_by('-created_at')[:10]
            
            # Format recent activities
            formatted_activities = []
            for transaction in recent_activities:
                formatted_activities.append({
                    'timestamp': transaction.created_at.strftime('%Y-%m-%d %H:%M'),
                    'description': f'{transaction.get_transaction_type_display()} of {transaction.amount} for {transaction.account.member.user.get_full_name()}',
                    'user': transaction.processed_by.get_full_name() if transaction.processed_by else 'System',
                    'amount': transaction.amount,
                    'type': transaction.transaction_type
                })
            
            # Financial summary
            financial_summary = {
                'total_deposits': Transaction.objects.filter(
                    transaction_type='deposit',
                    status='completed',
                    created_at__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0,
                
                'total_withdrawals': Transaction.objects.filter(
                    transaction_type='withdrawal', 
                    status='completed',
                    created_at__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0,
                
                'total_loan_disbursements': Transaction.objects.filter(
                    transaction_type='loan_disbursement',
                    status='completed',
                    created_at__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0,
            }
            
            context = {
                'branch_stats': branch_stats,
                'pending_approvals': pending_approvals,
                'recent_activities': formatted_activities,
                'financial_summary': financial_summary,
            }
            return render(request, 'dashboard/staff_dashboard.html', context)
            
        except Exception as e:
            logger.error(f"Error in staff dashboard: {str(e)}")
            messages.error(request, f"An error occurred loading dashboard: {str(e)}")
            # Return a basic context to avoid complete failure
            context = {
                'branch_stats': {'total_members': 0, 'active_loans': 0, 'todays_transactions': 0, 'pending_approvals': 0},
                'pending_approvals': [],
                'recent_activities': [],
                'financial_summary': {'total_deposits': 0, 'total_withdrawals': 0, 'total_loan_disbursements': 0},
            }
            return render(request, 'dashboard/staff_dashboard.html', context)
    
    else:
        logger.warning(f"Unauthorized dashboard access by user: {request.user.username}")
        messages.error(request, "Unauthorized access")
        return redirect('logout')