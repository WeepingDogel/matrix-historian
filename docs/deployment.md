# Matrix Historian - Deployment Guide

## Deployment Options

Matrix Historian supports multiple deployment methods to suit different needs:

1. **Docker Compose** (Recommended for most users)
2. **Manual Installation** (For development or custom setups)
3. **Kubernetes** (For production scaling)
4. **Cloud Platforms** (AWS, GCP, Azure)

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 2GB | 8GB+ |
| Storage | 10GB | 50GB+ (depends on archive size) |
| OS | Linux, macOS, Windows (WSL2) | Linux |

### Required Software

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Git** for cloning the repository
- **curl** or similar HTTP client for testing

## 1. Docker Compose Deployment (Recommended)

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/WeepingDogel/matrix-historian.git
cd matrix-historian

# Copy environment configuration
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

### Step 2: Configure Environment Variables

Edit `.env` with your Matrix credentials:

```env
# ===== Matrix Configuration =====
MATRIX_HOMESERVER=https://matrix.org
MATRIX_USER_ID=@your_bot:matrix.org
MATRIX_ACCESS_TOKEN=syt_youraccesstoken
MATRIX_ROOMS=!room1:matrix.org,!room2:matrix.org

# ===== Database Configuration =====
POSTGRES_DB=matrix_historian
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_this_secure_password

# ===== MinIO Configuration =====
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=change_this_too
MINIO_BUCKET_NAME=matrix-media

# ===== API Configuration =====
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=generate_a_secure_secret_key_here

# ===== Optional: AI Features =====
# GROQ_API_KEY=your_groq_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
```

### Step 3: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 4: Verify Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Check database connection
docker-compose exec db psql -U postgres -d matrix_historian -c "SELECT version();"

# Check MinIO
curl http://localhost:9001/minio/health/live
```

### Step 5: Access Services

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| API & Docs | http://localhost:8000/docs | None (public) |
| MinIO Console | http://localhost:9001 | minioadmin / password_from_env |
| PostgreSQL | localhost:5432 | postgres / password_from_env |

## 2. Manual Deployment

### Step 1: Install Dependencies

```bash
# Install Python 3.9+ and required system packages
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib

# Install MinIO (S3-compatible storage)
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# Or use package manager
# sudo apt-get install -y minio
```

### Step 2: Set Up Database

```bash
# Create database and user
sudo -u postgres psql -c "CREATE DATABASE matrix_historian;"
sudo -u postgres psql -c "CREATE USER historian WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE matrix_historian TO historian;"
```

### Step 3: Set Up MinIO

```bash
# Create data directory
sudo mkdir -p /data/minio
sudo chown -R $USER:$USER /data/minio

# Start MinIO
minio server /data/minio --console-address ":9001" &
```

### Step 4: Clone and Configure

```bash
git clone https://github.com/WeepingDogel/matrix-historian.git
cd matrix-historian

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env as shown in Docker section
```

### Step 5: Run Services

```bash
# Terminal 1: Start API service
cd services/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Bot service
cd services/bot
python main.py

# Terminal 3: (Optional) Start analysis service
cd services/analysis
python main.py
```

## 3. Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (minikube, k3s, or cloud Kubernetes)
- kubectl configured
- Helm (optional)

### Step 1: Create Namespace

```bash
kubectl create namespace matrix-historian
```

### Step 2: Create Secrets

```bash
# Create secret from .env file
kubectl create secret generic matrix-historian-secrets \
  --namespace matrix-historian \
  --from-file=.env=./.env
```

### Step 3: Deploy with Helm (Recommended)

```bash
# Add Helm repository (if available)
helm repo add matrix-historian https://charts.matrix-historian.org

# Install chart
helm install matrix-historian matrix-historian/matrix-historian \
  --namespace matrix-historian \
  --values values.yaml
```

### Step 4: Deploy Manifests

See `k8s/` directory for example manifests:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get all -n matrix-historian
```

## 4. Cloud Platform Deployment

### AWS (ECS/EKS)

```bash
# Build and push Docker images
aws ecr create-repository --repository-name matrix-historian
docker build -t matrix-historian .
docker tag matrix-historian:latest <account-id>.dkr.ecr.<region>.amazonaws.com/matrix-historian:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/matrix-historian:latest

# Deploy with CloudFormation or Terraform
# See cloud/aws/ directory for templates
```

### Google Cloud (GKE)

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/matrix-historian

