# Video Recap Agent — Implementation Plan

## Overview

Convert the existing CLI-based Video Recap Agent into a production-grade Dockerized SaaS + API application. The existing `modules/` directory stays **unchanged** — we wrap it with adapters.

---

## Phase 1: Backend Foundation + Docker

### 1.1 Create Directory Structure

```bash
video_recap_agent/
├── backend/
│   ├── alembic/
│   │   ├── versions/           # Migration files
│   │   └── env.py              # Alembic environment
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Pydantic Settings
│   │   ├── api/v1/
│   │   │   ├── router.py       # Aggregates all routers
│   │   │   ├── deps.py         # Dependency injection (DB, auth)
│   │   │   └── endpoints/
│   │   │       ├── auth.py
│   │   │       ├── jobs.py
│   │   │       ├── uploads.py
│   │   │       ├── api_keys.py
│   │   │       ├── billing.py
│   │   │       ├── health.py
│   │   │       └── websocket.py
│   │   ├── core/
│   │   │   ├── security.py     # JWT, password hashing, API key gen
│   │   │   ├── oauth.py        # Google OAuth verification
│   │   │   ├── rate_limiter.py # Redis sliding window
│   │   │   └── permissions.py  # Quota checks per tier
│   │   ├── db/
│   │   │   ├── session.py      # AsyncEngine + sessionmaker
│   │   │   └── base.py         # DeclarativeBase + TimestampMixin
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── job.py
│   │   │   ├── api_key.py
│   │   │   ├── subscription.py
│   │   │   └── usage.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── job.py
│   │   │   ├── upload.py
│   │   │   ├── api_key.py
│   │   │   └── billing.py
│   │   ├── services/
│   │   │   ├── storage.py
│   │   │   ├── job_service.py
│   │   │   ├── user_service.py
│   │   │   ├── billing_service.py
│   │   │   └── notification.py
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   ├── tasks.py
│   │   │   └── pipeline.py
│   │   └── processing/
│   │       ├── __init__.py
│   │       ├── transcription.py
│   │       ├── video_processing.py
│   │       ├── audio_processing.py
│   │       └── progress.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   ├── test_workers/
│   │   └── test_processing/
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   ├── requirements.txt
│   └── requirements-dev.txt
```

### 1.2 Files to Create (in order)

1. **`backend/app/config.py`** — Pydantic Settings class loading all env vars:
   - DATABASE_URL, REDIS_URL, S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET
   - JWT_SECRET, JWT_ALGORITHM (HS256), JWT_ACCESS_TOKEN_EXPIRE_MINUTES
   - GOOGLE_CLIENT_ID, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
   - OPENAI_API_KEY, WHISPER_MODEL_SIZE
   - CORS_ORIGINS

2. **`backend/app/db/base.py`** — SQLAlchemy DeclarativeBase with TimestampMixin (created_at, updated_at auto columns)

3. **`backend/app/db/session.py`** — create_async_engine + async_sessionmaker using config.DATABASE_URL

4. **`backend/app/models/`** — All 5 models (user, job, api_key, subscription, usage) with relationships. See DB schema in plan.

5. **`backend/app/core/security.py`** — JWT encode/decode, password hash (bcrypt via passlib), API key generation (secrets.token_urlsafe), API key hashing (SHA-256)

6. **`backend/app/core/oauth.py`** — Verify Google OAuth ID token using google-auth library

7. **`backend/app/schemas/auth.py`** — Pydantic models: SignupRequest, LoginRequest, TokenResponse, UserResponse, GoogleAuthRequest

8. **`backend/app/services/user_service.py`** — create_user, authenticate_user, get_by_email, get_by_google_id, get_or_create_google_user

9. **`backend/app/api/v1/deps.py`** — get_db (async session), get_current_user (JWT decode), get_current_user_or_api_key (checks both)

10. **`backend/app/api/v1/endpoints/auth.py`** — signup, login, refresh, google, me endpoints

11. **`backend/app/api/v1/endpoints/health.py`** — Check DB, Redis, S3 connectivity

12. **`backend/app/api/v1/router.py`** — Include auth + health routers under /api/v1

13. **`backend/app/main.py`** — FastAPI app with CORS, lifespan (DB init), include v1 router

