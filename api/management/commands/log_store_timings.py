from django.core.management.base import BaseCommand
from api.models import OpenTime, Store, TimeStamp, UptimeDowntimeLog
from datetime import datetime, time
import pytz

class Command(BaseCommand):
    help = 'Calculate store uptime and downtime'

    def handle(self, *args, **options):
        all_stores = Store.objects.all()
        for st in all_stores:
            try:
                self.process_store(st)
                self.stdout.write(self.style.SUCCESS(f"Finished: {st.store_id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error at: {st.store_id} - {str(e)}"))

    def process_store(self, st):
        target_timezone = pytz.timezone(st.timezone_str)
        all_ts = TimeStamp.objects.filter(store=st).order_by('timestamp_utc')
        
        current_date = None
        daily_timestamps = []
        
        for ts in all_ts:
            ts.timestamp_utc = ts.timestamp_utc.astimezone(target_timezone)
            if current_date != ts.timestamp_utc.date():
                if daily_timestamps:
                    self.day_processor(daily_timestamps, st)
                daily_timestamps = []
                current_date = ts.timestamp_utc.date()
            daily_timestamps.append(ts)
        
        if daily_timestamps:
            self.day_processor(daily_timestamps, st)

    def day_processor(self, timestamp_list, st):
        if not timestamp_list:
            return

        store = timestamp_list[0].store
        date = timestamp_list[0].timestamp_utc.date()
        weekday = date.weekday()
        
        try:
            open_time = OpenTime.objects.filter(store=store, day=weekday).first()

            if open_time:
                start_time_local = datetime.combine(date, open_time.start_time_local)
                end_time_local = datetime.combine(date, open_time.end_time_local)
            else:
        # If no OpenTime data, consider the store open for 24 hours
                start_time_local = datetime.combine(date, time.min)
                end_time_local = datetime.combine(date, time.max)
        except OpenTime.DoesNotExist:
            start_time_local = datetime.combine(date, time.min)
            end_time_local = datetime.combine(date, time.max)

        timezone = pytz.timezone(store.timezone_str)
        start_time_local = timezone.localize(start_time_local)
        end_time_local = timezone.localize(end_time_local)

        uptime = downtime = 0
        previous_time = start_time_local
        previous_status = None

        for ts in timestamp_list:
            current_time = max(ts.timestamp_utc, start_time_local)
            if current_time >= end_time_local:
                break

            if previous_status is not None:
                time_diff = (current_time - previous_time).total_seconds() / 3600.0
                if previous_status:
                    uptime += time_diff
                else:
                    downtime += time_diff

            previous_status = ts.status
            previous_time = current_time

        # Handle the time after the last timestamp to the end time
        if previous_time < end_time_local:
            time_diff = (end_time_local - previous_time).total_seconds() / 3600.0
            if previous_status:
                uptime += time_diff
            else:
                downtime += time_diff

        total_time = (end_time_local - start_time_local).total_seconds() / 3600.0

        # Ensure uptime + downtime equals total_time
        if abs(total_time - (uptime + downtime)) > 1e-6:  # it just somehow works
            difference = total_time - (uptime + downtime)
            if uptime > downtime:
                uptime += difference
            else:
                downtime += difference

        UptimeDowntimeLog.objects.create(
            uptime=uptime,
            downtime=downtime,
            store=st,
            date=date
        )

        self.stdout.write(self.style.SUCCESS(f"\tCompleted: {st.store_id} - {date}"))