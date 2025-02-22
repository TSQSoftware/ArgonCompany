from django.http import JsonResponse
from ninja import Router

from tasks.models import Task, TaskStatus, TaskNote
from tasks.schemas import TaskSchema, TaskNoteSchema
from worker.models import WorkerRole
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

@router.patch('/task/{task_id}/status', response=TaskSchema, auth=worker_auth)
def set_status(request, task_id: int, status: TaskStatus):
    worker = request.worker
    if status == TaskStatus.COMPLETED or status == TaskStatus.CANCELLED:
        if worker.role == WorkerRole.WORKER:
            return JsonResponse({'error': 'Worker not authorized'}, status=401)

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    task.status = status
    task.save()

    return task

@router.post('/task/{task_id}/note/create', response=TaskSchema, auth=worker_auth)
def add_note(request, task_id: int, note: str):
    worker = request.worker

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    if not task.workers.filter(workers__in=[worker]).exists():
        return JsonResponse({'error': 'Worker not authorized'}, status=401)

    task_note = TaskNote(task=task, note=note, worker=worker)
    task_note.save()

    return task