14. **`backend/alembic.ini`** + **`backend/alembic/env.py`** — Alembic config pointing to async DB, imports all models

15. **`backend/requirements.txt`** — All production deps

16. **`backend/Dockerfile`** — Multi-stage: python:3.11-slim + ffmpeg + deps + app

17. **`backend/Dockerfile.worker`** — Same base, CMD runs celery

18. **`docker-compose.yml`** — All services (postgres, redis, minio, minio-init, backend, worker, celery-beat, frontend)

### 1.3 Verification
- `docker compose up` starts all services
- `GET /api/v1/health` returns 200
- `POST /api/v1/auth/signup` + `POST /api/v1/auth/login` work

---

## Phase 2: Storage + Upload

### 2.1 Files to Create

1. **`backend/app/services/storage.py`** — S3StorageService class:
   - `__init__`: creates boto3 client with endpoint_url (MinIO dev, S3 prod)
   - `upload_file(key, file_obj)`: put_object
   - `download_file(key, dest_path)`: download_fileobj
   - `generate_presigned_url(key, expires=3600)`: generate_presigned_url
   - `delete_file(key)`: delete_object
   - `file_exists(key)`: head_object

2. **`backend/app/schemas/upload.py`** — UploadResponse (upload_id, s3_key, filename, size)

3. **`backend/app/api/v1/endpoints/uploads.py`** — POST /uploads/video:
   - Accept multipart file upload
   - Validate format (.mp4, .mov, .avi, .mkv, .webm) and size (< 2GB)
   - Generate S3 key: `uploads/{user_id}/{uuid}/{filename}`
   - Stream to S3 via storage service
   - Return upload_id (the UUID) and s3_key

4. **Update `router.py`** to include uploads router

### 2.2 Docker Updates
- minio-init service in docker-compose creates the `video-recaps` bucket on startup

### 2.3 Verification
- Upload a video via POST /uploads/video
- Confirm file visible in MinIO console at :9001

---

## Phase 3: Processing Pipeline Adapters

### 3.1 Files to Create

1. **`backend/app/processing/__init__.py`** — Adds `modules/` parent dir to sys.path so `import modules.X` works

2. **`backend/app/processing/transcription.py`** — Adapter:
   - `patched_module_paths(working_dir)` context manager patches SCRIPT_DIR + get_output_path on `modules.transcription`
   - `transcribe_video_service(video_path, working_dir, model_size, language, progress_cb)` — calls original
   - `translate_transcription_service(transcription_file, working_dir, source_lang, target_lang, progress_cb)` — calls original

3. **`backend/app/processing/video_processing.py`** — Adapter:
   - Same patching pattern for `modules.video_processing`
   - `generate_recap_service(transcription_file, working_dir, target_duration, progress_cb)`
   - `extract_clips_service(video_path, recap_data_file, working_dir, target_duration, progress_cb)`
   - `remove_audio_service(video_path, working_dir, progress_cb)`

4. **`backend/app/processing/audio_processing.py`** — Adapter:
   - Same patching pattern for `modules.audio_processing`
   - `generate_tts_service(recap_text_file, working_dir, tts_model, voice, progress_cb)`
   - `merge_audio_video_service(video_path, audio_path, working_dir, progress_cb)`

5. **`backend/app/processing/progress.py`** — ProgressReporter class:
   - Maps step number (1-7) to overall percentage range
   - Step weights: transcription=20%, translate=5%, recap=15%, extract=25%, remove_audio=5%, tts=15%, merge=15%
   - `report(step, sub_progress, message)` → computes overall_pct, calls notification service

6. **`backend/app/workers/pipeline.py`** — RecapPipeline class:
   - `run(job_id)`:
     1. Load job from DB
     2. Create temp working dir with output/ subdirs (output/transcriptions, output/videos, output/audio, output/original, output/temp)
     3. Download input video from S3 → temp dir
     4. For each of 7 steps:
        a. Call adapter function (patches paths → runs original module)
        b. Upload intermediate outputs to S3 under `jobs/{job_id}/`
        c. Update job status + progress in DB
        d. Publish progress event to Redis pub/sub
     5. Upload final video to S3 under `results/{job_id}/`
     6. Set job status = completed
     7. Clean up temp dir (in finally block)

