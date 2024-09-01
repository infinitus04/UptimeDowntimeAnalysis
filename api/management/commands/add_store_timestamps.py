from django.core.management.base import BaseCommand
from api.models import Store, TimeStamp
import csv
from datetime import datetime
from django.utils import timezone
import re
import pytz

class Command(BaseCommand):
    help = 'Import store status data from CSV'

    def handle(self, *args, **options):
        total_count = 0
        with open('/home/inifnitus/homeAssignment/takeHome/csvs/store_status.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                store_id = row[0]
                status = row[1]
                timestamp_utc = row[2]

                # Parse the timestamp with optional microseconds
                # try:
                timestamp_obj = self.parse_timestamp(timestamp_utc)
                total_count += 1
                store = Store.objects.get(store_id=store_id)
                status = True if status == 'active' else False
                self.stdout.write(f'adding {total_count} ID: {store_id}')
                TimeStamp.objects.create(store=store, status=status, timestamp_utc=timestamp_obj)
                # except:
                #     self.stdout.write('except')
                #     continue
        self.stdout.write(f'total_count finished: {total_count}')

    def parse_timestamp(self, timestamp_str):
        # Remove 'UTC' and any trailing/leading whitespace
        timestamp_str = timestamp_str.replace('UTC', '').strip()

        # Define regex pattern for datetime with optional microseconds
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.(\d{1,6}))?'
        match = re.match(pattern, timestamp_str)

        if match:
            date_part, microseconds = match.groups()
            dt = datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S")
            
            if microseconds:
                microseconds = microseconds.ljust(6, '0')[:6]
                dt = dt.replace(microsecond=int(microseconds))

            return dt.replace(tzinfo=pytz.UTC)
        else:
            raise ValueError(f"Invalid timestamp format: {timestamp_str}")