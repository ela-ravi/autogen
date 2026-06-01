# Test Emotion Analysis - Graceful Failure Handling

After rebuilding Docker, follow these steps to test the emotion analysis feature with graceful failure handling.

## Prerequisites
- Docker stack running: `docker-compose up -d`
- Migrations applied: `docker-compose exec backend alembic upgrade head`
- Frontend ready: http://localhost:3000
- Google Cloud credentials set (if testing success scenario): `echo $GOOGLE_APPLICATION_CREDENTIALS`

---

## Test 1: Emotion Analysis SUCCESS ✅

### Setup
```bash
# Verify Google Cloud credentials are set
echo $GOOGLE_APPLICATION_CREDENTIALS
# Should show path to JSON key file

# Verify google-cloud-speech is installed
docker-compose exec worker pip list | grep google-cloud-speech
# Should show: google-cloud-speech    2.29.0
```

### Test Steps
1. Open http://localhost:3000 and sign in
2. Go to Dashboard → Upload Video
3. Select a test video (e.g., test-video/vidssave.com*.mp4)
4. **Enable** "✨ Include Emotion Analysis (Premium)" ← KEY STEP
5. Click "Start Processing"
6. **Watch Progress:**
   - Should see "[PREMIUM (with emotion analysis)]" in status
   - Should see "Analyzing emotions in progress..." message
7. **When Completed:**
   - Status container shows: `✓ Emotion analysis completed (PREMIUM)`
   - Sub-text: "Speaker emotions detected and used for intelligent clip weighting"
   - Color: **Purple/indigo** (premium)
8. **Modal Appears:** "Keep original video?"
   - Click "Keep Original" → Toast: "Original video will be kept"
   - OR click "Delete Original" → Toast: "Original video deleted"

### Verify in Logs
```bash
# Check backend logs for success
docker-compose logs -f backend | grep -i "emotion\|completed"
# Should see: "✅ Emotion analysis completed"

# Check worker logs
docker-compose logs -f worker | grep -i "emotion"
# Should see emotion analysis progress messages
```

---

## Test 2: Emotion Analysis FAILURE (Graceful) ❌

### Setup - Simulate Credentials Missing
```bash
# Stop Docker containers
docker-compose down

# Unset credentials in current terminal
unset GOOGLE_APPLICATION_CREDENTIALS

# Restart WITHOUT credentials
docker-compose up -d

# Verify it's not set in worker
docker-compose exec worker bash -c 'echo $GOOGLE_APPLICATION_CREDENTIALS'
# Should be empty
```

### Test Steps
1. Sign in at http://localhost:3000
2. Upload a video
3. **Enable** "✨ Include Emotion Analysis (Premium)"
4. Click "Start Processing"
5. **Watch Progress:**
   - Should see "[PREMIUM (with emotion analysis)]" in status
   - Should see "Analyzing emotions in progress..."
   - **Job should CONTINUE** and complete successfully ← Key difference
6. **When Completed:**
   - Job status: `completed` ✅ (not failed)
   - Status container shows: `❌ Emotion analysis failed`
   - Sub-text: "Google Cloud Speech API error. Check system logs..."
   - Color: **Red** (error)
   - **Recap still available to download!**
7. **Modal Appears:** "Keep original video?" (same as before)

### Verify in Logs
```bash
# Check worker logs for specific error
docker-compose logs -f worker | grep -i "emotion\|failed"
# Should see warning like: "❌ Emotion analysis failed"

# Check for actual API error details
docker-compose logs -f worker | grep -A5 "Emotion analysis failed"
# Might show: "DefaultCredentialsError" or similar
```

---

## Test 3: Video Deletion Confirmation 🗑️

### Test Keep vs Delete
After completing a job (success or graceful failure):

1. **Scenario A: Keep Original**
   - Modal: "Keep original video?"
   - Click: "Keep Original"
   - Toast: "Original video will be kept in your account"
   - Database updated: `keep_original_video = true`

2. **Scenario B: Delete Original**
   - Modal: "Keep original video?"
   - Click: "Delete Original"
   - Toast: "Original video has been deleted"
   - Original removed from S3 immediately
   - Database updated: `keep_original_video = false`

3. **Next Upload (after keeping):**
   - Should show option like "Previously uploaded - reuse?" ← Future feature
   - User can reuse without re-uploading

---

## Expected Behavior Summary

| Scenario | Emotion Enabled | API Status | Job Status | UI Shows | Can Download |
|----------|---|---|---|---|---|
| **Test 1** | ✓ Yes | ✅ Works | Completed | ✓ Success (Purple) | ✅ Yes |
| **Test 2** | ✓ Yes | ❌ Fails | Completed | ❌ Failed (Red) | ✅ Yes |
| **Test 3** | ✗ No | N/A | Completed | ⊘ Skipped (Gray) | ✅ Yes |

---

## Troubleshooting

### Docker build errors
```bash
docker-compose build --no-cache worker backend
```

### Database migration errors
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic history
```

### Emotion analysis not showing
- Check if `keep_original_video` field exists: `docker-compose exec backend alembic current`
- Check if `emotion_analysis_status` field exists in DB
- Check worker logs: `docker-compose logs -f worker`

### Google Cloud errors
```bash
# Test credentials
docker-compose exec worker bash -c 'python -c "from google.cloud import speech; print(\"OK\")"'

# Verify credentials file
docker-compose exec worker bash -c 'cat $GOOGLE_APPLICATION_CREDENTIALS | head -5'
```

---

## Success Criteria ✅

- [ ] Test 1: Emotion analysis succeeds with purple container + success message
- [ ] Test 2: Emotion analysis fails gracefully - job still completes, red container shows error
- [ ] Test 3: Confirmation modal appears for both scenarios
- [ ] Both "Keep" and "Delete" buttons work correctly
- [ ] Error messages are clear and actionable
- [ ] Recap video still available for download in both success and failure cases
