# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, time, timedelta

app = FastAPI(title="Timetable API")

# allow the frontend to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Your timetable (exactly as you provided) ----------
TIMETABLE = {
  "Monday": [
    ["08:00", "09:00", "SE&PM"],
    ["09:00", "10:00", "Library"],
    ["10:00", "10:30", "Break"],
    ["10:30", "11:30", "RM&IPR"],
    ["11:30", "12:30", "CV"],
    ["12:30", "13:30", "Lunch"],
    ["13:30", "14:30", "Mentoring"],
    ["14:30", "15:30", "NSS"]
  ],
  "Tuesday": [
    ["08:00", "09:00", "RM&IPR"],
    ["09:00", "10:00", "TC"],
    ["10:00", "10:30", "Break"],
    ["10:30", "12:30", "CN Lab"],
    ["12:30", "13:30", "Lunch"],
    ["13:30", "14:30", "NSS"],
    ["14:30", "16:30", "Mini Project"]
  ],
  "Wednesday": [
    ["08:00", "09:00", "CN"],
    ["09:00", "10:00", "EVS"],
    ["10:00", "10:30", "Break"],
    ["10:30", "11:30", "SE&PM"],
    ["11:30", "12:30", "TC"],
    ["12:30", "13:30", "Lunch"],
    ["13:30", "14:30", "Remedial"],
    ["14:30", "16:30", "Mini Project"]
  ],
  "Thursday": [
    ["08:00", "09:00", "RM&IPR"],
    ["09:00", "10:00", "CV"],
    ["10:00", "10:30", "Break"],
    ["10:30", "11:30", "CN"],
    ["11:30", "12:30", "SE&PM"],
    ["12:30", "13:30", "Lunch"],
    ["13:30", "14:30", "TC"]
  ],
  "Friday": [
    ["08:00", "09:00", "TC"],
    ["09:00", "10:00", "CN"],
    ["10:00", "10:30", "Break"],
    ["10:30", "11:30", "SE&PM"],
    ["11:30", "12:30", "CV"],
    ["12:30", "13:30", "Lunch"],
    ["13:30", "15:30", "Forum Activity"]
  ],
  "Saturday": [
    ["08:00", "10:00", "DV Lab"],
    ["10:00", "10:30", "Break"],
    ["10:30", "11:30", "RM&IPR"],
    ["11:30", "12:30", "TC"],
    ["12:30", "13:30", "Lunch"]
  ]
}
# ---------------------------------------------------------------

def parse_time_hhmm(s: str) -> time:
    hh, mm = map(int, s.split(":"))
    return time(hour=hh, minute=mm)

def sessions_for_day(day_name: str):
    """Return list of session dicts for day_name with parsed times."""
    slots = TIMETABLE.get(day_name, [])
    result = []
    for start, end, subj in slots:
        result.append({
            "start": start,
            "end": end,
            "subject": subj,
            "start_time": parse_time_hhmm(start),
            "end_time": parse_time_hhmm(end),
        })
    return result

def today_name():
    return datetime.now().strftime("%A")

def find_current_and_next():
    now_dt = datetime.now()
    now_time = now_dt.time()
    today = today_name()
    sessions = sessions_for_day(today)

    current = None
    next_s = None

    # find current and next in today's schedule
    for i, s in enumerate(sessions):
        if s["start_time"] <= now_time < s["end_time"]:
            current = {"start": s["start"], "end": s["end"], "subject": s["subject"], "day": today}
            if i + 1 < len(sessions):
                n = sessions[i + 1]
                next_s = {"start": n["start"], "end": n["end"], "subject": n["subject"], "day": today}
            break
        if now_time < s["start_time"] and next_s is None:
            next_s = {"start": s["start"], "end": s["end"], "subject": s["subject"], "day": today}
            break

    # if no current and no next today, look for next day's first session (up to 6 days ahead)
    if not current and not next_s:
        for d in range(1, 7):
            check_day_dt = now_dt + timedelta(days=d)
            check_day = check_day_dt.strftime("%A")
            s_list = sessions_for_day(check_day)
            if s_list:
                f = s_list[0]
                next_s = {"start": f["start"], "end": f["end"], "subject": f["subject"], "day": check_day}
                break

    return current, next_s

@app.get("/")
def root():
    return {"message": "Timetable API up. Use /timetable, /timetable/{day}, /today, /now."}

@app.get("/timetable")
def get_timetable():
    return TIMETABLE

@app.get("/timetable/{day}")
def get_timetable_day(day: str):
    day_cap = day.capitalize()
    return { "day": day_cap, "sessions": [
        {"start": s[0], "end": s[1], "subject": s[2]} for s in TIMETABLE.get(day_cap, [])
    ] }

@app.get("/today")
def get_today():
    t = today_name()
    sessions = [{"start": s[0], "end": s[1], "subject": s[2]} for s in TIMETABLE.get(t, [])]
    return {"day": t, "sessions": sessions}

@app.get("/now")
def get_now():
    current, nxt = find_current_and_next()
    return {"current": current, "next": nxt}
