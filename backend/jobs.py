"""Gotcha job data layer: seed jobs, live aggregation, match scoring, skill stats."""
import json
import urllib.request

# --- Seed jobs (UCD-flavoured sample pool) ---
SEED = [
    {"co": "Stripe", "icon": "💳", "role": "Frontend Intern", "type": "Internship",
     "pay": "€2,400/mo", "loc": "Dublin · Hybrid", "src": "LinkedIn",
     "skills": ["React", "TypeScript", "CSS"],
     "hours": "Mon–Fri · full-time (summer)",
     "requirements": ["2nd-year+ Computer Science", "Comfortable with React", "A portfolio or GitHub"],
     "vibe": ["fast", "solo", "office"],
     "q": "We'd geek out over…", "a": "shaving 200ms off a checkout flow."},
    {"co": "UCD Research Lab", "icon": "🔬", "role": "Data Assistant", "type": "Student job",
     "pay": "€15/hr", "loc": "UCD Campus", "src": "UCD Careers",
     "skills": ["Python", "Pandas", "SQL"],
     "hours": "~8 h/week · flexible around lectures",
     "requirements": ["Current UCD student", "Python + basic stats", "Tidy, careful with data"],
     "vibe": ["structured", "solo", "office"],
     "q": "A perfect week looks like…", "a": "clean data in, one neat chart out."},
    {"co": "Intercom", "icon": "💬", "role": "Grad SWE", "type": "Graduate",
     "pay": "€52k/yr", "loc": "Dublin", "src": "Company site",
     "skills": ["Ruby", "React", "PostgreSQL"],
     "hours": "Mon–Fri · 9:30–18:00",
     "requirements": ["2:1 degree or higher", "One backend language", "Solid CS fundamentals"],
     "vibe": ["fast", "solo", "office"],
     "q": "You'll fit if…", "a": "you ship small and often."},
    {"co": "Remote.co", "icon": "🌍", "role": "Junior Designer", "type": "Remote",
     "pay": "€1,800/mo", "loc": "Fully remote", "src": "RemoteOK",
     "skills": ["Figma", "UI", "Prototyping"],
     "hours": "Full-time · async, flexible",
     "requirements": ["A Figma portfolio", "1 internship or project", "Self-managed worker"],
     "vibe": ["fast", "solo", "remote"],
     "q": "Our love language is…", "a": "a tidy component library."},
    {"co": "Café Nero", "icon": "☕", "role": "Weekend Barista", "type": "Side job",
     "pay": "€13.5/hr", "loc": "Dublin 2", "src": "Indeed",
     "skills": ["Customer care", "Teamwork"],
     "hours": "Sat–Sun · 8-hour shifts",
     "requirements": ["No experience needed", "Weekend availability", "Right to work in Ireland"],
     "vibe": ["people", "structured", "office"],
     "q": "Best shift ever…", "a": "rush hour and a good playlist."},
    {"co": "Deliveroo", "icon": "🚲", "role": "Delivery Rider", "type": "Side job",
     "pay": "€12–18/hr", "loc": "Dublin city", "src": "Indeed",
     "skills": ["Time management", "Navigation"],
     "hours": "Evenings & weekends · fully flexible",
     "requirements": ["Own bike or e-scooter", "A smartphone", "Right to work in Ireland"],
     "vibe": ["fast", "solo", "office"],
     "q": "A good shift is…", "a": "dry weather and short waits."},
    {"co": "Penneys", "icon": "🛍️", "role": "Retail Assistant", "type": "Side job",
     "pay": "€13.7/hr", "loc": "Dublin 1", "src": "Indeed",
     "skills": ["Customer care", "Teamwork"],
     "hours": "Weekends + late-night openings",
     "requirements": ["No experience needed", "Friendly & reliable", "Right to work in Ireland"],
     "vibe": ["people", "structured", "office"],
     "q": "Best part of the job…", "a": "a tidy rail and happy customers."},
    {"co": "UCD Events", "icon": "🎪", "role": "Event Steward", "type": "Side job",
     "pay": "€14/hr", "loc": "UCD Campus", "src": "UCD Careers",
     "skills": ["Communication", "Teamwork"],
     "hours": "Event days · ad-hoc shifts",
     "requirements": ["Current UCD student", "Some weekend availability", "Clear communicator"],
     "vibe": ["people", "structured", "office"],
     "q": "Ideal shift…", "a": "a buzzing event that runs on time."},
    {"co": "HubSpot", "icon": "🧡", "role": "Marketing Grad", "type": "Graduate",
     "pay": "€40k/yr", "loc": "Dublin · Hybrid", "src": "LinkedIn",
     "skills": ["Analytics", "SEO", "Content"],
     "hours": "Mon–Fri · hybrid (3 days in office)",
     "requirements": ["Marketing or business degree", "Analytics basics", "Strong writing"],
     "vibe": ["people", "fast", "office"],
     "q": "We'd swipe right on…", "a": "a data-backed campaign idea."},
    {"co": "TutorMe", "icon": "📚", "role": "CS Tutor", "type": "Student job",
     "pay": "€20/hr", "loc": "Remote", "src": "UCD Careers",
     "skills": ["Java", "Teaching", "React"],
     "hours": "Evenings · 6–10 h/week",
     "requirements": ["Completed intro CS", "Clear communicator", "Flexible evenings"],
     "vibe": ["people", "structured", "remote"],
     "q": "Ideal match…", "a": "you explain recursion with pizza."},
]

