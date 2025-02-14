from django.http import JsonResponse
from ninja import Router

from tasks.models import TaskType, Task
from tasks.schemas import TaskTypeSchema, TaskTypeCreateSchema, TaskSchema, TaskCreateSchema, TaskTypeUpdateSchema, \
    TaskUpdateSchema
from worker.worker_auth import worker_auth

router = Router()


@router.post('/type/create', response=TaskTypeSchema)
def create_type(request, payload: TaskTypeCreateSchema):
    task_type = TaskType(**payload.dict())
    task_type.save()
    return task_type


@router.get('/types', response=list[TaskTypeSchema])
def get_types(request):
    return TaskType.objects.all()


@router.patch('/type/{type_id}', response=TaskTypeSchema)
def update_type(request, type_id: int, payload: TaskTypeUpdateSchema):
    try:
        task_type = TaskType.objects.get(id=type_id)
    except TaskType.DoesNotExist:
        return JsonResponse({'error': 'Task type not found'}, status=404)

    update_data = {key: value for key, value in payload.dict().items() if value is not None}

    for key, value in update_data.items():
        setattr(task_type, key, value)

    task_type.save()
    return task_type


@router.post('/task/create', response=TaskSchema)
def create_task(request, payload: TaskCreateSchema):
    task = Task.objects.create(
        name=payload.name,
        description=payload.description,
        contact_phone_number=payload.contact_phone_number,
        address=payload.address,
    )

    task.type_id = payload.type_id
    task.save()

    return task


@router.patch('/task/{task_id}', response=TaskTypeSchema)
def update_task(request, task_id: int, payload: TaskUpdateSchema):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    update_data = {key: value for key, value in payload.dict().items() if value is not None}

    for key, value in update_data.items():
        setattr(task, key, value)

    task.save()
    return task


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
