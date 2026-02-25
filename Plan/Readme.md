# Campus-to-Hire — MVP Build Plan
### AI for Bharat Hackathon · Prototype Phase · Deadline: March 4, 2026

---

## Overview

This document is the 7-day execution plan for building the **Campus-to-Hire Personalization Platform** MVP — an AI-driven product that gives Indian students (especially from Tier-2/3 colleges and non-English backgrounds) a personalized, structured roadmap to become job-ready.

**Team:** 3 people · **Budget:** $100 AWS credits · **Deadline:** March 4, 2026

**Deliverables:**
- Live working prototype URL
- GitHub repository
- Demo video
- Documentation

---

## Problem & Solution

**Problem:** Campus students fail to become job-ready efficiently because existing resources are generic, English-centric, and disconnected from individual backgrounds, skill gaps, and real hiring expectations — disproportionately hurting students from Tier-2/3 colleges.

**Solution:** An AI-powered platform using Amazon Bedrock that generates personalized weekly roadmaps, daily tasks, mock interviews, and JD skill-gap analysis — all in the user's preferred language (Hindi, Tamil, Telugu).

---

## Architecture

```
Browser
  │
  ▼
Next.js 14 Frontend  (Vercel / AWS Amplify)
  │  Google + GitHub OAuth via NextAuth.js
  │  JWT → FastAPI for all authenticated calls
  ▼
FastAPI Backend  (AWS EC2 t3.micro + Docker + nginx)
  │
  ├──→ Amazon Bedrock (Claude 3.5 Haiku / Sonnet)
  │       • Roadmap generation
  │       • Interview simulation & evaluation
  │       • JD skill extraction
  │
  ├──→ Amazon Translate
  │       • Hindi, Tamil, Telugu content translation
  │
  └──→ PostgreSQL  (Neon free tier)
          • All application data via SQLAlchemy
```

**AWS Services used:** Bedrock, Translate, EC2, S3, CloudFront, IAM

---

## MVP Feature Scope

### Included (P0 / P1)

| Feature | Description | Priority |
|---|---|---|
| Auth + Onboarding | 4-step wizard: background → skills → goals → preferences | P0 |
| AI Roadmap Generation | Bedrock generates a personalized weekly roadmap with milestones | P0 — Hero Feature |
| Daily Plan View | Derive from roadmap: today's tasks with checkboxes and time estimates | P0 |
| JD Mapping | Paste JD → Bedrock extracts required skills → show gap matrix | P0 |
| Multi-Language | Translate AI content to Hindi / Tamil / Telugu via Amazon Translate | P0 |
| Progress Dashboard | Tasks completed, roadmap %, streak counter, skill radar chart | P0 |
| Interview Simulation | Text-based mock interview: Bedrock asks role-specific Qs and evaluates answers | P1 |

### Cut for MVP

| Feature | Reason |
|---|---|
| Spaced repetition | Needs behavioral data over time |
| Resource curation DB | Hardcode a few links in roadmap instead |
| Adaptive learning engine | Needs usage data; impossible to demo in 7 days |
| Push / email notifications | Not needed for demo |
| Offline mode (PWA) | Complexity not worth it |
| Automated nightly plan generation | Generate on-demand instead |

---

## Tech Stack

### Frontend
| Library | Purpose |
|---|---|
| Next.js 14+ (App Router) | Framework (SSR + API routes) |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| shadcn/ui | UI components (buttons, cards, forms, dialogs, tabs) |
| React Hook Form + Zod | Form validation |
| Recharts | Dashboard charts (radar, line, bar) |
| Framer Motion | Subtle animations |
| react-markdown | Render Bedrock markdown output |
| lucide-react | Icons |

### Backend (FastAPI — Python)
| Library | Purpose |
|---|---|
| FastAPI | API framework |
| uvicorn | ASGI server |
| SQLAlchemy + Alembic | ORM + migrations |
| pydantic | Data validation |
| boto3 | AWS SDK (Bedrock, Translate) |
| python-jose / PyJWT | JWT token validation |
| passlib + bcrypt | Password hashing |
| httpx | Async HTTP client |
| python-dotenv | Environment config |

### Auth
| Library | Purpose |
|---|---|
| NextAuth.js (Auth.js) | Google + GitHub OAuth on the frontend |
| JWT tokens | Passed to FastAPI for every authenticated API call |

---

## Project Structure

