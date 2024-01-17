def update_end_time_dropdown(start_hour, start_minute, end_hour):
    if start_hour and start_minute:
        hour = int(start_hour)
        minute = int(start_minute)
        if end_hour:
            end_hour = int(end_hour)
        hours = [{'label': str(h).zfill(2), 'value': str(h).zfill(2)} for h in range(hour, 24)]
        if hour == end_hour:
            minutes = [{'label': str(m).zfill(2), 'value': str(m).zfill(2)} for m in range(minute, 60)]
        else:
            minutes = [{'label': str(m).zfill(2), 'value': str(m).zfill(2)} for m in range(60)]
        return hours, minutes
    return [], []