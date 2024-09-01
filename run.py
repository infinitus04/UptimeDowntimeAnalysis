from datetime import datetime
from django.utils import timezone
time = '2023-01-24 23:00:57.900649 UTC'
# timestamp_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")

def parse_and_save_datetime(datetime_str):
    # Regular expression to match the datetime pattern
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.\d+)?\s*(UTC)?'
    
    match = re.match(pattern, datetime_str)
    if match:
        # Extract the datetime part without microseconds
        date_part = match.group(1)
        
        # Parse the datetime
        parsed_datetime = datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S")
        
        # Make it timezone-aware (UTC)
        aware_datetime = timezone.make_aware(parsed_datetime, timezone=timezone.utc)
        
        return aware_datetime
    else:
        return -1

timestamp_obj = 
print(type(timestamp_obj))