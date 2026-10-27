"""Gotcha job data layer: seed jobs, live aggregation, match scoring, skill stats."""
import json
import urllib.request

# --- Seed jobs (UCD-flavoured sample pool) ---
SEED = [
    {"co": "Stripe", "icon": "💳", "role": "Frontend Intern", "type": "Internship",
     "pay": "€2,400/mo", "loc": "Dublin · Hybrid", "src": "LinkedIn",
     "skills": ["React", "TypeScript", "CSS"],
     "q": "We'd geek out over…", "a": "shaving 200ms off a checkout flow."},
    {"co": "UCD Research Lab", "icon": "🔬", "role": "Data Assistant", "type": "Student job",
     "pay": "€15/hr", "loc": "UCD Campus", "src": "UCD Careers",
     "skills": ["Python", "Pandas", "SQL"],
     "q": "A perfect week looks like…", "a": "clean data in, one neat chart out."},
    {"co": "Intercom", "icon": "💬", "role": "Grad SWE", "type": "Graduate",
     "pay": "€52k/yr", "loc": "Dublin", "src": "Company site",
     "skills": ["Ruby", "React", "PostgreSQL"],
     "q": "You'll fit if…", "a": "you ship small and often."},
    {"co": "Remote.co", "icon": "🌍", "role": "Junior Designer", "type": "Remote",
     "pay": "€1,800/mo", "loc": "Fully remote", "src": "RemoteOK",
     "skills": ["Figma", "UI", "Prototyping"],
     "q": "Our love language is…", "a": "a tidy component library."},
    {"co": "Café Nero", "icon": "☕", "role": "Weekend Barista", "type": "Side job",
     "pay": "€13.5/hr", "loc": "Dublin 2", "src": "Indeed",
     "skills": ["Customer care", "Teamwork"],
     "q": "Best shift ever…", "a": "rush hour and a good playlist."},
    {"co": "HubSpot", "icon": "🧡", "role": "Marketing Grad", "type": "Graduate",
     "pay": "€40k/yr", "loc": "Dublin · Hybrid", "src": "LinkedIn",
     "skills": ["Analytics", "SEO", "Content"],
     "q": "We'd swipe right on…", "a": "a data-backed campaign idea."},
    {"co": "TutorMe", "icon": "📚", "role": "CS Tutor", "type": "Student job",
     "pay": "€20/hr", "loc": "Remote", "src": "UCD Careers",
     "skills": ["Java", "Teaching", "React"],
     "q": "Ideal match…", "a": "you explain recursion with pizza."},
]

# In-memory event log (swipes) — would be a DB in production.
EVENTS = []


def fetch_remoteok(limit=4):
    """Pull a few live remote roles from RemoteOK's public JSON API.

    Best-effort: returns [] on any network/parse error so the demo never breaks.
    """
    try:
        req = urllib.request.Request(
            "https://remoteok.com/api",
            headers={"User-Agent": "Gotcha-hackathon/0.1"},
        )
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []

    out = []
    for item in data:
        if not isinstance(item, dict) or not item.get("position"):
            continue  # first element is a legal notice
        tags = [t.capitalize() for t in (item.get("tags") or [])][:3]
        out.append({
            "co": item.get("company", "Remote role"),
            "icon": "🌍",
            "role": item.get("position", "Remote role"),
            "type": "Remote",
            "pay": item.get("salary_min") and f"${item['salary_min']}+/yr" or "Remote",
            "loc": item.get("location") or "Fully remote",
            "src": "RemoteOK (live)",
            "skills": tags or ["Remote"],
            "q": "Why this role…",
            "a": "work from anywhere, ship real product.",
        })
        if len(out) >= limit:
            break
    return out


def match_pct(job, user_skills, user_types):
    """Overlap of a job's skills with the user's interests (+ a type-fit bonus)."""
    skills = job["skills"] or []
    overlap = sum(1 for s in skills if s in user_skills)
    pct = 35 + round(55 * (overlap / len(skills))) if skills else 35
    if job["type"] in user_types:
        pct += 8
    return max(40, min(99, pct))


def get_jobs(user_skills, user_types, include_live=True):
    """Aggregated + scored + sorted feed."""
    pool = list(SEED)
    if include_live:
        pool += fetch_remoteok()
    for j in pool:
        j["match"] = match_pct(j, user_skills, user_types)
    pool.sort(key=lambda j: j["match"], reverse=True)
    return pool


def top_skill():
    """Most frequent skill across all swiped cards (data for the hidden reel)."""
    freq = {}
    for e in EVENTS:
        for s in e.get("skills", []):
            freq[s] = freq.get(s, 0) + 1
    if not freq:
        return None
    return max(freq.items(), key=lambda kv: kv[1])[0]
