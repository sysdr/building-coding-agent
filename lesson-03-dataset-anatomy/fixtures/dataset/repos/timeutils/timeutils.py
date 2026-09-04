def is_weekend(day_index):
    return day_index in (5, 6)


def add_days(day_index, n):
    return (day_index + n) % 7 - 1
