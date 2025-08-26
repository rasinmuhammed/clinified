# Clinified Setup Guide

This guide will help you set up the Clinified development environment and get the application running locally.

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (v20.10+)
- **Python** (3.9+)
- **Flutter SDK** (3.0+)
- **Git** (2.30+)
- **Node.js** (16+) - for web dashboard (optional)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd clinified
```

### 2. Environment Setup

#### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Application
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production
APP_NAME=Clinified API
VERSION=1.0.0

# Database
DATABASE_URL=postgresql://clinified:clinified123@localhost:5432/clinified

# Redis
REDIS_URL=redis://localhost:6379

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# File Storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "image/gif", "application/pdf", "text/plain"]

# ABDM Integration (Sandbox)
ABDM_BASE_URL=https://healthidsbx.abdm.gov.in
ABDM_CLIENT_ID=your-abdm-client-id
ABDM_CLIENT_SECRET=your-abdm-client-secret

# Payment Gateway (Razorpay)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# SMS/WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Sync Settings
SYNC_BATCH_SIZE=100
SYNC_RETRY_ATTEMPTS=3
SYNC_RETRY_DELAY=5
```

### 3. Database Setup

#### Option A: Using Docker (Recommended)

```bash
cd deployment
docker-compose up -d postgres redis
```

#### Option B: Local Installation

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database**:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE clinified;
   CREATE USER clinified WITH PASSWORD 'clinified123';
   GRANT ALL PRIVILEGES ON DATABASE clinified TO clinified;
   \q
   ```

3. **Install Redis**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Windows
   # Download from https://redis.io/download
   ```

### 4. Backend Setup

#### Install Dependencies

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

#### Database Migrations

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

#### Run the Backend

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py
python app/main.py
```

The API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 5. Mobile App Setup

#### Install Flutter Dependencies

```bash
cd mobile
flutter pub get
```

#### Run the Mobile App

```bash
# Check available devices
flutter devices

# Run on connected device or emulator
flutter run

# Run in debug mode
flutter run --debug

# Run in release mode
flutter run --release
```

### 6. Web Dashboard Setup (Optional)

```bash
cd web
npm install
npm start
```

The web dashboard will be available at: http://localhost:3000

## 🐳 Docker Setup (Alternative)

If you prefer to run everything in Docker:

```bash
cd deployment

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services Available:

- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Nginx**: http://localhost:80
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601
- **MinIO**: http://localhost:9000

## 🔧 Development Tools

### Code Quality

#### Backend (Python)

```bash
cd backend

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Run tests
pytest tests/
pytest --cov=app tests/
```

#### Mobile (Flutter)

```bash
cd mobile

# Format code
dart format lib/

# Analyze code
flutter analyze

# Run tests
flutter test

# Generate code
flutter packages pub run build_runner build
```

### Database Management

```bash
# Access PostgreSQL
psql -h localhost -U clinified -d clinified

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### API Testing

```bash
# Using curl
curl -X GET "http://localhost:8000/health"

# Using httpie
http GET localhost:8000/health

# Using the interactive docs
# Visit http://localhost:8000/docs
```

## 📱 Mobile App Configuration

### Android Setup

1. **Android Studio**: Install Android Studio and Android SDK
2. **Emulator**: Create an Android Virtual Device (AVD)
3. **Device**: Enable Developer Options and USB Debugging

### iOS Setup (macOS only)

1. **Xcode**: Install Xcode from App Store
2. **Simulator**: Use iOS Simulator or connect physical device
3. **Certificates**: Set up development certificates

### Flutter Configuration

```bash
# Check Flutter installation
flutter doctor

# Configure Android
flutter config --android-sdk /path/to/android/sdk

# Configure iOS (macOS only)
flutter config --ios-sdk /path/to/ios/sdk
```

## 🔒 Security Configuration

### SSL/TLS Setup

```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure Nginx with SSL
# Edit deployment/nginx/conf.d/default.conf
```

### Environment Security

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set up environment variables
export CLINIFIED_SECRET_KEY="your-generated-secret"
export CLINIFIED_DATABASE_URL="your-database-url"
```

## 📊 Monitoring Setup

### Prometheus Configuration

```bash
# Edit deployment/prometheus/prometheus.yml
# Add your application targets
```

### Grafana Dashboards

1. Access Grafana: http://localhost:3000
2. Login: admin/admin123
3. Add Prometheus data source
4. Import dashboards from `deployment/grafana/dashboards/`

### Logging Configuration

```bash
# Configure log levels in .env
LOG_LEVEL=DEBUG  # For development
LOG_LEVEL=INFO   # For production
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run integration tests
pytest tests/integration/
```

### Mobile Testing

```bash
cd mobile

# Run unit tests
flutter test

# Run integration tests
flutter test integration_test/

# Run on specific device
flutter test -d <device-id>
```

### API Testing

```bash
# Using pytest with httpx
pytest tests/api/ -v

# Using Postman
# Import the Postman collection from docs/postman/
```

## 🚀 Production Deployment

### Environment Variables

```bash
# Production .env
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/clinified
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=["your-domain.com"]
```

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

## 🆘 Troubleshooting

### Common Issues

#### Backend Issues

```bash
# Database connection error
# Check DATABASE_URL in .env
# Ensure PostgreSQL is running

# Import errors
# Activate virtual environment
source venv/bin/activate

# Port already in use
# Change port in uvicorn command
uvicorn app.main:app --port 8001
```

#### Mobile Issues

```bash
# Flutter doctor issues
flutter doctor --android-licenses
flutter clean
flutter pub get

# Device not detected
flutter devices
adb devices  # For Android
```

#### Docker Issues

```bash
# Container not starting
docker-compose logs <service-name>

# Port conflicts
# Change ports in docker-compose.yml

# Volume issues
docker-compose down -v
docker-compose up -d
```

### Getting Help

1. **Documentation**: Check the `/docs` directory
2. **Issues**: Create an issue on GitHub
3. **Discussions**: Use GitHub Discussions
4. **Email**: support@clinified.com

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Flutter Documentation](https://flutter.dev/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [ABDM Documentation](https://abdm.gov.in/)

---

This setup guide should get you started with developing Clinified. For more detailed information, refer to the specific documentation in the `/docs` directory. 