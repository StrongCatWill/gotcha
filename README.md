# Gotcha 🎯

**A "job dating" app for UCD graduates and undergraduates.** Swipe through roles like Hinge, and Gotcha pulls only the jobs that match the criteria and interests you set.

Run the prototype: just open `index.html` in a browser (no build needed).

---

## Core concept
- **Swipe**: ❤️ apply / ✕ pass / ★ save — Hinge-style mechanic.
- **Multi-source aggregation**: jobs from LinkedIn · UCD Careers · company career pages · RemoteOK · Indeed in one feed.
- **Job-type filters**: Internship / Graduate / Student job / Side job / Remote.
- 🔓 **Hidden feature**: every 5 cards, the skill that appeared most across the roles you viewed is summarized as a **1-minute video**, served like an ad.

---

## 🧵 Thread split

### 🎨 Design thread
- [ ] Logo / color / type (brand purple `#6b4eff`)
- [ ] Swipe card layout + LIKE/NOPE stamps
- [ ] Filter chips, empty state, toasts
- [ ] Hidden skill-reel overlay UI
- [ ] Onboarding mockups (2 screens: criteria + interests)

### 💻 Frontend thread
- [x] Swipe interaction (drag + buttons) — `index.html`
- [x] Filtering logic / card-stack render
- [x] Trigger skill reel every 5 cards
- [ ] Onboarding → feed routing
- [ ] Saved / applications screen
- [ ] Wire up backend API (currently `JOBS` is hardcoded)

### 🔧 Backend thread
- [ ] Job aggregator / scraper: LinkedIn API, RemoteOK, Indeed, company pages
- [ ] Store user criteria + interests, matching & ranking
- [ ] Log swipe / save events
- [ ] **Skill frequency aggregation** → extract top skill from viewed roles (data for the hidden feature)
- [ ] Map each skill to its 1-minute video metadata

---

## ✅ Demo checklist (working in the prototype now)
- [x] Swipe job cards (left / right / save)
- [x] Switch job-type filters
- [x] Multi-source badges (LinkedIn / UCD / company / Remote…)
- [x] Hinge-style prompts ("We'd geek out over…")
- [x] Skill 1-min recap reel pops after every 5 cards
- [x] Viewed / saved counter
- [ ] (next) Onboarding criteria → personalized feed

---

## What we need right now (30-min demo)
1. Demo `index.html` as is — the swipe → 5 cards → reel flow.
2. Pitch angle: the differentiator is **"multi-source aggregation + a skill-learning loop."**
3. Next wiring: backend aggregation API replaces the frontend `JOBS` array.