# Deploy to GKE
kubectl apply -f cloud/gcp/
```

### Azure (AKS)

```bash
# Build and push to ACR
az acr build --registry <registry-name> --image matrix-historian .

# Deploy to AKS
kubectl apply -f cloud/azure/
```

## Configuration Details

### Matrix Bot Configuration

The bot service requires:
- Valid Matrix access token
- Room IDs to monitor
- Appropriate permissions in each room

To get an access token:
1. Log into Element Web
2. Settings → Help & About → Access Token
3. Copy the token starting with `syt_`

### Database Configuration

PostgreSQL settings for performance:

```sql
-- Recommended settings for production
ALTER SYSTEM SET shared_buffers = '1GB';
ALTER SYSTEM SET effective_cache_size = '3GB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### Storage Configuration

MinIO settings for media storage:

```yaml
# minio/config.yaml
version: "v1"
storageclass:
  standard:
    parity: 2
    disksperreplica: 4
```

### API Configuration

Environment variables for API service:

```env
# Security
API_SECRET_KEY=your-secret-key-here
API_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]

# Rate limiting
API_RATE_LIMIT=100/ minute

# Cache settings
API_CACHE_TTL=300
```

## Monitoring and Maintenance

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec db pg_isready

# Storage health
curl http://localhost:9001/minio/health/live
```

### Logging

```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f bot

# Export logs
docker-compose logs --tail=1000 > logs.txt
```

### Backup Strategy

#### Database Backups

```bash
# Daily backup script
docker-compose exec db pg_dump -U postgres matrix_historian > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup.sql | docker-compose exec -T db psql -U postgres matrix_historian
```

#### Media Backups

```bash
# Sync MinIO bucket to backup location
mc mirror minio/matrix-media s3/backup-bucket/
```

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Database performance
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# API metrics
curl http://localhost:8000/metrics
```

## Scaling Considerations

### Vertical Scaling

Increase resources for existing services:

```yaml
# docker-compose.override.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    environment:
      - WORKERS=4
```

### Horizontal Scaling

Scale services independently:

```bash
# Scale API service
docker-compose up -d --scale api=3

# Scale bot service (if monitoring multiple homeservers)
docker-compose up -d --scale bot=2
```

### Database Scaling

For large archives:
1. Add read replicas
2. Implement connection pooling
3. Add caching layer (Redis)

## Security Considerations

### Network Security

```yaml
# docker-compose.yml - Network isolation
networks:
  internal:
    internal: true
  public:
    driver: bridge
```

### Secrets Management

```bash
# Use Docker secrets
echo "your_password" | docker secret create db_password -

# Or use external secrets manager
# - HashiCorp Vault
# - AWS Secrets Manager
# - Azure Key Vault
```

### SSL/TLS Configuration

```nginx
# Nginx configuration for SSL
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
```

## Troubleshooting

### Common Issues

1. **Bot won't connect to Matrix**
   - Verify access token
   - Check homeserver URL
   - Ensure bot account exists

2. **Database connection errors**
   - Check PostgreSQL is running
   - Verify credentials in `.env`
   - Check network connectivity

3. **API not responding**
   - Check port 8000 is available
   - View API logs for errors
   - Verify dependencies are installed

4. **Media storage issues**
   - Check MinIO is running
   - Verify bucket exists
   - Check permissions

### Debugging Commands

```bash
# Check service status
docker-compose ps
docker-compose logs --tail=50

# Test database connection
docker-compose exec db psql -U postgres -c "\l"

# Test API endpoints
curl -v http://localhost:8000/health

# Check disk space
df -h
docker system df
```

### Recovery Procedures

#### Database Recovery

```bash
# Stop services
docker-compose down

# Restore from backup
cat backup.sql | docker-compose exec -T db psql -U postgres matrix_historian

# Start services
docker-compose up -d
```

#### Media Recovery

```bash
# Restore from S3 backup
mc mirror s3/backup-bucket/ minio/matrix-media/
```

## Upgrading

### Version Upgrade Process

1. Backup database and media
2. Stop services: `docker-compose down`
3. Pull latest code: `git pull`
4. Update environment variables if needed
5. Rebuild images: `docker-compose build`
6. Start services: `docker-compose up -d`
7. Run migrations if any: `docker-compose exec api alembic upgrade head`

## Support

For deployment issues:
1. Check the [GitHub Issues](https://github.com/WeepingDogel/matrix-historian/issues)
2. Review logs: `docker-compose logs`
3. Open a new issue with deployment details

---

*Matrix Historian is now deployed and ready to archive your conversations!*