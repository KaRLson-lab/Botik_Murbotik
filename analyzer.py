from db_handler import get_entries

def get_stats(user_id, days=7):
    rows = get_entries(user_id, days)
    if not rows:
        return None

    moods       = [r["mood"]       for r in rows]
    work_hours  = [r["work_hours"] for r in rows]
    sleep_hours = [r["sleep_hours"] for r in rows]

    best_day = max(rows, key=lambda r: r["mood"])
    worst_day = min(rows, key=lambda r: r["mood"])

    good_sleep = [r["mood"] for r in rows if r["sleep_hours"] >= 7]
    bad_sleep  = [r["mood"] for r in rows if r["sleep_hours"] < 7]
    avg_mood_good_sleep = round(sum(good_sleep) / len(good_sleep), 2) if good_sleep else "—"
    avg_mood_bad_sleep  = round(sum(bad_sleep)  / len(bad_sleep),  2) if bad_sleep  else "—"

    return {
        "count":      len(rows),
        "avg_mood":   round(sum(moods) / len(moods), 2),
        "avg_work":   round(sum(work_hours) / len(work_hours), 2),
        "avg_sleep":  round(sum(sleep_hours) / len(sleep_hours), 2),
        "best_day":   best_day["created_at"][:10],
        "worst_day":  worst_day["created_at"][:10],
        "mood_good_sleep": avg_mood_good_sleep,
        "mood_bad_sleep":  avg_mood_bad_sleep,
    }