### 3.2 Key Design Decisions
- Each Celery worker process gets its own temp dir → no path conflicts
- Monkeypatching is safe because Celery prefork pool = process isolation
- The context manager restores original values in `finally` for safety

### 3.3 Verification
- Write a test that calls pipeline directly, confirm output uploaded to S3

---

## Phase 4: Celery Tasks + Job Management

### 4.1 Files to Create

1. **`backend/app/workers/celery_app.py`** — Celery config:
   - Broker: redis://redis:6379/0
   - Backend: redis://redis:6379/1
   - Task serializer: json
   - Task routes: processing tasks → 'processing' queue
   - Task time limit: 30 minutes (soft), 35 minutes (hard)

2. **`backend/app/workers/tasks.py`** — Celery tasks:
   - `process_recap_job(job_id)`: Instantiates RecapPipeline, calls run(), handles exceptions (sets job=failed)
   - `cleanup_expired_files()`: Periodic task (celery-beat), finds jobs past expires_at, deletes S3 files, marks deleted

3. **`backend/app/services/job_service.py`** — JobService:
   - `create_job(user_id, upload_id, s3_key, config, filename, file_size)` → creates RecapJob, dispatches Celery task
   - `get_job(job_id, user_id)` → returns job if owned by user
   - `list_jobs(user_id, page, per_page, status_filter)` → paginated list
   - `update_job_progress(job_id, step, step_name, progress_pct, message)`
   - `complete_job(job_id, output_key)`
   - `fail_job(job_id, error_message)`
   - `delete_job(job_id, user_id)` → cancel Celery task + delete S3 files + soft delete

4. **`backend/app/schemas/job.py`** — Pydantic models:
   - CreateJobRequest (upload_id, config dict)
   - JobConfig (target_duration, whisper_model, tts_voice, tts_model, language, translate_to)
   - JobResponse (all fields from DB)
   - JobListResponse (items, total, page, per_page)
   - DownloadResponse (download_url, expires_in)

5. **`backend/app/api/v1/endpoints/jobs.py`** — Endpoints:
   - POST /jobs → create job, dispatch to Celery
   - GET /jobs → list with pagination + status filter
   - GET /jobs/{id} → single job detail
   - GET /jobs/{id}/download → presigned S3 URL for output
   - DELETE /jobs/{id} → cancel + cleanup

6. **Update `router.py`** to include jobs router

### 4.2 Docker Updates
- Ensure worker service and celery-beat are in docker-compose
- Worker: `celery -A app.workers.celery_app worker --loglevel=info --concurrency=2`
- Beat: `celery -A app.workers.celery_app beat --loglevel=info`

### 4.3 Verification
- POST /jobs → job created with status=pending
- Worker picks up task → status progresses through steps
- GET /jobs/{id} shows completed
- GET /jobs/{id}/download returns presigned URL

---

## Phase 5: Real-Time Progress

### 5.1 Files to Create

1. **`backend/app/services/notification.py`** — NotificationService:
   - Uses Redis pub/sub channel `job:{job_id}:progress`
   - `publish_progress(job_id, data)`: publishes JSON message to Redis channel
   - `ConnectionManager` class: manages active WebSocket connections per job_id
   - `subscribe(job_id)`: async generator that yields messages from Redis subscription

2. **`backend/app/api/v1/endpoints/websocket.py`**:
   - `WS /ws/jobs/{id}?token=` — WebSocket endpoint:
     - Authenticate via token query param
     - Verify user owns the job
     - Subscribe to Redis channel for this job
     - Forward messages to WebSocket client
     - Handle disconnect gracefully
   - `GET /jobs/{id}/events` — SSE fallback:
     - Same auth + subscription logic
     - Returns StreamingResponse with text/event-stream content type

3. **Update pipeline.py** — After each step, call `notification.publish_progress(job_id, {step, step_name, progress_pct, message})`

### 5.2 Message Format
```json
{
  "type": "progress",
  "step": 3,
  "step_name": "Generating recap suggestions",
  "progress_pct": 45.0,
  "message": "AI analyzing transcription..."
}
```
Final message:
```json
{
  "type": "completed",
  "step": 7,
  "progress_pct": 100.0,
  "output_video_key": "results/{job_id}/recap_video_with_narration.mp4"
}
```

