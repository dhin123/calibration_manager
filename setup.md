# Complete Local Setup Guide - Calibration Management API

This guide will help you run the Calibration Management microservices system locally.

## Prerequisites

Before we start, you'll need to install a few tools.

### Required Software

#### 1. Docker Desktop (Required for all options)
- **Download:** https://www.docker.com/products/docker-desktop/
- **Install for your OS:** Windows, Mac, or Linux
- **After installation:** Make sure Docker Desktop is running (you'll see a whale icon in your system tray)

#### 2. Git (Required)
- **Download:** https://git-scm.com/downloads
- **Test installation:** Open terminal and type `git --version`

#### 3. curl (Usually pre-installed)
- **Test:** Open terminal and type `curl --version`
- **If missing:** 
  - **Mac:** `brew install curl` (install Homebrew first if needed)
  - **Windows:** Download from https://curl.se/windows/
  - **Linux:** `sudo apt-get install curl`

#### 4. jq (Optional but recommended for pretty JSON)
- **What it is:** Makes JSON responses readable
- **Install:**
  - **Mac:** `brew install jq`
  - **Windows:** Download from https://github.com/jqlang/jq/releases
  - **Linux:** `sudo apt-get install jq`

---

## Getting the Code

### Step 1: Download the Project
```bash
# Open a terminal and navigate to where you want the project
cd ~/Desktop  # or wherever you prefer

# Clone the project (download the code)
git clone https://github.com/dhin123/calibration_manager.git
cd calibration_manager

# See what's in the project
ls -la
```

**What you should see:**
```
calibration_manager/
├── api-service/              # API Gateway service
├── calibration-service/      # Calibration business logic
├── tag-service/             # Tag management service
├── common_packages/         # Shared utilities
├── docker-compose.yml       # Docker container configuration
├── deployment               # Kubernetes deployment
├── setup.md                 # local setup guide
└── README.md               # Project documentation
```

---

# Option 1: Quick Start with Docker Compose

## What Docker Compose Does
- **Starts all services automatically** (API Gateway, Calibration Service, Tag Service, Database)
- **Handles networking** between services
- **One command to start everything**

## Step-by-Step Instructions

### Step 1: Start All Services

```bash
# Make sure you're in the project directory
cd calibration_manager

# Start all services in the background
docker-compose up -d or docker compose up -d
# What this does:
# - Downloads PostgreSQL database image
# - Builds your 3 microservices
# - Starts all 4 containers
# - Sets up networking between them
```
```bash
## macOS Apple Silicon (M1/M2) Build Instructions

# If you previously set `DOCKER_DEFAULT_PLATFORM=linux/amd64`,
# you may get 403 errors when installing packages in your containers. 
# To fix this, first unset the override and then rebuild:
unset DOCKER_DEFAULT_PLATFORM
docker compose up --build -d
```
**Expected output:**
```
[+] Running 4/4
 ✔ Container calibration-postgres        Started
 ✔ Container calibration-service         Started  
 ✔ Container tag-service                 Started
 ✔ Container api-gateway                 Started
```

```bash
If you encounter errors like 
# Ports are not available: exposing port TCP 0.0.0.0:5000 -> 0.0.0.0:0: 
# listen tcp 0.0.0.0:5000: bind: address already in use
in docker-compose.yaml, in api-gateway service update ports to an available port 
eg :     ports:
      - "5003:5000"
and make sure to update the port in  every curl command from 5000 to 5003 

```

### Step 2: Verify Everything is Running

```bash
# Check that all containers are running
docker-compose ps

# You should see all services as "running"
```

**Expected output:**
```
NAME                   SERVICE               STATUS
api-gateway            api-gateway           running
calibration-postgres   postgres              running (healthy)
calibration-service    calibration-service   running
tag-service           tag-service            running
```

### Step 3: Test the API

**Open a new terminal window** and test the API:

```bash
# Test 1: Check if API is healthy
curl http://localhost:5000/health

# Expected response (without jq):
{"status":"healthy","service":"calibration-api-gateway","version":"1.0.0","api_version":"v1"}

# With jq for pretty output:
curl http://localhost:5000/health | jq '.'
```

**Expected pretty response:**
```json
{
  "status": "healthy",
  "service": "calibration-api-gateway", 
  "version": "1.0.0",
}
```

### Step 4: Test the Complete Workflow

Let's test all 5 use cases that the system supports:

#### **Use Case 1: Create a Calibration**

```bash
# Create a new calibration
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{
    "calibration_type": "offset",
    "value": 1.5,
    "username": "alice"
  }' | jq '.'
```

**Expected response:**
```json
{
  "status": {
    "calibration_id": 7359259734479736832,
    "code": 201,
    "message": "Calibration created successfully!"
  }
}

```

**📝 Important:** Copy the `calibration_id` from the response! You'll need it for the next steps.

#### **Use Case 2: Get All Calibrations**

```bash
# Get all calibrations
curl http://localhost:5000/api/v1/calibrations | jq '.'
```

**Expected response:**
```json
{
  "data": {
    "calibrations": [
       {
        "calibration_type": "gain",
        "id": 7359258551077842944,
        "timestamp": "2025-08-07T16:26:06.988677+00:00",
        "username": "test2",
        "value": 1.5
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "pages": 1
    }
  },
  "status": {
    "code": 200,
    "message": "Success"
  }
}
```

#### **Use Case 3: Add Calibration to a Tag**

```bash
# Replace CALIBRATION_ID with the actual ID from use case 1
CALIBRATION_ID=1753840813590716416

curl -X POST http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags \
  -H "Content-Type: application/json" \
  -d '{"tag_name": "production"}' | jq '.'
```

**Expected response:**
```json
{
  "data": {
    "calibration_id": 7359267120674373632,
    "tag_id": 2,
    "tag_name": "qa"
  },
  "status": {
    "code": 201,
    "message": "Calibration successfully added to tag 'qa'"
  }
}

```

#### **Use Case 4: Get Tags for a Calibration**

```bash
# Get all tags for the calibration
curl http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags | jq '.'
```

**Expected response:**
```json
{
  "data": {
    "calibration_id": 7359258527640338432,
    "calibration_info": {
      "calibration_type": "gain",
      "id": 7359258527640338432,
      "timestamp": "2025-08-07T16:26:01.401503+00:00",
      "username": "test1",
      "value": 1.5
    },
    "tag_count": 0,
    "tags": []
  },
  "status": {
    "code": 200,
    "message": "Success"
  }
}

```

#### **Use Case 5: Advanced Filtering**

```bash
# Filter calibrations by username
curl "http://localhost:5000/api/v1/calibrations?username=alice" | jq '.'

# Filter by calibration type
curl "http://localhost:5000/api/v1/calibrations?calibration_type=offset" | jq '.'

# Filter by tag (this tests cross-service communication!)
curl "http://localhost:5000/api/v1/calibrations?tag_name=production" | jq '.'

# Combined filtering
curl "http://localhost:5000/api/v1/calibrations?username=alice&calibration_type=offset&tag_name=production" | jq '.'
```

#### **Use Case 6: Remove Calibration from Tag**

```bash
# Remove the calibration from the production tag
curl -X DELETE http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags/production | jq '.'

# Verify it was removed
curl http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags | jq '.'
```

### Step 5: Create More Test Data

Let's create more calibrations to test filtering:

```bash
# Create calibration for Bob
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{
    "calibration_type": "gain",
    "value": 2.0,
    "username": "bob"
  }' | jq '.'

# Create calibration for Charlie  
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{
    "calibration_type": "temperature", 
    "value": 25.5,
    "username": "charlie"
  }' | jq '.'

# Now test filtering by different users
curl "http://localhost:5000/api/v1/calibrations?username=bob" | jq '.'
curl "http://localhost:5000/api/v1/calibrations?calibration_type=gain" | jq '.'
```

### Step 6: Monitor the System

```bash
# View logs from all services
docker-compose logs -f

# View logs from just the API Gateway
docker-compose logs -f api-gateway

# View logs from a specific service
docker-compose logs -f calibration-service

# Press Ctrl+C to stop viewing logs
```

### Step 7: Stop the System

```bash
# Stop all services
docker-compose down

# To completely clean up (removes data too)
docker-compose down -v
```

---

# Option 2: Kubernetes Deployment 

This option shows how to deploy the same system using Kubernetes.

## What Kubernetes Does
- **Container orchestration** - Manages multiple containers
- **Service discovery** - Services can find each other automatically  
- **Scaling** - Can run multiple copies of services
- **Health monitoring** - Restarts failed containers

## Prerequisites for Kubernetes

### Enable Kubernetes in Docker Desktop

1. **Open Docker Desktop**
2. **Go to Settings** (gear icon)
3. **Click "Kubernetes" tab**
4. **Check "Enable Kubernetes"**
5. **Click "Apply & Restart"**
6. **Wait for green dot** next to Kubernetes

### Test Kubernetes

```bash
# Test that kubectl (Kubernetes command tool) works
kubectl version --client

# Test cluster connection
kubectl cluster-info
```

## Step-by-Step Kubernetes Deployment

### Step 1: Prepare Docker Images

```bash
# Make sure you're in the project directory
cd calibration_manager

# Build all images using Docker Compose
docker-compose build

# Tag images for Kubernetes (this creates copies with simpler names)
docker tag calibration_manager-api-gateway:latest api-gateway:latest
docker tag calibration_manager-calibration-service:latest calibration-service:latest  
docker tag calibration_manager-tag-service:latest tag-service:latest

# Verify images exist
docker images | grep -E "(api-gateway|calibration-service|tag-service)"
```

### Step 2: Deploy to Kubernetes

**You need to open TWO terminal windows for this:**

**Terminal 1 - Deployment:**
```bash
cd deployment
# Deploy all services and database
kubectl apply -f k8s-deployment.yaml

# Deploy all networking (services)  
kubectl apply -f k8s-services.yaml

# Check deployment status
kubectl get pods -n calibration
```

**Wait for all pods to show "Running" status:**
```
NAME                                   READY   STATUS    RESTARTS   AGE
api-gateway-xxx                        1/1     Running   0          2m
calibration-service-xxx                1/1     Running   0          2m
postgres-xxx                           1/1     Running   0          2m
tag-service-xxx                        1/1     Running   0          2m
```

### Step 3: Access the API

**Terminal 1 - Keep this running:**
```bash
# This creates a tunnel from your computer to the Kubernetes cluster
kubectl port-forward -n calibration service/api-gateway 5000:5000

# Keep this terminal open! You'll see:
# Forwarding from 127.0.0.1:5000 -> 5000
# Forwarding from [::1]:5000 -> 5000
```

**Terminal 2 - Test the API:**
```bash
# Test the health endpoint
curl http://localhost:5000/health | jq '.'

# Create a calibration
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{
    "calibration_type": "offset",
    "value": 1.5,  
    "username": "kubernetes-user"
  }' | jq '.'

# Get all calibrations
curl http://localhost:5000/api/v1/calibrations | jq '.'
```

### Step 4: Monitor Kubernetes

**Terminal 2 (while Terminal 1 keeps port-forward running):**

```bash
# Check pod status
kubectl get pods -n calibration

# Check services
kubectl get services -n calibration

# View logs from API Gateway
kubectl logs -f -n calibration deployment/api-gateway

# View logs from Calibration Service  
kubectl logs -f -n calibration deployment/calibration-service

# View events (troubleshooting)
kubectl get events -n calibration --sort-by=.metadata.creationTimestamp
```

### Step 5: Scale Services (Optional)

```bash
# Scale API Gateway to 3 replicas
kubectl scale deployment api-gateway --replicas=3 -n calibration

# Scale Calibration Service to 2 replicas
kubectl scale deployment calibration-service --replicas=2 -n calibration

# Check the scaling
kubectl get pods -n calibration
```

### Step 6: Clean Up Kubernetes

```bash
# Stop port forwarding (Ctrl+C in Terminal 1)

# Delete everything
kubectl delete -f k8s-services.yaml
kubectl delete -f k8s-deployment.yaml

# Or delete the entire namespace (removes everything)
kubectl delete namespace calibration
```

---

# Troubleshooting Guide

## Common Issues and Solutions

### Docker Issues

#### "Docker daemon not running"
**Problem:** Docker Desktop is not started  
**Solution:** Start Docker Desktop application

#### "Port already in use"
**Problem:** Port 5000, 5001, 5002, or 5432 is being used  
**Solution:**
```bash
# Find what's using the port
lsof -i :5000  # Replace 5000 with the problematic port

# Kill the process if safe to do so
kill -9 <PID>

# Or change ports in docker-compose.yml
```

#### "Container exits immediately"
**Problem:** Service crashes on startup  
**Solution:**
```bash
# Check container logs
docker-compose logs api-gateway

# Run container interactively to debug
docker-compose run api-gateway /bin/bash
```

### Kubernetes Issues

#### "ErrImagePull" errors
**Problem:** Kubernetes can't find local Docker images  
**Solution:**
```bash
# Make sure images are built and tagged correctly
docker images | grep -E "(api-gateway|calibration-service|tag-service)"

# If missing, rebuild and retag
docker-compose build
docker tag calibration_manager-api-gateway:latest api-gateway:latest
docker tag calibration_manager-calibration-service:latest calibration-service:latest
docker tag calibration_manager-tag-service:latest tag-service:latest
```

#### "Pod stuck in Pending"
**Problem:** Not enough resources or scheduling issues  
**Solution:**
```bash
# Check pod details
kubectl describe pod -n calibration <pod-name>

# Check node resources
kubectl top nodes
```

#### "Can't access API after port-forward"
**Problem:** Port forwarding not working  
**Solution:**
```bash
# Make sure port-forward is running in another terminal
kubectl port-forward -n calibration service/api-gateway 5000:5000

# Check if pods are ready
kubectl get pods -n calibration

# Try different local port
kubectl port-forward -n calibration service/api-gateway 8000:5000
curl http://localhost:8000/health
```

### API Issues

#### "Connection refused"
**Problem:** Service not running or wrong port  
**Solution:**
```bash
# Check what's running on each port
curl http://localhost:5000/health  # API Gateway
curl http://localhost:5001/health  # Calibration Service  
curl http://localhost:5002/health  # Tag Service

# Check Docker containers
docker-compose ps

# Check Kubernetes pods
kubectl get pods -n calibration
```

#### "500 Internal Server Error"
**Problem:** Database connection or service communication issue  
**Solution:**
```bash
# Check database is running
docker-compose logs postgres

# Check service logs
docker-compose logs calibration-service
docker-compose logs tag-service

# For Kubernetes:
kubectl logs -f -n calibration deployment/calibration-service
```

#### "Schema validation errors"
**Problem:** Incorrect JSON format in requests  
**Solution:**
```bash
# Make sure Content-Type header is set
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \  # This is required!
  -d '{"calibration_type": "offset", "value": 1.5, "username": "alice"}'

# Check JSON syntax is valid
echo '{"calibration_type": "offset", "value": 1.5, "username": "alice"}' | jq '.'
```

### Database Issues

#### "Database connection failed"
**Problem:** PostgreSQL not ready or wrong connection string  
**Solution:**
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Test database connection directly
docker-compose exec postgres psql -U calibration_user -d calibration_db -c "SELECT 1;"
```

---

# Quick Reference

## Useful Commands Cheat Sheet

### Docker Compose Commands
```bash
# Start all services
docker-compose up -d

# Stop all services  
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Rebuild images
docker-compose build --no-cache

# Check status
docker-compose ps
```

### Kubernetes Commands
```bash
# Apply deployments
kubectl apply -f k8s-deployment.yaml

# Check pods
kubectl get pods -n calibration

# Port forward  
kubectl port-forward -n calibration service/api-gateway 5000:5000

# View logs
kubectl logs -f -n calibration deployment/api-gateway

# Delete everything
kubectl delete namespace calibration
```

### API Testing Commands
```bash
# Health check
curl http://localhost:5000/health | jq '.'

# Create calibration
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{"calibration_type": "offset", "value": 1.5, "username": "alice"}' | jq '.'

# Get calibrations
curl http://localhost:5000/api/v1/calibrations | jq '.'

# Filter by user
curl "http://localhost:5000/api/v1/calibrations?username=alice" | jq '.'
```

## Port Reference
- **5000** - API Gateway (main entry point)
- **5001** - Calibration Service (internal)
- **5002** - Tag Service (internal)  
- **5432** - PostgreSQL Database (internal)

## Architecture Overview
```
Client (curl) → API Gateway (5000) → Backend Services (5001, 5002) → PostgreSQL (5432)
```

---