```
campus-hire/
├── frontend/                           # Next.js 14 App
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx                # Landing page
│   │   │   ├── api/auth/[...nextauth]/route.ts
│   │   │   ├── onboarding/page.tsx     # 4-step wizard
│   │   │   └── dashboard/
│   │   │       ├── page.tsx            # Progress dashboard
│   │   │       ├── roadmap/page.tsx
│   │   │       ├── today/page.tsx
│   │   │       ├── interview/page.tsx
│   │   │       └── jd-analyze/page.tsx
│   │   ├── components/
│   │   │   ├── ui/                     # shadcn/ui
│   │   │   ├── onboarding/
│   │   │   ├── roadmap/
│   │   │   ├── daily-plan/
│   │   │   ├── interview/
│   │   │   ├── dashboard/
│   │   │   └── layout/
│   │   ├── lib/
│   │   │   ├── api.ts                  # Axios/fetch wrapper for FastAPI
│   │   │   └── auth.ts                 # NextAuth config
│   │   └── types/index.ts
│   ├── .env.local
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── package.json
│
├── backend/                            # FastAPI App
│   ├── app/
│   │   ├── main.py                     # Entry point + CORS
│   │   ├── config.py                   # Settings (env vars)
│   │   ├── database.py                 # SQLAlchemy engine + session
│   │   ├── models.py                   # User, Roadmap, DailyPlan, Interview
│   │   ├── schemas.py                  # Pydantic request/response schemas
│   │   ├── auth.py                     # JWT validation middleware
│   │   ├── routers/
│   │   │   ├── profile.py              # GET/PUT /api/profile
│   │   │   ├── roadmap.py              # POST /api/roadmap/generate
│   │   │   ├── daily_plan.py           # GET /api/daily-plan, PATCH task complete
│   │   │   ├── interview.py            # POST /api/interview/start, /respond
│   │   │   ├── jd.py                   # POST /api/jd/analyze
│   │   │   └── translate.py            # POST /api/translate
│   │   └── services/
│   │       ├── bedrock.py              # Bedrock client + helpers
│   │       ├── translate.py            # Amazon Translate client
│   │       └── prompts.py              # All AI prompt templates
│   ├── alembic/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
└── README.md
```

---

## Database Schema

```python
class User(Base):
    id, email, name, avatar_url, auth_provider
    college, college_tier, degree, major, current_year, is_cs_background
    target_role, target_companies, hours_per_day, days_per_week
    preferred_language, skills, onboarding_completed
    created_at, updated_at

class Roadmap(Base):
    id, user_id → users.id
    content (JSON — full Bedrock roadmap)
    pace, total_weeks, current_week, current_day, is_active
    created_at

class DailyPlan(Base):
    id, roadmap_id → roadmaps.id
    week, day
    tasks (JSON — [{id, title, type, duration, completed}])
    created_at

class Interview(Base):
    id, user_id → users.id
    role, company
    messages (JSON — conversation history)
    score, feedback
    created_at
```

---

## Day-by-Day Schedule

### Team Roles
- **Dev A — Frontend Lead:** Next.js, UI pages, components, forms, charts, NextAuth OAuth
- **Dev B — Backend Lead:** FastAPI, SQLAlchemy models, API endpoints, deployment
- **Dev C — AI/ML Lead:** Bedrock integration, prompt engineering, Translate, interview AI logic

---

### Day 1 — Foundation Setup

| Dev A (Frontend) | Dev B (Backend) | Dev C (AI/ML) |
|---|---|---|
| Init Next.js 14 + TS + Tailwind + shadcn/ui | Init FastAPI + SQLAlchemy + Alembic | Set up AWS account, enable Bedrock models in `ap-south-1` |
| Configure NextAuth.js (Google + GitHub) | Define DB models, run migrations on Neon | Write & test Bedrock prompts (roadmap, interview) in Python |
| Build landing page + auth flow UI | Set up CORS + JWT validation middleware | Test boto3 Bedrock + Translate API calls |
| Deploy frontend skeleton to Vercel/Amplify | Deploy backend to EC2 or Railway | Document prompt templates |
| **✓ Live frontend URL with OAuth working** | **✓ FastAPI running with DB connected** | **✓ Bedrock returning structured JSON** |

### Day 2 — Onboarding + Roadmap Generation

| Dev A (Frontend) | Dev B (Backend) | Dev C (AI/ML) |
|---|---|---|
| Build 4-step onboarding wizard (React Hook Form + Zod) | Build PUT /api/profile | Build POST /api/roadmap/generate with Bedrock |
| Build roadmap display page (timeline/milestones) | Build GET /api/profile | Iterate roadmap prompt for CS vs non-CS profiles |
| Wire onboarding form → backend API | Build GET /api/roadmap | Test with different target roles/companies |
| **✓ Onboarding wizard saves to DB** | **✓ Profile + roadmap APIs working** | **✓ Quality AI-generated roadmaps** |

### Day 3 — Daily Plans + JD Mapping

| Dev A (Frontend) | Dev B (Backend) | Dev C (AI/ML) |
|---|---|---|
| Build daily plan page (task list + checkboxes) | Build GET /api/daily-plan (derive from roadmap JSON) | Build POST /api/jd/analyze with Bedrock |
| Build JD paste form + skill gap matrix UI | Build PATCH /api/daily-plan/task/:id/complete | Engineer JD skill extraction prompt |
| Add category badges, time estimates to tasks | Build daily plan derivation logic | Build POST /api/translate with Amazon Translate |
| **✓ Daily plan + JD analysis pages** | **✓ Daily plan + JD APIs working** | **✓ JD analysis + translate working** |