# In-memory event log (swipes) — would be a DB in production.
EVENTS = []

# Canonical skill -> aliases we look for in an uploaded CV.
SKILL_VOCAB = {
    "React": ["react", "react.js", "reactjs"],
    "TypeScript": ["typescript", "ts"],
    "Python": ["python", "pandas", "numpy", "django", "flask"],
    "SQL": ["sql", "postgres", "postgresql", "mysql", "sqlite"],
    "Figma": ["figma", "sketch"],
    "UI": ["ui", "ux", "ui/ux", "user interface", "wireframe"],
    "Java": ["java", "spring"],
    "Ruby": ["ruby", "rails"],
    "Analytics": ["analytics", "google analytics", "tableau", "power bi", "data analysis"],
    "SEO": ["seo", "search engine"],
    "Teaching": ["teaching", "tutor", "tutoring", "mentor"],
    "Customer care": ["customer", "barista", "retail", "hospitality", "support"],
}


def detect_skills(text):
    """Scan CV text and return the canonical skills it mentions."""
    t = (text or "").lower()
    found = []
    for skill, aliases in SKILL_VOCAB.items():
        if any(a in t for a in aliases):
            found.append(skill)
    return found


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
            "hours": "Full-time · remote",
            "requirements": (tags or ["Relevant experience"]) + ["Able to work remotely"],
            "q": "Why this role…",
            "a": "work from anywhere, ship real product.",
        })
        if len(out) >= limit:
            break
    return out


def match_pct(job, user_skills, user_types, user_vibes=()):
    """Skill overlap (+ type-fit bonus + personality/vibe fit)."""
    skills = job["skills"] or []
    overlap = sum(1 for s in skills if s in user_skills)
    pct = 35 + round(50 * (overlap / len(skills))) if skills else 35
    if job["type"] in user_types:
        pct += 8
    vibe_hits = sum(1 for v in (job.get("vibe") or []) if v in user_vibes)
    pct += vibe_hits * 4                      # personality-test boost
    return max(40, min(99, pct))


def get_jobs(user_skills, user_types, user_vibes=(), include_live=True):
    """Aggregated + scored + sorted feed."""
    pool = list(SEED)
    if include_live:
        pool += fetch_remoteok()
    for j in pool:
        j["match"] = match_pct(j, user_skills, user_types, user_vibes)
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
