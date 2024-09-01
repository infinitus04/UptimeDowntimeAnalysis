from api.models import TimeStamp,UptimeDowntimeLog
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        UptimeDowntimeLog.objects.all().delete()