### Day 4 — Interview Simulation + Translation

| Dev A (Frontend) | Dev B (Backend) | Dev C (AI/ML) |
|---|---|---|
| Build interview chat UI (message bubbles) | Build POST /api/interview/start | Build interview Q&A logic with Bedrock |
| Build progress dashboard page | Build POST /api/interview/respond | Add company-specific interview formats |
| Add Recharts (skill radar, progress timeline) | Build GET /api/interview/history | Integrate Translate into roadmap/plan responses |
| Add language selector to UI | Wire translation into existing endpoints | Test multi-language output quality |
| **✓ Interview + dashboard UI** | **✓ Interview + translate APIs** | **✓ AI interview evals working** |

### Day 5 — Integration + Polish

| Dev A (Frontend) | Dev B (Backend) | Dev C (AI/ML) |
|---|---|---|
| End-to-end flow testing | Fix API bugs, add error handling | Edge case handling in AI responses |
| Mobile responsiveness pass | API response validation | Prompt refinement from testing |
| Loading skeletons, empty states | Deployment + HTTPS setup | Fallback for Bedrock failures |
| Navigation polish, sidebar | Rate limiting, request validation | Cache Bedrock responses in DB |
| **✓ Full flow works end-to-end on live URL** | | |

### Day 6 — Documentation + Demo Video

| Dev A (Frontend) | Dev B (Backend) | Dev C (AI/ML) |
|---|---|---|
| Screenshots, UI polish | Write deployment guide + README | Record demo video (full user journey) |
| Fix visual bugs | Architecture diagram | Write project summary + problem statement |
| Final frontend deployment | Final backend deployment verification | Edit and upload video |
| **✓ All docs + video complete** | | |

### Day 7 — Buffer + Submission (March 4)
- All: Final bug fixes, fresh account test, cross-browser check
- **Submit:** GitHub repo URL · Live prototype URL · Video link (YouTube/Drive) · Documentation

---

## Cost Budget

| Service | Estimated Cost |
|---|---|
| AWS EC2 t3.micro (backend) | $0 — free tier (750 hrs/month) |
| Amazon Bedrock (Haiku/Sonnet) | $5–15 (~500 requests) |
| Amazon Translate | $0.50–2 |
| Frontend (Vercel / Amplify free tier) | $0 |
| PostgreSQL (Neon free tier) | $0 |
| **Total** | **~$6–17 of $100** |

---

## Deployment

| Component | Platform |
|---|---|
| Frontend | Vercel (free) or AWS Amplify (free tier) |
| Backend | AWS EC2 t3.micro — Docker + nginx reverse proxy |
| Database | Neon PostgreSQL (free tier, external) |

---

## Verification Checklist

Before submission, validate the following end-to-end:

1. **Fresh user test** — Register → onboarding → generate roadmap → view daily plan → complete tasks → mock interview → analyze JD → check dashboard → switch language
2. **Mobile test** — Full flow on phone-width browser
3. **Multi-profile test** — CS student vs non-CS student roadmaps differ meaningfully
4. **Translation test** — Roadmap content renders correctly in Hindi and Tamil
5. **Live URL** — Accessible from an external network (not just localhost)
6. **Demo video** — Covers the complete user journey in under 5 minutes

---

## Key Files (Build Order)

### Backend (FastAPI)
1. `backend/app/main.py` — FastAPI entry point + CORS
2. `backend/app/models.py` — SQLAlchemy models
3. `backend/app/database.py` — DB engine + session factory
4. `backend/app/auth.py` — JWT validation middleware
5. `backend/app/services/bedrock.py` — Bedrock client wrapper
6. `backend/app/services/prompts.py` — All AI prompt templates
7. `backend/app/services/translate.py` — Amazon Translate wrapper
8. `backend/app/routers/roadmap.py` — Hero endpoint: POST /api/roadmap/generate
9. `backend/app/routers/profile.py` — Profile CRUD
10. `backend/app/routers/daily_plan.py` — Daily plan derivation + task completion
11. `backend/app/routers/interview.py` — Mock interview start + respond
12. `backend/app/routers/jd.py` — JD analysis endpoint
13. `backend/requirements.txt`
14. `backend/Dockerfile`

### Frontend (Next.js)
1. `frontend/package.json` + `next.config.js` + `tailwind.config.ts`
2. `frontend/src/lib/auth.ts` — NextAuth config (Google + GitHub)
3. `frontend/src/lib/api.ts` — API client for FastAPI
4. `frontend/src/app/page.tsx` — Landing page
5. `frontend/src/app/onboarding/page.tsx` — 4-step wizard
6. `frontend/src/app/dashboard/page.tsx` — Progress dashboard
7. `frontend/src/app/dashboard/roadmap/page.tsx` — Roadmap timeline
8. `frontend/src/app/dashboard/today/page.tsx` — Daily plan
9. `frontend/src/app/dashboard/interview/page.tsx` — Mock interview chat
10. `frontend/src/app/dashboard/jd-analyze/page.tsx` — JD mapping
