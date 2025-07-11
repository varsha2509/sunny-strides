import typing as ta

import pandas as pd


def format_running_times_for_email_template(times_list: ta.List[pd.Timestamp]) -> str:
    running_times_by_date_dict: ta.Dict[str, ta.List[str]] = {}
    for timestamp in times_list:
        date = timestamp.strftime("%Y-%m-%d")
        time = timestamp.strftime("%H:%M")

        if date not in running_times_by_date_dict:
            running_times_by_date_dict[date] = [time]
        else:
            running_times_by_date_dict[date].append(time)

    html_body: ta.List[str] = []
    for date in sorted(running_times_by_date_dict):
        times_str = ", ".join(sorted(running_times_by_date_dict[date]))
        html_body.append(f"<li><strong>{date}:</strong> {times_str}</li>")

    return "".join(html_body)
