# takeHomeAssignment
How Report generation works!

1. generate_report(report_id, datetimenow)

    Purpose: This function generates a report for a given report ID. It calculates the uptime and downtime for each store for the last hour, day, week, and month, and saves the results to a CSV file.
    Parameters:
        report_id: The ID of the report to generate.
        datetimenow: The current date and time used as a reference point for calculations.
    Process:
        Fetches the report and all stores from the database.
        For each store, it calls process_store to get uptime and downtime data.
        Calculates the uptime and downtime for the last hour.
        Writes the results to a CSV file and updates the report status to 'Complete'.

2. process_store(st, datetimenow)

    Purpose: This function processes the uptime and downtime data for a single store over the last 30 days.
    Parameters:
        st: The store to process.
        datetimenow: The current date and time used as a reference point.
    Process:
        Converts timestamps to the store's local time zone.
        Groups timestamps by day and processes each day with day_processor.
        Sums up the uptime and downtime for the last day, last 7 days, and last 30 days.
    Returns: A dictionary containing the store's ID and its uptime and downtime for the last day, week, and month.

3. day_processor(timestamp_list, st)

    Purpose: This function calculates the uptime and downtime for a specific store on a given day.
    Parameters:
        timestamp_list: A list of timestamps for a particular day.
        st: The store to process.
    Process:
        Determines the store's opening and closing times for the day.
        Calculates the time the store was up (operational) and down (non-operational) based on the timestamps.
        Adjusts for any differences between the total calculated time and the store's scheduled hours.
    Returns: A dictionary containing the date, uptime, and downtime for that day.