### 5.3 Verification
- Connect WebSocket to job endpoint
- Submit a job
- Receive step-by-step progress messages in real-time

---

## Phase 6: API Keys + Rate Limiting

### 6.1 Files to Create

1. **`backend/app/schemas/api_key.py`** — CreateApiKeyRequest (name), ApiKeyResponse (id, name, prefix, last_used_at), ApiKeyCreatedResponse (includes full key, shown once)

2. **`backend/app/api/v1/endpoints/api_keys.py`**:
   - POST /api-keys → generate key (secrets.token_urlsafe(32)), hash it, store prefix ("vra_" + first 8 chars), return full key once
   - GET /api-keys → list user's keys (prefix only, not full key)
   - DELETE /api-keys/{id} → soft deactivate (is_active=false)

3. **Update `deps.py`** — `get_current_user_or_api_key`:
   - First check Authorization header for Bearer JWT
   - Then check X-API-Key header
   - If API key: hash it, lookup in DB, verify active, update last_used_at
   - Return user associated with the API key

4. **`backend/app/core/rate_limiter.py`** — Redis sliding window rate limiter:
   - `RateLimiter.check(user_id, tier)` → returns (allowed: bool, remaining: int, reset_at: datetime)
   - Tier limits: free=10 req/min, pro=60 req/min, enterprise=300 req/min
   - Uses Redis sorted sets with timestamps
   - Exposed as FastAPI dependency

5. **`backend/app/core/permissions.py`** — Quota enforcement:
   - `check_quota(user_id, tier)` → queries usage_records for current billing period
   - Tier quotas: free=3/month, pro=50/month, enterprise=unlimited
   - Raises HTTPException 429 if over quota

6. **Update job creation endpoint** to check quota before creating job

### 6.2 Verification
- Create API key, use X-API-Key header to list jobs
- Exceed rate limit, get 429 response

---

## Phase 7: Next.js Frontend

