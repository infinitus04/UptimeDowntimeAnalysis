from django.core.management.base import BaseCommand
from api.models import OpenTime,Store
from datetime import datetime
import csv
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        
        with open('/home/inifnitus/homeAssignment/takeHome/csvs/menu_hours.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)
            
            for row in reader:
                store_id = row[0]
                try:
                    store = Store.objects.get(store_id=store_id)
                except:
                    if not store:
                        store = Store.objects.create(store_id=store_id)
                day = row[1]
                start_time_local = row[2]
                end_time_local = row[3]
                self.stdout.write(f'adding store: {store.store_id} | day: {day}')

                OpenTime.objects.update_or_create(store = store, day=day, start_time_local=start_time_local,end_time_local=end_time_local)
        self.stdout.write('finished')


    