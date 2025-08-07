from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import UserProfile, Role, UserRole, UserActivity
from core.models import Address


@login_required
def user_dashboard(request):
    """User dashboard view"""
    user = request.user
    profile = user.profile
    
    # Get user's roles
    user_roles = UserRole.objects.filter(user=user, is_active=True)
    
    # Get recent activities
    recent_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:10]
    
    context = {
        'user': user,
        'profile': profile,
        'user_roles': user_roles,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def user_profile(request):
    """User profile view"""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        # Handle profile update
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        profile.phone = request.POST.get('phone', '')
        profile.mobile = request.POST.get('mobile', '')
        profile.department = request.POST.get('department', '')
        profile.position = request.POST.get('position', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    context = {
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def user_list(request):
    """List all users (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_dashboard')
    
    users = User.objects.select_related('profile').all()
    
    context = {
        'users': users,
    }
    
    return render(request, 'users/user_list.html', context)


@login_required
def role_list(request):
    """List all roles (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_dashboard')
    
    roles = Role.objects.all()
    
    context = {
        'roles': roles,
    }
    
    return render(request, 'users/role_list.html', context)


@login_required
def user_activities(request):
    """View user activities (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_dashboard')
    
    activities = UserActivity.objects.select_related('user').all().order_by('-created_at')
    
    context = {
        'activities': activities,
    }
    
    return render(request, 'users/activities.html', context)


@require_http_methods(["POST"])
@login_required
def assign_role(request):
    """Assign role to user (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    user_id = request.POST.get('user_id')
    role_id = request.POST.get('role_id')
    
    try:
        user = User.objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
        
        # Check if role is already assigned
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': request.user}
        )
        
        if not created:
            user_role.is_active = True
            user_role.assigned_by = request.user
            user_role.save()
        
        return JsonResponse({'success': True, 'message': f'Role {role.name} assigned to {user.username}'})
    
    except (User.DoesNotExist, Role.DoesNotExist):
        return JsonResponse({'error': 'User or Role not found'}, status=404)


@require_http_methods(["POST"])
@login_required
def remove_role(request):
    """Remove role from user (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    user_id = request.POST.get('user_id')
    role_id = request.POST.get('role_id')
    
    try:
        user_role = UserRole.objects.get(user_id=user_id, role_id=role_id)
        user_role.is_active = False
        user_role.save()
        
        return JsonResponse({'success': True, 'message': 'Role removed successfully'})
    
    except UserRole.DoesNotExist:
        return JsonResponse({'error': 'User role not found'}, status=404)