### 7.1 Project Setup

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir
cd frontend
npx shadcn@latest init
npx shadcn@latest add button card input label dialog dropdown-menu separator badge progress tabs avatar
npm install axios js-cookie sonner lucide-react recharts
```

### 7.2 Files to Create

**Core Infrastructure:**
1. **`src/lib/types.ts`** — TypeScript interfaces matching all backend schemas (User, Job, JobConfig, ApiKey, Subscription, UsageSummary, etc.)
2. **`src/lib/api.ts`** — Axios instance with base URL, auth interceptor (attaches JWT), 401 interceptor (redirects to login)
3. **`src/lib/auth.ts`** — AuthContext + AuthProvider: stores tokens in localStorage, provides login/logout/signup functions, auto-refresh
4. **`src/lib/websocket.ts`** — WebSocket manager: auto-reconnect with exponential backoff, message typing
5. **`src/lib/utils.ts`** — Formatting: file sizes, dates, durations, status badges

**Hooks:**
6. **`src/hooks/useAuth.ts`** — Wraps AuthContext
7. **`src/hooks/useJobs.ts`** — CRUD operations for jobs (list, get, delete)
8. **`src/hooks/useJobProgress.ts`** — WebSocket subscription for live job progress
9. **`src/hooks/useUpload.ts`** — File upload with progress tracking (XMLHttpRequest for progress events)
10. **`src/hooks/useApiKeys.ts`** — CRUD for API keys

**Layout Components:**
11. **`src/components/layout/Header.tsx`** — App header with user menu, logout
12. **`src/components/layout/Sidebar.tsx`** — Dashboard sidebar nav (Dashboard, Upload, Jobs, API Keys, Billing, Settings)
13. **`src/components/layout/Footer.tsx`** — Simple footer

**Auth Components:**
14. **`src/components/auth/LoginForm.tsx`** — Email/password + Google OAuth button
15. **`src/components/auth/SignupForm.tsx`** — Full name, email, password, confirm
16. **`src/components/auth/GoogleOAuthButton.tsx`** — Google sign-in button (uses @react-oauth/google)

**Job Components:**
17. **`src/components/jobs/JobCard.tsx`** — Card showing job status, filename, dates, progress
18. **`src/components/jobs/JobList.tsx`** — List of JobCards with filters (status, date)
19. **`src/components/jobs/JobProgress.tsx`** — Real-time progress bar with step names
20. **`src/components/jobs/VideoPreview.tsx`** — Video player for completed recaps

**Upload Components:**
21. **`src/components/upload/DropZone.tsx`** — Drag-and-drop area with file type validation
22. **`src/components/upload/UploadForm.tsx`** — Config form: target duration, voice, model, language
23. **`src/components/upload/UploadProgress.tsx`** — Upload progress bar

**Billing Components:**
24. **`src/components/billing/UsageChart.tsx`** — Bar chart of monthly usage (recharts)
25. **`src/components/billing/PricingTable.tsx`** — Three-tier pricing cards

**API Key Components:**
26. **`src/components/api-keys/ApiKeyList.tsx`** — Table of keys with revoke buttons
27. **`src/components/api-keys/CreateKeyDialog.tsx`** — Dialog to create + show key once

**Pages:**
28. **`src/app/layout.tsx`** — Root layout: AuthProvider, Toaster
29. **`src/app/page.tsx`** — Landing page: hero section, features grid, pricing, CTA
30. **`src/app/(auth)/login/page.tsx`** — Login page
31. **`src/app/(auth)/signup/page.tsx`** — Signup page
32. **`src/app/(dashboard)/layout.tsx`** — Dashboard layout with sidebar
33. **`src/app/(dashboard)/dashboard/page.tsx`** — Overview: stats cards (total jobs, this month, storage), recent jobs
34. **`src/app/(dashboard)/upload/page.tsx`** — Upload flow: dropzone → config → submit
35. **`src/app/(dashboard)/jobs/page.tsx`** — Jobs list with pagination + filters
36. **`src/app/(dashboard)/jobs/[id]/page.tsx`** — Job detail: live progress or completed result
37. **`src/app/(dashboard)/api-keys/page.tsx`** — API key management
38. **`src/app/(dashboard)/billing/page.tsx`** — Usage + subscription + upgrade
39. **`src/app/(dashboard)/settings/page.tsx`** — User profile settings
40. **`src/middleware.ts`** — Route protection: redirect to /login if no token for /dashboard/* routes

**Frontend Docker:**
41. **`frontend/Dockerfile`** — Multi-stage Next.js build (node:20-alpine → deps → build → runner)

### 7.3 Verification
- Sign up → redirected to dashboard
- Upload video → see upload progress → job created
- Watch live progress via WebSocket
- Download completed recap
- Manage API keys

---

## Phase 8: Billing with Stripe

### 8.1 Files to Create

1. **`backend/app/services/billing_service.py`** — BillingService:
   - `get_or_create_stripe_customer(user)`: creates Stripe customer if none
   - `create_checkout_session(user, tier)`: Stripe Checkout for subscription
   - `handle_webhook(payload, sig)`: processes Stripe events:
     - `checkout.session.completed` → create/update subscription, update user tier
     - `customer.subscription.updated` → update subscription status
     - `customer.subscription.deleted` → downgrade to free
     - `invoice.payment_failed` → mark subscription past_due
   - `get_usage_summary(user_id)`: query usage_records for current period
   - `record_usage(user_id, job_id)`: create usage_record
   - `check_quota(user_id)`: compare usage vs tier limit

2. **`backend/app/schemas/billing.py`** — TierInfo, UsageSummary, SubscriptionResponse, CheckoutRequest, CheckoutResponse

3. **`backend/app/api/v1/endpoints/billing.py`**:
   - GET /billing/tiers → static tier info
   - GET /billing/usage → current usage vs quota
   - GET /billing/subscription → active subscription details
   - POST /billing/checkout → create Stripe checkout session, return URL
   - POST /billing/webhook → Stripe webhook handler (verify signature)

4. **Update job creation** to call `billing_service.record_usage()` and `billing_service.check_quota()`

5. **Frontend billing page** — usage chart, current plan card, upgrade buttons that redirect to Stripe Checkout

### 8.2 Stripe Setup (manual)
- Create Stripe products: Free, Pro ($19/mo), Enterprise ($99/mo)
- Configure webhook endpoint: `https://yourdomain.com/api/v1/billing/webhook`
- Events to listen: checkout.session.completed, customer.subscription.*, invoice.payment_failed

