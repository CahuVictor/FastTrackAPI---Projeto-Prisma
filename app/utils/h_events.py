# app/utils/h_events.py
from datetime import timezone

def order_and_slice(events, key_fn, limit=10, reverse=False, filter_fn=None):
    """
    Sorts and paginates a list of events by a given key function.

    Optionally, applies a filter before sorting, and returns only the first `limit` items.

    Args:
        events (list): List of event objects to process.
        key_fn (Callable): Function to extract a comparison key from each event.
        limit (int, optional): Maximum number of results to return. Defaults to 10.
        reverse (bool, optional): Whether to reverse the sort order. Defaults to False.
        filter_fn (Callable, optional): Function to filter events before sorting. Defaults to None.

    Returns:
        list: The sorted and sliced list of events.

    Example:
        # Get top 5 upcoming events
        from app.utils.h_events import order_and_slice, ensure_aware
        now = datetime.now(timezone.utc)
        upcoming = order_and_slice(
            [e for e in events if ensure_aware(e.event_date) >= now],
            key_fn=lambda e: ensure_aware(e.event_date),
            limit=5
        )
    """
    if filter_fn:
        events = filter(filter_fn, events)
    ordered = sorted(events, key=key_fn, reverse=reverse)[:limit]
    return list(ordered)

def ensure_aware(dt):
    """
    Ensure a datetime object is timezone-aware (UTC).

    This helper should be used whenever comparing or storing datetimes
    to guarantee consistency between offset-naive and offset-aware datetimes.

    - If the input datetime is naive (tzinfo is None), it is assumed to be in UTC and 
      a tzinfo=timezone.utc is added.
    - If already timezone-aware, returns as is.

    This prevents `TypeError: can't compare offset-naive and offset-aware datetimes`
    and is recommended for any event, timestamp, or interval logic in this project.

    Example:
        event_time = ensure_aware(event.event_date)
        now = datetime.now(timezone.utc)
        if event_time >= now:
            ...

    :param dt: A datetime object, naive or aware.
    :return: A UTC-aware datetime object.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt