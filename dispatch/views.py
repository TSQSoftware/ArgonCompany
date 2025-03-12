from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from tasks.models import Task


def admin_login(request):
    if request.user.is_authenticated:
        return redirect("dispatch:dispatch_dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("dispatch:dispatch_dashboard")
            else:
                messages.error(request, "You are not authorized to access this section.")
        else:
            messages.error(request, "Invalid username or password.")

    else:
        form = AuthenticationForm()

    return render(request, "dispatch/admin_login.html", {"form": form})

@login_required
def admin_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("dispatch:admin_login")

@login_required
def dispatch_dashboard(request):
    tasks = Task.objects.all()
    workers = []
    return render(request, "dispatch/dashboard.html", {"workers": workers, "tasks": tasks})