### 8.3 Verification
- Free tier user hits quota after 3 jobs → 429
- Click "Upgrade to Pro" → Stripe Checkout → subscription active → quota increased

---

## Phase 9: Testing + Polish

### 9.1 Test Files

1. **`backend/tests/conftest.py`**:
   - Test database (SQLite async or test PostgreSQL)
   - Override get_db dependency
   - Test client (httpx AsyncClient)
   - Mock S3 (moto or mock boto3)
   - Mock OpenAI API calls
   - Factory fixtures: create_test_user, create_test_job

2. **`backend/tests/test_api/test_auth.py`** — Test signup, login, refresh, invalid credentials, duplicate email
3. **`backend/tests/test_api/test_jobs.py`** — Test create job, list, get, download, delete, unauthorized access
4. **`backend/tests/test_api/test_uploads.py`** — Test upload, invalid format, size limit
5. **`backend/tests/test_api/test_api_keys.py`** — Test create, list, revoke, use for auth
6. **`backend/tests/test_api/test_health.py`** — Test health endpoint
7. **`backend/tests/test_services/test_user_service.py`** — User CRUD tests
8. **`backend/tests/test_services/test_job_service.py`** — Job lifecycle tests
9. **`backend/tests/test_services/test_storage.py`** — S3 operations (mocked)
10. **`backend/tests/test_workers/test_pipeline.py`** — Pipeline orchestration (mocked modules)
11. **`backend/tests/test_processing/test_adapters.py`** — Verify patching/unpatching

### 9.2 Polish Files

1. **`backend/requirements-dev.txt`** — pytest, pytest-asyncio, pytest-cov, httpx, moto, factory-boy

2. **`docker-compose.prod.yml`** — Production overrides:
   - Resource limits (worker: 4GB RAM, 2 CPU)
   - Backend replicas: 2
   - No volume mounts
   - Production env vars
   - Health checks on all services

3. **`docker-compose.dev.yml`** — Dev overrides:
   - Volume mounts for hot-reload
   - `--reload` flag on uvicorn
   - `watchmedo auto-restart` on worker
   - Frontend: `npm run dev`

4. **`.env.example`** — All env vars documented with comments

5. **`Makefile`** — Shortcuts:
   - `make up` / `make down` / `make restart`
   - `make dev` (dev overrides)
   - `make migrate` / `make migration`
   - `make test` / `make test-cov`
   - `make logs` / `make shell`

### 9.3 Verification
- `pytest tests/ -v --cov=app` passes with >80% coverage
- `docker compose -f docker-compose.yml -f docker-compose.prod.yml up` starts cleanly
- Full end-to-end flow works

---

## Dependency Order

```
Phase 1 (Foundation)
  └── Phase 2 (Storage)
       └── Phase 3 (Pipeline Adapters)
            └── Phase 4 (Celery + Jobs)
                 ├── Phase 5 (Real-time Progress)
                 └── Phase 6 (API Keys + Rate Limiting)
                      └── Phase 7 (Frontend)
                           └── Phase 8 (Billing)
                                └── Phase 9 (Testing + Polish)
```

---

## Key Technical Decisions

1. **Async everywhere**: FastAPI + SQLAlchemy 2.0 async + async Redis
2. **Celery prefork pool**: Process isolation makes monkeypatching safe
3. **S3 abstraction**: MinIO in dev, AWS S3 in prod — same boto3 interface
4. **JWT + API keys**: JWT for web sessions, API keys for developer API access
5. **Redis triple duty**: Celery broker, rate limiter store, pub/sub for WebSocket
6. **Temp dirs per job**: Each pipeline run gets isolated temp directory, cleaned up after

---

## Estimated File Count

| Phase | New Files | Modified Files |
|-------|-----------|---------------|
| 1 | ~20 | 0 |
| 2 | ~4 | 1 (router.py) |
| 3 | ~6 | 0 |
| 4 | ~5 | 1 (router.py) |
| 5 | ~2 | 1 (pipeline.py) |
| 6 | ~4 | 2 (deps.py, jobs.py) |
| 7 | ~42 | 0 |
| 8 | ~4 | 2 (jobs.py, router.py) |
| 9 | ~15 | 0 |
| **Total** | **~102** | **~7** |
