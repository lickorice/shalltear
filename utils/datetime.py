from datetime import timedelta


def format_time_string(growing_time_in_seconds):
    growing_time = timedelta(seconds=growing_time_in_seconds)
    result_str = []
    hours, rem = divmod(growing_time.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    first_digit = True

    if growing_time.days:
        result_str.append("{}d".format(growing_time.days))
    if not first_digit or hours:
        result_str.append("{}h".format(hours))
    if not first_digit or minutes:
        result_str.append("{}m".format(minutes))
    if not first_digit or seconds:
        result_str.append("{}s".format(seconds))
    
    return ', '.join(result_str)