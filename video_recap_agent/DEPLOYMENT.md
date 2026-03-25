# Deploying Video Recap Agent to Hostinger KVM2 VPS

This guide covers deploying alongside an existing OpenClaw installation on Ubuntu.

## Prerequisites

- Ubuntu VPS with Docker and Docker Compose V2 installed
- SSH access to the VPS
- GitHub repository with this code pushed

## Step 1: Check VPS Resources

SSH into your VPS and verify you have enough resources:

```bash
free -h          # Need at least 4GB free RAM
df -h            # Need at least 15-20GB free disk
docker --version # Docker 24+ recommended
docker compose version  # V2 required
```

## Step 2: Create Deploy User

```bash
sudo adduser videorecap
sudo usermod -aG docker videorecap
```

## Step 3: Set Up SSH Key for GitHub Actions

```bash
# On your local machine, generate a deploy key:
ssh-keygen -t ed25519 -C "videorecap-deploy" -f ~/.ssh/videorecap_deploy

# Copy the PUBLIC key to the VPS:
ssh-copy-id -i ~/.ssh/videorecap_deploy.pub videorecap@YOUR_VPS_IP

# Test the connection:
ssh -i ~/.ssh/videorecap_deploy videorecap@YOUR_VPS_IP

# Add the PRIVATE key as a GitHub Secret:
# Go to: GitHub repo > Settings > Secrets and variables > Actions > New repository secret
# Name: VPS_SSH_KEY
# Value: paste contents of ~/.ssh/videorecap_deploy
```

Add these GitHub Secrets:
| Secret | Value |
|--------|-------|
| `VPS_HOST` | Your VPS IP address |
| `VPS_USER` | `videorecap` |
| `VPS_SSH_KEY` | Contents of the private key file |
| `VPS_PORT` | `22` (or your SSH port) |

## Step 4: Clone the Repository on VPS

```bash
sudo -u videorecap -i
git clone https://github.com/YOUR_USER/YOUR_REPO.git ~/video-recap-agent
cd ~/video-recap-agent/video_recap_agent
```

## Step 5: Create Production Environment File

```bash
cp .env.production.example .env
nano .env
```

Fill in all values marked with `CHANGE_ME`:
- Generate JWT secret: `python3 -c "import secrets; print(secrets.token_urlsafe(64))"`
- Set strong MinIO and Postgres passwords
- Add your OpenAI API key
- Set `S3_PUBLIC_ENDPOINT` to `http://YOUR_VPS_IP/storage`
- Set `CORS_ORIGINS` to `["http://YOUR_VPS_IP"]`

## Step 6: Install and Configure Nginx

```bash
sudo apt update && sudo apt install -y nginx

# Copy the config
sudo cp ~/video-recap-agent/video_recap_agent/nginx/videorecap.conf \
     /etc/nginx/sites-available/videorecap

# Enable it
sudo ln -sf /etc/nginx/sites-available/videorecap \
     /etc/nginx/sites-enabled/videorecap

# Remove default site if not needed by OpenClaw
# sudo rm /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

If OpenClaw already uses Nginx on port 80, edit the `server_name` in
`videorecap.conf` to use a subdomain (e.g., `recap.yourdomain.com`)
so both can coexist on port 80.

## Step 7: First Deploy

```bash
cd ~/video-recap-agent/video_recap_agent

# Build and start all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to be healthy
docker compose ps

# Run initial database migrations
docker compose exec -T backend alembic upgrade head
```

## Step 8: Verify

- Frontend: `http://YOUR_VPS_IP` (through Nginx)
- API Health: `curl http://YOUR_VPS_IP/api/v1/health`
- MinIO Console: `http://YOUR_VPS_IP:9101` (only from localhost, use SSH tunnel)

## Step 9 (Optional): Domain + SSL

```bash
# Point your domain DNS A record to your VPS IP, then:
sudo apt install -y certbot python3-certbot-nginx

# Edit videorecap.conf: change server_name _ to your domain
sudo nano /etc/nginx/sites-available/videorecap
# Change: server_name _; -> server_name recap.yourdomain.com;

# Get SSL certificate
sudo certbot --nginx -d recap.yourdomain.com

# Update .env with HTTPS URLs
# CORS_ORIGINS=["https://recap.yourdomain.com"]
# S3_PUBLIC_ENDPOINT=https://recap.yourdomain.com/storage

# Rebuild frontend with new URLs and restart
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build frontend
```

## CI/CD: Automatic Deployments

After the initial setup, every push to `main` that changes files in
`video_recap_agent/` will automatically trigger the GitHub Actions
workflow (`.github/workflows/deploy.yml`) which:

1. SSHs into your VPS
2. Pulls the latest code
3. Rebuilds and restarts containers
4. Runs database migrations
5. Cleans up old Docker images

You can also trigger a deploy manually from the GitHub Actions tab
(workflow_dispatch).

## Monitoring

```bash
# View all service logs
docker compose logs -f

# View specific service
docker compose logs -f backend
docker compose logs -f worker

# Check resource usage
docker stats

# Restart a service
docker compose restart backend
```

## Troubleshooting

**Worker killed (OOM):** Reduce `WHISPER_MODEL_SIZE` to `tiny` in `.env`
and restart the worker.

**Disk full:** Run `docker system prune -a --volumes` to reclaim space.
The cleanup task runs every 6 hours to delete expired job files.

**502 Bad Gateway:** Check if containers are running with `docker compose ps`.
If not, check logs with `docker compose logs`.
