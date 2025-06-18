# app/utils/h_events.py
def order_and_slice(events, key_fn, limit=10, reverse=False, filter_fn=None):
    if filter_fn:
        events = filter(filter_fn, events)
    ordered = sorted(events, key=key_fn, reverse=reverse)[:limit]
    return list(ordered)
