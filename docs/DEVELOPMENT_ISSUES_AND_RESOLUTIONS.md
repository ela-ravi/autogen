# Development issues, solutions, and outcomes

This document summarizes problems encountered while building and deploying the Video Recap application (FastAPI + Next.js + Celery + Docker), choices that were made (yours and implementation-side), how behavior improved, and trade-offs / side effects where they matter.

It is based on the development and deployment arc (local, Docker, Hostinger/VPS, Traefik). It is **not** a complete forensic log of every bug.

---

## Legend

- **You** — product or ops decisions, constraints, or fixes you drove (e.g. infra, “use GitHub Actions”, “separate Linux user”).
- **Implementation** — architectural or code changes applied in the repo (often proposed and then implemented in collaboration).
- **Outcome** — what got better.
- **Side effects** — regressions, operational cost, or things to watch later.

---

## 1. Deployment and security on a shared VPS (OpenClaw + this app)

| Aspect | Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|--------|----------------|---------------------------|---------|----------------|
| Isolation | OpenClaw already on the same VPS; risk if one stack is compromised | Run this app under a **dedicated Linux user** (e.g. `videorecap`), not `openclaw` or root for daily ops | Same; compose/deploy owned by that user; secrets in env / GitHub, not in image | Blast radius reduced; clearer ownership | Two users to patch/SSH; docs must say which user owns which tree |
| CI/CD | Manual deploys error-prone | **GitHub Actions** deploy on push to `main` | Workflow + SSH; secrets for key/host | Repeatable deploys | Broken pipeline blocks release until secrets/SSH fixed |
| Routing | Port 80 used by Traefik; app on host ports | Subdomain `recap.hallucinotai.com` + existing Traefik | Frontend/backend on localhost bind; Traefik labels / routing plan | HTTPS without stealing OpenClaw’s setup | DNS + Traefik config must stay correct; wrong label → 404 |

---

## 2. Frontend cannot reach API (`/api/v1/*` 404, wrong host)

| Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|----------------|---------------------------|---------|--------------|
| Browser called wrong origin (e.g. `localhost:3000/api/v1` → Next, not API) | Set **`NEXT_PUBLIC_API_URL`** for real API base; clarify prod vs local | **Root `.env` → `next.config.js`** for `NEXT_PUBLIC_*`; **dev rewrites** when URL empty; **middleware** `rewrite` for `/api/v1` → backend with `BACKEND_INTERNAL_URL` in Docker | Login, `/meta`, and API work in dev and when frontend uses relative `/api/v1` | More moving parts: must set `BACKEND_INTERNAL_URL` in compose for container→container proxy; mis-ENV still breaks |
| Middleware ignored `/api` | — | **Include `/api/v1/:path*` in matcher** and proxy before auth redirects | `/meta` and API reachable through Next when using same-origin URLs | Matcher order must stay correct so API isn’t accidentally redirected to `/login` without token in edge cases |

---

## 3. Environment variables and Docker

| Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|----------------|---------------------------|---------|--------------|
| `docker compose restart` didn’t pick up new `.env` | Recreate containers when env changes | **`docker compose up -d --force-recreate backend`** (and similar) | Feature flags and `GOOGLE_CLIENT_ID` match file | Easy to forget; docs should say “recreate, not only restart” |
| **`frontend/.next` in Git** | — | **`.gitignore`**: `.next/`, `frontend/.next/`, etc. | Status noise and accidental commits of build output dropped | `next-env.d.ts` / lockfile policy should stay explicit (commit lockfile, optional env d) |

---

## 4. Billing, quota, and feature flags

| Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|----------------|---------------------------|---------|--------------|
| Billing not ready but UI showed quotas | **Feature-flag billing**; gray out or message, not fake billing | `ENABLE_BILLING`, `BILLING_DISABLED_MESSAGE`; quota checks **no-op** when billing off; usage summary **unlimited** when off | No confusing “3/mo” when you’re not charging | When billing is turned on, behavior changes suddenly—need comms |
| API keys menu / landing “Developer API” | Toggle visibility with **`ENABLE_API_KEYS_MENU`** | Same + landing card overlay “Coming Soon” when off | Marketing matches product | Must keep `/meta` and UI in sync (recreate backend) |

---

## 5. User-supplied OpenAI keys (BYOK)

| Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|----------------|---------------------------|---------|--------------|
| SaaS vs BYOK | **Prefer SaaS** but allow **user keys** under flags | Fernet (or similar) storage, `ENABLE_USER_API_KEYS`, optional **`API_KEY_ALLOWED_EMAILS`** | Cost/control per cohort | Key rotation, support, and “who pays OpenAI” must be clear |
| Job failed with cryptic error when key required | Guide user, don’t opaque 500 | Validation + UX copy toward API key/settings | Better conversion and fewer support tickets | More branches in job create path |

---

## 6. Downloads and storage (MinIO / `localhost`)

| Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|----------------|---------------------------|---------|--------------|
| Download URLs pointed at **`localhost:9000`** in prod | Fix for real users | **Stream or sign through backend** (or correct public endpoint) | Works behind NAT/domain | More bandwidth/CPU on API |

