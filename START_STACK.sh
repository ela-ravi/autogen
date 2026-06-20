#!/bin/bash

###############################################################################
#
# 🚀 START_STACK.sh - Start all services for Video Recap with Emotions
#
# This script helps you start the full application stack:
# - Docker services (PostgreSQL, Redis, Nginx) - already running
# - Backend (FastAPI)
# - Celery Worker (async job processing)
# - Frontend (Next.js)
#
# Usage: Open 3 terminals and run commands from each section
#
###############################################################################

PROJECT_DIR="/Volumes/Development/hallucinotai/videorecap"

echo "=================================================="
echo "🎬 Video Recap Stack Startup Helper"
echo "=================================================="
echo ""
echo "This guide will help you start all required services."
echo "Open 3 terminals and follow the sections below."
echo ""

# =============================================================================
# SECTION 1: DOCKER COMPOSE (PostgreSQL, Redis, Nginx)
# =============================================================================
cat << 'EOF'
════════════════════════════════════════════════════════════════════════════════
📦 SECTION 1: Docker Services (PostgreSQL, Redis, Nginx)
════════════════════════════════════════════════════════════════════════════════

Status: Already starting in background (or run manually if needed)

Manual start (if needed):
    cd /Volumes/Development/hallucinotai/videorecap
    docker-compose up -d

Verify services:
    docker-compose ps
    docker-compose logs -f postgres  # watch PostgreSQL startup
    docker-compose logs -f redis     # watch Redis startup

Expected output:
    ✓ postgres is up
    ✓ redis is up
    ✓ nginx is up

════════════════════════════════════════════════════════════════════════════════
EOF

echo ""
cat << 'EOF'
════════════════════════════════════════════════════════════════════════════════
🔧 SECTION 2: Backend (FastAPI)
════════════════════════════════════════════════════════════════════════════════

Copy and paste in TERMINAL 1:

    cd /Volumes/Development/hallucinotai/videorecap
    source .venv/bin/activate
    cd backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Expected output:
    INFO:     Will watch for changes in these directories: ['/Volumes/...']
    INFO:     Uvicorn running on http://0.0.0.0:8000
    INFO:     Application startup complete

Test it works:
    curl http://localhost:8000/api/v1/health
    # Should return: {"status": "ok"}

════════════════════════════════════════════════════════════════════════════════
EOF

echo ""
cat << 'EOF'
════════════════════════════════════════════════════════════════════════════════
⚙️  SECTION 3: Celery Worker (Async Job Processing)
════════════════════════════════════════════════════════════════════════════════

Copy and paste in TERMINAL 2:

    cd /Volumes/Development/hallucinotai/videorecap
    source .venv/bin/activate
    celery -A app.workers.tasks worker --loglevel=info --concurrency=2

Expected output:
    Connected to redis://localhost:6379//
    celery@YOUR-HOSTNAME ready to accept tasks.

This worker will:
    ✓ Process video transcription jobs
    ✓ Analyze audio emotions (if include_emotions=True)
    ✓ Generate recap suggestions
    ✓ Create video clips
    ✓ Generate TTS narration
    ✓ Merge audio and video

════════════════════════════════════════════════════════════════════════════════
EOF

echo ""
cat << 'EOF'
════════════════════════════════════════════════════════════════════════════════
🎨 SECTION 4: Frontend (Next.js)
════════════════════════════════════════════════════════════════════════════════

Copy and paste in TERMINAL 3:

    cd /Volumes/Development/hallucinotai/videorecap/frontend
    npm run dev

Expected output:
    ▲ Next.js 14.2.0
    ✓ Ready in 2.5s
    ✓ Listening on 0.0.0.0:3000

Open in browser:
    http://localhost:3000

════════════════════════════════════════════════════════════════════════════════
EOF

echo ""
cat << 'EOF'
════════════════════════════════════════════════════════════════════════════════
🧪 TESTING IN UI
════════════════════════════════════════════════════════════════════════════════

Once all services are running:

1. Open http://localhost:3000 in browser

2. Sign up with email/password or Google OAuth

3. Navigate to Dashboard → Upload Video

4. Select test video:
   test-video/vidssave.com One-Minute Time Machine...mp4

5. Click "Create Job" and configure:
   ✓ Target duration: 30s
   ✓ Model: small
   ✓ Include emotions: ON (or OFF to compare)
   ✓ Click "Create Job"

6. Watch progress in UI:
   [Step 1] Transcribing [PREMIUM (with emotion analysis)]...
   [Step 2] Translation (skipped)
   [Step 3] Generating recap (with emotion weighting)...
   [Step 4] Generating TTS narration...
   [Step 5] Extracting clips...
   [Step 6] Merging audio...

7. Once complete → Download final video!

8. Create another job with include_emotions=OFF to compare

════════════════════════════════════════════════════════════════════════════════
EOF

echo ""
cat << 'EOF'
════════════════════════════════════════════════════════════════════════════════
🔍 TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════════

If backend fails to start:
    • Check PostgreSQL is running: docker-compose ps | grep postgres
    • Check .env has OPENAI_API_KEY: cat .env | grep OPENAI
    • Reinstall dependencies: pip install -r backend/requirements.txt

If Celery fails to start:
    • Check Redis is running: docker-compose ps | grep redis
    • Check Redis connection: redis-cli ping
    • Check logs: docker-compose logs redis

If emotion analysis fails:
    • Check Google Cloud setup: echo $GOOGLE_APPLICATION_CREDENTIALS
    • If not set, run: onetime-setup/SETUP_COMMANDS.sh
    • Or manually: export GOOGLE_APPLICATION_CREDENTIALS=~/videorecap-key.json

If job gets stuck:
    • Check Celery logs: Look at TERMINAL 2
    • Restart worker: Ctrl+C in TERMINAL 2, then restart
    • Check Redis: redis-cli KEYS "*"

════════════════════════════════════════════════════════════════════════════════
EOF

echo ""
echo "✨ Ready to start? Follow the 4 sections above!"
echo ""
