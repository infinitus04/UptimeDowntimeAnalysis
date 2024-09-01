from django.db import models

# Create your models here.
class Store(models.Model):
    store_id = models.CharField(max_length=50, unique=True)
    timezone_str = models.CharField(max_length=50, default='America/Chicago')

class OpenTime(models.Model):
    store = models.ForeignKey(Store,on_delete= models.CASCADE)
    day = models.IntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

class TimeStamp(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    status = models.BooleanField()
    timestamp_utc = models.DateTimeField(auto_now=False, auto_now_add=False)

class UptimeDowntimeLog(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    uptime = models.FloatField(default=0)
    downtime = models.FloatField(default=0)
    date= models.DateTimeField()
    


class Report(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=20, choices=[('Running', 'Running'), ('Complete', 'Complete')])
    file = models.FileField(upload_to='reports/', null=True, blank=True)