---

## 7. Jobs: resume, stop, progress

| Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|----------------|---------------------------|---------|--------------|
| Failed jobs | **Resume from failed step** | Intermediate artifacts + resume step in pipeline | Less wasted GPU/time | State machine complexity; storage for intermediates |
| Long runs | **Stop/pause** then resume | Stop signal + Celery handling; status `stopped` | Operator control | Race: stop vs step completion—needed careful status updates |
| UI felt stale | Show progress | **WebSocket** URL from env or host; **activity log** on job page | Trust and debuggability | WS proxy must work in prod (same patterns as HTTP) |

---

## 8. Upload UX

| Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|----------------|---------------------------|---------|--------------|
| File lost on navigation | Retain selection | **sessionStorage** (or similar) + clear/remove | Smoother UX | Must **delete blob in storage** on remove—not only UI—to avoid orphan objects |

---

## 9. Video recap length, audio/video alignment (core pipeline)

Several iterations happened; below is the logical sequence.

### 9a. Target duration vs actual output (e.g. asked 30s, got ~15s + black)

| Issue | Direction | Implementation | Outcome | Side effects |
|--------|-----------|----------------|---------|--------------|
| Output shorter than target | **Pad or extend** narrative/video sensibly | Pipeline changes: narration timing + clip **overshoot + trim** (no black-frame pad) | No long black tail from padding video | Required tuning overshoot (+5s) and trim rules |

### 9b. Black screen while audio still playing

| Issue | Direction | Implementation | Outcome | Side effects |
|--------|-----------|----------------|---------|--------------|
| Video shorter than audio at end | **Clips longer than audio, trim video to audio** | `target_duration=actual_audio_duration + 5` for extract, trim down | Audio and picture end together | If audio extremely long vs clips, trim/cap logic must still apply |

### 9c. Long silent gaps (e.g. speech in the middle of a 60s recap)

| Issue | Your observation | First fix | Outcome | Side effects |
|--------|------------------|-----------|---------|--------------|
| Silence at start/end from **TTS padding** to hit target | “Audio starts at ~8s, ends ~40s on 60s” | **Pad silence only at end** (remove 30/70 front/back) | No huge **intro** dead air | **Long tail mute** if speech still short |
| Better alignment | Content-length, not silence | **Remove silence padding**; drive duration from real TTS; **scale narration word budget** with `target_duration`; **cap** clip trim and merge at `target_duration + overshoot` | Recap length respects user cap; less arbitrary mute; less **audio hard-cut** from merge | Final length may be **under** target if model still under-writes; aggressive **merge cap** can trim end of narration if TTS runs long |

**Net:** The stable design is: **(1)** don’t fake duration with silence, **(2)** ask the LLM for enough words for ~target spoken length, **(3)** cap montage and final mux to **user target + small grace** so one long TTS can’t blow past the requested recap (e.g. ~1:28 when 60s was asked).

---

## 10. Model / token limits (OpenAI)

| Issue | Direction | Implementation | Outcome | Side effects |
|--------|-----------|----------------|---------|--------------|
| `context_length_exceeded` on recap | Shorter prompts or bigger model | Model upgrade / chunking / retries (as implemented) | Fewer hard failures | Cost per job may rise |

---

## 11. Google authentication

| Issue | Your direction | Implementation direction | Outcome | Side effects |
|--------|----------------|---------------------------|---------|--------------|
| Social login | **Add Google**; you add OAuth client + origins | `@react-oauth/google`, `googleLogin` → existing **`POST /auth/google`**, **`google_client_id` on `/meta`**, provider in root layout | One-click sign-in when `GOOGLE_CLIENT_ID` set | **No button** if `/meta` fails or client id missing; Google Cloud console must list every origin (local + prod) |

---

## 12. Versioning and product polish

| Issue | Direction | Implementation | Outcome | Side effects |
|--------|-----------|----------------|---------|--------------|
| Know what’s deployed | **Auto version on push to main** | Version in settings + `window.__meta__` | Support/debug clarity | Build pipeline must pass `APP_VERSION` or similar |

---

## Summary table (high level)

| Theme | Primary lever | Main risk if misconfigured |
|--------|-------------|----------------------------|
| Multi-tenant VPS | Separate user + Traefik | Wrong route or user = outage or security blur |
| Next ↔ API | Env + middleware proxy | 404 on `/meta` / auth; Google button missing |
| Feature flags | Backend env + recreate | Stale behavior after `.env` edit |
| Recap A/V | Words ↔ duration + caps | Too short copy or trimmed end of VO |
| Jobs | Celery + storage + WS | Stuck UI, orphan files, stop races |

---

## How to use this doc

- **Onboarding:** Read sections 2, 3, and 9 before changing pipeline or frontend API base.
- **Ops:** Sections 1 and 3 before VPS or compose changes.
- **Product:** Sections 4–5 and 11 for flags and auth.

If you want this narrowed to **only production incidents** or **only pipeline AV**, say which sections to split into separate runbooks.
