from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from dispatch.forms import TaskForm
from tasks.models import Task
from worker.models import Worker


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
    workers = Worker.objects.all()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dispatch:dispatch_dashboard")
    else:
        form = TaskForm()

    return render(
        request,
        "dispatch/dashboard.html",
        {"workers": workers, "tasks": tasks, "form": form}
    )


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, "dispatch/task_detail.html", {"task": task})

@login_required
def tasks_list(request):
    return render(request, "dispatch/tasks_list.html", {"tasks": Task.objects.all()})

