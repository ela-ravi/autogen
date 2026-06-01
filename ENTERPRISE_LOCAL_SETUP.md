# Enterprise Access - Local Development Setup

This guide shows you how to upgrade to Enterprise tier locally for testing longer video durations (> 120s).

## Quick Start

### 1. Start the Backend

Make sure your backend is running:

```bash
cd /Volumes/Development/hallucinotai/videorecap
docker-compose up -d backend
# or locally:
python -m uvicorn app.main:app --reload
```

### 2. Get Your JWT Token

First, sign up or log in to get a JWT token:

```bash
# Sign up
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@example.com",
    "password": "testpassword123",
    "full_name": "Dev User"
  }'

# Or login if you already have an account
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@example.com",
    "password": "testpassword123"
  }'
```

Response will include:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {...}
}
```

**Save the `access_token` value** - you'll need it for the next step.

### 3. Upgrade to Enterprise

Use the new dev endpoint to upgrade your tier:

```bash
curl -X POST http://localhost:8000/api/v1/users/upgrade-to-enterprise \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

Replace `YOUR_ACCESS_TOKEN_HERE` with the token from step 2.

**Response:**
```json
{
  "message": "Successfully upgraded to enterprise tier",
  "user_id": "uuid-here",
  "email": "dev@example.com",
  "tier": "enterprise",
  "note": "This is a development-only endpoint. Use /api/v1/billing for production upgrades."
}
```

### 4. Verify Your Tier

Check that you're now on enterprise:

```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

Response should show `"tier": "enterprise"`

### 5. Submit a Job with 180+ Seconds

Now you can submit a job with any duration:

```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "test-upload-123",
    "s3_key": "test/video.mp4",
    "original_filename": "video.mp4",
    "file_size_bytes": 50000000,
    "config": {
      "target_duration": 180
    }
  }'
```

The request will succeed! ✅

---

## Alternative: Set Tier Manually

Instead of upgrading to enterprise, you can set any tier:

```bash
# Set to pro (120s limit)
curl -X POST http://localhost:8000/api/v1/users/set-tier/pro \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# Set to enterprise (unlimited)
curl -X POST http://localhost:8000/api/v1/users/set-tier/enterprise \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# Set back to free (30s limit)
curl -X POST http://localhost:8000/api/v1/users/set-tier/free \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Using with Frontend

If you're testing via the web frontend, you need to:

1. Log in with your dev account
2. Open browser DevTools (F12)
3. Go to Application → Local Storage → Find your JWT token
4. Copy the token and use it with the curl commands above
5. Or, add this to your frontend's login handler to auto-upgrade:

```javascript
// After successful login
const response = await fetch('http://localhost:8000/api/v1/users/upgrade-to-enterprise', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const data = await response.json();
console.log('Upgraded to enterprise:', data.tier);
```

---

## Check Available Tiers

See what tiers are available and their limits:

```bash
curl http://localhost:8000/api/v1/users/tiers
```

**Response:**
```json
[
  {
    "name": "free",
    "price": 0,
    "max_duration": 30,
    "max_jobs_per_month": 3,
    "features": ["Basic voices", "30s max duration", "7-day file retention"]
  },
  {
    "name": "pro",
    "price": 19,
    "max_duration": 120,
    "max_jobs_per_month": 50,
    "features": ["All voices", "HD TTS", "120s max", "30-day retention", "Translation"]
  },
  {
    "name": "enterprise",
    "price": 99,
    "max_duration": 3600,
    "max_jobs_per_month": -1,
    "features": ["Unlimited duration", "Priority queue", "Custom branding", "90-day retention", "Dedicated support"]
  }
]
```

---

## Troubleshooting

### "Invalid token" error
- Make sure you're using the `access_token` from login, not the user ID
- Check that your token hasn't expired
- Sign in again to get a fresh token

### "User not found" error
- Sign up/login first before using dev endpoints
- Make sure you're using the correct JWT token for your user

### 401 Unauthorized
- Missing `Authorization: Bearer` header
- Token is invalid or expired
- Use the exact format: `Authorization: Bearer YOUR_TOKEN_HERE`

### Job still rejects 180s duration
- Verify tier upgrade succeeded (check `/users/me`)
- Make sure backend is restarted after tier change
- Clear browser cache to reload any cached validation rules

---

## How It Works

The new endpoints work by:

1. **`/users/me`** - View your current tier and user info
2. **`/users/upgrade-to-enterprise`** - Set your tier to "enterprise" (unlimited duration)
3. **`/users/set-tier/{tier}`** - Set tier to any value (free, pro, enterprise)
4. **`/users/tiers`** - See available tiers and their limits

The tier is stored in the database and checked when you submit a job.

---

## Production Notes

⚠️ **These endpoints are FOR LOCAL DEVELOPMENT ONLY**

In production:
- Remove these endpoints or guard them with admin-only access
- Use the Stripe billing endpoint (`/billing/checkout`) for real upgrades
- Don't let users directly set their own tier

The endpoints log warnings when used:
```
WARNING User abc123 (dev@example.com) upgraded to enterprise tier via dev endpoint
```

---

## Clean Up

When you're done testing, you can:

1. **Reset to free tier:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/users/set-tier/free \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Delete your test user** (via database if needed):
   ```bash
   psql -U postgres -d videorecap -c "DELETE FROM users WHERE email = 'dev@example.com';"
   ```

3. **Stop the backend:**
   ```bash
   docker-compose down
   ```

---

## Next Steps

Now that you have enterprise access:

1. ✅ Test 180s+ duration recaps
2. ✅ Test all enterprise features
3. ✅ Test longer narration generation
4. ✅ Test clip selection with more content

Enjoy testing! 🚀
