from django.core.management.base import BaseCommand
from api.models import Store
import csv
class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        with open('/home/inifnitus/homeAssignment/takeHome/csvs/store_timezones.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader) 

            for row in reader:
                store_id = row[0]
                timezone_str = row[1]
                try:
                    store = Store.objects.get(store_id=store_id)
                except:
                    store =Store.objects.create(store_id=store_id)
                self.stdout.write('adding timezone id: {store_id}')
                store.timezone_str = timezone_str
                store.save()

        # for removing any empty
        # stores = Store.objects.all()
        # for st in stores:
        #     if st.timezone_str == '':
        #         st.timezone_str = 'America/Chicago'
        #         st.save()

