from django.core.management.base import BaseCommand
from api.models import Store
import csv
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        unique_store_ids = set()
        total_count = 0
        unique_count = 0
        with open('/home/inifnitus/homeAssignment/takeHome/csvs/store_status.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader) 

            for row in reader:
                store_id = row[0]
                total_count +=1
                if store_id not in unique_store_ids:
                    unique_store_ids.add(store_id)
                    unique_count +=1
                    self.stdout.write(f'adding store_id: {unique_count}')

                    Store.objects.create(store_id=store_id)            

            self.stdout.write(f'total_count: {total_count}')
            self.stdout.write(f'unique_count: {unique_count}')
