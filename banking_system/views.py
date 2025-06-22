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

@login_required
def dashboard(request):
    if request.user.is_member:
        try:
            member = Member.objects.get(user=request.user)
            recent_transactions = Transaction.objects.filter(
                account__member=member
            ).order_by('-created_at')[:5]
            active_loans = Loan.objects.filter(
                member=member, 
                status='active'
            )
            notifications = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).order_by('-created_at')[:5]
            
            context = {
                'member': member,
                'recent_transactions': recent_transactions,
                'active_loans': active_loans,
                'notifications': notifications,
            }
            return render(request, 'dashboard/member_dashboard.html', context)
        
        except Member.DoesNotExist:
            messages.error(request, "Member profile not found")
            return redirect('logout')
    
    elif request.user.is_staff_member:
        # Staff dashboard logic
        branch_stats = {
            'total_members': 125,
            'active_loans': 42,
            'todays_transactions': 18,
            'pending_approvals': 7,
        }
        
        pending_approvals = [
            {'type': 'Loan', 'details': 'L-2023-00123', 'created_at': '2023-06-15', 'link': '#'},
            {'type': 'Member', 'details': 'New member registration', 'created_at': '2023-06-14', 'link': '#'},
        ]
        
        recent_activities = [
            {'timestamp': '2023-06-15 10:30', 'description': 'Approved loan L-2023-00122', 'user': request.user},
            {'timestamp': '2023-06-15 09:15', 'description': 'Processed withdrawal for A/C 10023456', 'user': request.user},
        ]
        
        context = {
            'branch_stats': branch_stats,
            'pending_approvals': pending_approvals,
            'recent_activities': recent_activities,
        }
        return render(request, 'dashboard/staff_dashboard.html', context)
    
    else:
        messages.error(request, "Unauthorized access")
        return redirect('logout')