from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import m2m_changed, post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from tasks.models import Task


@receiver(m2m_changed, sender=Task.workers.through)
def workers_updated(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Triggered when workers are added or removed from a task.
    action: 'post_add', 'post_remove'
    """
    channel_layer = get_channel_layer()
    if action == 'post_add':
        for worker_id in pk_set:
            worker = model.objects.get(id=worker_id)
            group_name = f'task_updates_{worker.id}'

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'task_update',
                }
            )

    elif action == 'post_remove':
        for worker_id in pk_set:
            worker = model.objects.get(id=worker_id)
            group_name = f'task_updates_{worker.id}'

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'task_update',
                }
            )


@receiver(post_save, sender=Task)
def task_updated(sender, instance, created, **kwargs):
    """
    Triggered when a task is created or updated.
    """
    if not created:
        channel_layer = get_channel_layer()
        for worker in instance.workers.all():
            group_name = f'task_updates_{worker.id}'
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'task_update',
                }
            )

@receiver(post_delete, sender=Task)
def task_deleted(sender, instance, **kwargs):
    """
    Triggered when a task is deleted.
    """
    channel_layer = get_channel_layer()

    for worker in instance.workers.all():
        print(worker.id)
        group_name = f'task_updates_{worker.id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'task_update',
            }
        )