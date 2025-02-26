from django.db.models.signals import post_migrate
from django.dispatch import receiver

from data.models import Color


@receiver(post_migrate)
def populate_colors(sender, **kwargs):
    if sender.name == "data":
        if Color.objects.count() != 0:
            return

        initial_colors = [
            ("Red", "ff0000"),
            ("Blue", "0000ff"),
            ("Green", "00ff00"),
            ("Yellow", "ffff00"),
            ("Orange", "ffa500"),
            ("Purple", "800080"),
            ("Pink", "ffc0cb"),
            ("Black", "000000"),
            ("White", "ffffff"),
            ("Gray", "808080"),
            ("Cyan", "00ffff"),
            ("Magenta", "ff00ff"),
            ("Brown", "a52a2a"),
        ]
        for name, color in initial_colors:
            Color.objects.get_or_create(name=name, color=color)
