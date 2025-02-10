from django.http import JsonResponse
from ninja import Router

from worker.models import Worker
from worker.schemas import WorkerSchema, WorkerCreateSchema, WorkerUpdateSchema

router = Router()


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