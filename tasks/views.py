from django.http import JsonResponse
from ninja import Router

from tasks.models import Task
from tasks.schemas import TaskSchema
from worker.worker_auth import worker_auth

router = Router()

@router.get('/tasks', response=list[TaskSchema])
def get_tasks(request):
    return Task.objects.all()


@router.get('/tasks/id/{worker_id}', response=list[TaskSchema])
def get_worker_tasks(request, worker_id: int):
    return Task.objects.filter(workers__in=[worker_id]).all()


@router.get('/tasks/own', response=list[TaskSchema], auth=worker_auth)
def get_own_tasks(request):
    if not hasattr(request, "worker"):
        return JsonResponse({"error": "Worker not authenticated"}, status=401)

    return Task.objects.filter(workers__in=[request.worker.id]).all()

@router.get('/task/{task_id}', response=TaskSchema)
def get_task(request, task_id: int):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    return task


@router.patch('/task/{task_id}/workers', response=TaskSchema)
def set_workers(request, task_id: int, workers: list[int]):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    task.workers.set(workers)
    task.save()

    return task
