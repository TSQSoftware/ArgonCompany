import datetime
from uuid import uuid4

import jwt
from argon_company import settings
from django.http import JsonResponse
from ninja import Router

from worker.models import Worker
from worker.schemas import WorkerSchema, WorkerCreateSchema, WorkerUpdateSchema

router = Router()

@router.get("/login")
def login(request, activation_key: str, first_name: str, last_name: str):
    try:
        worker = Worker.objects.get(activation_key=activation_key, first_name=first_name, last_name=last_name)
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)

    uuid = uuid4()
    worker.uuid = uuid
    worker.save()

    payload = {
        'uuid': str(uuid),
        'worker_id': worker.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=31)
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return JsonResponse({'token': token})

@router.post('/create', response=WorkerSchema)
def create_worker(request, payload: WorkerCreateSchema):
    worker = Worker(**payload.dict())
    worker.save()
    return worker


@router.patch('/{worker_id}', response=WorkerSchema)
def update_worker(request, worker_id: int, payload: WorkerUpdateSchema):
    try:
        worker = Worker.objects.get(id=worker_id)
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)

    update_data = {key: value for key, value in payload.dict().items() if value is not None}

    for key, value in update_data.items():
        setattr(worker, key, value)

    worker.save()
    return worker


@router.patch('/activation/{worker_id}', response=WorkerSchema)
def activate_worker(request, worker_id: int):
    try:
        worker = Worker.objects.get(id=worker_id)
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)

    worker.set_random_activation_key()
    return worker

@router.delete('/{worker_id}')
def delete_worker(request, worker_id: int):
    try:
        worker = Worker.objects.get(id=worker_id)
    except Worker.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)

    worker.delete()
    return JsonResponse({'success': True})