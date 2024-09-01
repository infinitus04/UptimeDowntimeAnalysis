from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Report, Store, TimeStamp, OpenTime
from .serializer import ReportSerializer
from django.http import FileResponse
import threading
from datetime import datetime, timedelta, time
import uuid
import pytz
from io import StringIO
import csv
from django.core.files.base import ContentFile
from django.utils import timezone

@api_view(['GET'])
def trigger_report(request):
    datetimenow = request.query_params.get("datetime")
    if not datetimenow:
        return Response({'error': 'DateTime is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        utc_datetime = datetime.strptime(datetimenow, "%Y-%m-%d %H:%M:%S")
        utc_datetime = pytz.UTC.localize(utc_datetime)
    except ValueError:
        return Response({'error': 'Invalid datetime format'}, status=status.HTTP_400_BAD_REQUEST)

    report_id = str(uuid.uuid4())
    report = Report.objects.create(id=report_id, status='Running')
    
    threading.Thread(target=generate_report, args=(report_id, utc_datetime)).start()
    
    serializer = ReportSerializer(report)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_report(request):
    report_id = request.query_params.get('report_id')
    if not report_id:
        return Response({'error': 'report_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        report = Report.objects.get(id=report_id)
        if report.status == 'Running':
            serializer = ReportSerializer(report)
            return Response(serializer.data)
        elif report.status == 'Complete':
            response = FileResponse(report.file, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{report_id}.csv"'
            return response
    except Report.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

def generate_report(report_id, datetimenow):
    report = Report.objects.get(id=report_id)
    all_stores = Store.objects.all()
    all_store_data = []
    
    for st in all_stores:
        try:
            all_store_data.append(process_store(st, datetimenow))
            hrsmin= datetimenow - timedelta(hours=1)
            last_hour_data = TimeStamp.objects.filter(store =st, timestamp_utc__lte=datetimenow,timestamp_utc__gte=hrsmin )
            if not last_hour_data:
                uptime_last_hour = 0
                downtime_last_hour = 60
            else:
                if last_hour_data[0].status:
                    uptime_last_hour = 60
                    downtime_last_hour = 0
                else:
                    downtime_last_hour = 60
                    uptime_last_hour = 0
            all_store_data[-1]['uptime_last_hour'] = uptime_last_hour
            all_store_data[-1]['downtime_last_hour'] = downtime_last_hour

        except Exception as e:
                print(f"Error at: {st.store_id} - {str(e)}")
                continue
        

    # Convert all_store_data list to CSV
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)

    csv_writer.writerow(['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'uptime_last_month','downtime_last_hour','downtime_last_day', 'downtime_last_week', 'downtime_last_month'])
    for store_data in all_store_data:
        csv_writer.writerow([
            store_data['store_id'],
            store_data['uptime_last_hour'],
            store_data['uptime_1d'],
            store_data['uptime_7d'],
            store_data['uptime_30d'],
            store_data['downtime_last_hour'],
            store_data['downtime_1d'],
            store_data['downtime_7d'],
            store_data['downtime_30d']
        ])
    
    report.file.save(f'{report_id}.csv', ContentFile(csv_buffer.getvalue().encode()))
    report.status = 'Complete'
    report.save()

def process_store(st, datetimenow):
    target_timezone = pytz.timezone(st.timezone_str)
    start_datetime = datetimenow - timedelta(days=30)
    all_ts = TimeStamp.objects.filter(store=st, timestamp_utc__gte=start_datetime, timestamp_utc__lte=datetimenow).order_by('timestamp_utc')
    all_datetime_record = []
    current_date = None
    daily_timestamps = []
    
    for ts in all_ts:
        ts_local = ts.timestamp_utc.astimezone(target_timezone)
        if current_date != ts_local.date():
            if daily_timestamps:
                all_datetime_record.append(day_processor(daily_timestamps, st))
            daily_timestamps = []
            current_date = ts_local.date()
        daily_timestamps.append(ts)
    
    if daily_timestamps:
        all_datetime_record.append(day_processor(daily_timestamps, st))
    
    uptime_30d = downtime_30d = uptime_7d = downtime_7d = 0
    uptime_1d = downtime_1d = 0
    
    for i, record in enumerate(all_datetime_record[::-1]):
        if i == 0:  # Last day
            uptime_1d = record['uptime']
            downtime_1d = record['downtime']
        if i < 7:  # Last 7 days
            uptime_7d += record['uptime']
            downtime_7d += record['downtime']
        # Last 30 days
        uptime_30d += record['uptime']
        downtime_30d += record['downtime']
    
    return {
        'store_id': st.id,
        'uptime_1d': uptime_1d,
        'downtime_1d': downtime_1d,
        'uptime_7d': uptime_7d,
        'downtime_7d': downtime_7d,
        'uptime_30d': uptime_30d,
        'downtime_30d': downtime_30d,
    }

def day_processor(timestamp_list, st):
    if not timestamp_list:
        return None

    store = timestamp_list[0].store
    date = timestamp_list[0].timestamp_utc.astimezone(pytz.timezone(store.timezone_str)).date()
    weekday = date.weekday()
    
    
    open_time = OpenTime.objects.filter(store=store, day=weekday).first()
    if not open_time:
        start_time_local = datetime.combine(date, time.min)
        end_time_local = datetime.combine(date, time.max)
    else:
        start_time_local = datetime.combine(date, open_time.start_time_local)
        end_time_local = datetime.combine(date, open_time.end_time_local)
        # If no OpenTime data, consider the store open for 24 hours
    

    timezone = pytz.timezone(store.timezone_str)
    start_time_local = timezone.localize(start_time_local)
    end_time_local = timezone.localize(end_time_local)

    uptime = downtime = 0
    previous_time = start_time_local
    previous_status = None

    for ts in timestamp_list:
        current_time = max(ts.timestamp_utc.astimezone(timezone), start_time_local)
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

    if previous_time < end_time_local:
        time_diff = (end_time_local - previous_time).total_seconds() / 3600.0
        if previous_status:
            uptime += time_diff
        else:
            downtime += time_diff

    total_time = (end_time_local - start_time_local).total_seconds() / 3600.0

    if abs(total_time - (uptime + downtime)) > 1e-6:
        difference = total_time - (uptime + downtime)
        if uptime > downtime:
            uptime += difference
        else:
            downtime += difference

    return {
        'date': date,
        'uptime': uptime,
        'downtime': downtime,
    }