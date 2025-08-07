# Calibration Management API Documentation

## Overview

The Calibration Management API is a microservices-based system for managing calibration data and associated tags. The system provides RESTful endpoints for creating, retrieving, filtering, and tagging calibrations.

### API Information
- **Current Version:** v1.0.0
- **Base URL:** `http://localhost:5000/api/v1` (local) / `https://your-domain.com/api/v1` (production)
- **API Version:** v1
- **Content Type:** `application/json`
- **Authentication:** None (for take-home challenge)

### Architecture
- **API Gateway:** Routes and validates requests (Port 5000)
- **Calibration Service:** Manages calibration data (Port 5001)
- **Tag Service:** Manages tags and calibration-tag relationships (Port 5002)
- **Database:** PostgreSQL with proper relationships

## Table of Contents
1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [Endpoints](#endpoints)
   - [Health & Info](#health--info)
   - [Calibrations](#calibrations)
   - [Tags](#tags)
6. [Data Models](#data-models)
7. [Examples](#examples)
8. [SDKs](#sdks)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- curl or any HTTP client
- brew install jq

### Running the API
```bash
# Clone the repository
git clone <repository-url>
cd calibration-management

# Start all services
docker-compose up -d

# Verify services are running
curl http://localhost:5000/health
```

### Your First Request
```bash
# Create a calibration
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{
    "calibration_type": "offset",
    "value": 1.5,
    "username": "alice"
  }'

# Get all calibrations
curl http://localhost:5000/api/v1/calibrations
```

## Authentication

**Current Version:** No authentication required for this take-home challenge.

**Production Considerations:** 
- JWT Bearer tokens
- API key authentication
- OAuth 2.0 integration
- Rate limiting by user/API key

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid request data or schema validation failed |
| `404` | Not Found | Resource not found |
| `422` | Unprocessable Entity | Valid request format but business logic validation failed |
| `500` | Internal Server Error | Server-side error |

### Error Response Format

```json
{
  "status": {
    "code": 400,
    "message": "Invalid schema. Please use the correct schema for calibration creation"
  },
  "api_version": "v1",
  "errors": [
    {
      "field": "value",
      "message": "Value must be a number"
    }
  ]
}
```

## Rate Limiting

**Current:** No rate limiting implemented  
**Production:** 1000 requests per hour per IP

Rate limit headers will be included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642685400
```

---

# Endpoints
### API Versions
Get information about supported API versions.

**Endpoint:** `GET /api/versions`

```bash
curl http://localhost:5000/api/versions
```

**Response:**
```json
{
  "supported_versions": ["v1"],
  "current_version": "v1",
  "deprecated_versions": [],
  "sunset_versions": []
}
```

---

## Calibrations

### Create Calibration
Create a new calibration entry.

**Endpoint:** `POST /api/v1/calibrations`

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `calibration_type` | string | Yes | Type of calibration (e.g., "offset", "gain") |
| `value` | number | Yes | Calibration value |
| `username` | string | Yes | Username of the person creating the calibration |

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{
    "calibration_type": "offset",
    "value": 1.5,
    "username": "alice"
  }'
```

**Response:** `201 Created`
```json
{
  "status": {
    "code": 201,
    "message": "Calibration created successfully",
    "calibration_id": 1753840813590716416
  },
  "api_version": "v1"
}
```

### Get Calibrations
Retrieve calibrations with optional filtering and pagination.

**Endpoint:** `GET /api/v1/calibrations`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | string | Filter by username |
| `calibration_type` | string | Filter by calibration type |
| `tag_name` | string | Filter by tag name |
| `start_date` | string (ISO 8601) | Filter by start date |
| `end_date` | string (ISO 8601) | Filter by end date |
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page (default: 20, max: 100) |

**Example Requests:**
```bash
# Get all calibrations
curl http://localhost:5000/api/v1/calibrations

# Filter by user
curl "http://localhost:5000/api/v1/calibrations?username=alice"

# Filter by type
curl "http://localhost:5000/api/v1/calibrations?calibration_type=offset"

# Filter by tag
curl "http://localhost:5000/api/v1/calibrations?tag_name=production"

# Combined filtering
curl "http://localhost:5000/api/v1/calibrations?username=alice&calibration_type=offset&tag_name=production"

# Pagination
curl "http://localhost:5000/api/v1/calibrations?page=2&limit=10"

# Date range filtering
curl "http://localhost:5000/api/v1/calibrations?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z"
```

**Response:** `200 OK`
```json
{
  "data": {
    "calibrations": [
      {
        "id": 1753840813590716416,
        "calibration_type": "offset",
        "value": 1.5,
        "username": "alice",
        "timestamp": "2025-08-06T23:00:00.000000",
        "created_at": "2025-08-06T23:00:00.000000",
        "updated_at": "2025-08-06T23:00:00.000000"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "status": {
    "code": 200,
    "message": "Success"
  },
  "api_version": "v1"
}
```

---

## Tags

### Add Calibration to Tag
Associate a calibration with a tag.

**Endpoint:** `POST /api/v1/calibrations/{calibration_id}/tags`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `calibration_id` | integer | ID of the calibration |

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tag_name` | string | Yes | Name of the tag |
| `added_by` | string | No | Username adding the tag (default: "system") |

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/calibrations/1753840813590716416/tags \
  -H "Content-Type: application/json" \
  -d '{
    "tag_name": "production"
  }'
```

**Response:** `201 Created`
```json
{
  "status": {
    "code": 201,
    "message": "Calibration successfully added to tag 'production'"
  },
  "data": {
    "calibration_id": 1753840813590716416,
    "tag_name": "production",
    "tag_id": 1,
    "added_at": "2025-08-06T23:01:00.000000",
    "added_by": "system"
  },
  "api_version": "v1"
}
```

### Remove Calibration from Tag
Remove the association between a calibration and a tag.

**Endpoint:** `DELETE /api/v1/calibrations/{calibration_id}/tags/{tag_name}`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `calibration_id` | integer | ID of the calibration |
| `tag_name` | string | Name of the tag to remove |

**Example Request:**
```bash
curl -X DELETE http://localhost:5000/api/v1/calibrations/1753840813590716416/tags/production
```

**Response:** `200 OK`
```json
{
  "status": {
    "code": 200,
    "message": "Calibration successfully removed from tag 'production'"
  },
  "data": {
    "calibration_id": 1753840813590716416,
    "tag_name": "production",
    "removed_at": "2025-08-06T23:02:00.000000"
  },
  "api_version": "v1"
}
```

### Get Calibration Tags
Retrieve all tags associated with a specific calibration.

**Endpoint:** `GET /api/v1/calibrations/{calibration_id}/tags`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `calibration_id` | integer | ID of the calibration |

**Example Request:**
```bash
curl http://localhost:5000/api/v1/calibrations/1753840813590716416/tags
```

**Response:** `200 OK`
```json
{
  "data": {
    "calibration_id": 1753840813590716416,
    "calibration_info": {
      "id": 1753840813590716416,
      "calibration_type": "offset",
      "value": 1.5,
      "username": "alice",
      "timestamp": "2025-08-06T23:00:00.000000"
    },
    "tags": [
      {
        "tag_id": 1,
        "tag_name": "production",
        "added_at": "2025-08-06T23:01:00.000000",
        "added_by": "system"
      }
    ],
    "tag_count": 1
  },
  "status": {
    "code": 200,
    "message": "Success"
  },
  "api_version": "v1"
}
```

### Get All Tags
Retrieve a list of all available tags.

**Endpoint:** `GET /api/v1/tags`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page (default: 20) |

**Example Request:**
```bash
curl http://localhost:5000/api/v1/tags
```

**Response:** `200 OK`
```json
{
  "data": {
    "tags": [
      {
        "tag_id": 1,
        "tag_name": "production",
        "created_at": "2025-08-06T23:01:00.000000",
        "calibration_count": 5
      },
      {
        "tag_id": 2,
        "tag_name": "testing",
        "created_at": "2025-08-06T23:05:00.000000",
        "calibration_count": 2
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 2,
      "pages": 1
    }
  },
  "status": {
    "code": 200,
    "message": "Success"
  },
  "api_version": "v1"
}
```

---

# Data Models

## Calibration Model

```json
{
  "id": 1753840813590716416,
  "calibration_type": "string",
  "value": 1.5,
  "username": "string", 
  "timestamp": "2025-08-06T23:00:00.000000",
  "created_at": "2025-08-06T23:00:00.000000",
  "updated_at": "2025-08-06T23:00:00.000000"
}
```

**Field Descriptions:**
- `id`: Unique Snowflake ID (64-bit integer)
- `calibration_type`: Type of calibration (offset, gain, temperature, etc.)
- `value`: Numeric calibration value
- `username`: Username of the creator
- `timestamp`: When the calibration was taken
- `created_at`: Record creation timestamp
- `updated_at`: Record last update timestamp

## Tag Model

```json
{
  "tag_id": 1,
  "tag_name": "production",
  "created_at": "2025-08-06T23:01:00.000000",
  "calibration_count": 5
}
```

**Field Descriptions:**
- `tag_id`: Unique tag identifier
- `tag_name`: Human-readable tag name
- `created_at`: When the tag was first created
- `calibration_count`: Number of calibrations with this tag

## Calibration-Tag Association Model

```json
{
  "calibration_id": 1753840813590716416,
  "tag_id": 1,
  "tag_name": "production",
  "added_at": "2025-08-06T23:01:00.000000",
  "added_by": "system",
  "is_active": true
}
```

---

# Examples

## Complete Workflow Example

Here's a complete example workflow showing how to use the API:

```bash
# 1. Create a calibration
RESPONSE=$(curl -s -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{
    "calibration_type": "offset",
    "value": 1.5,
    "username": "alice"
  }')

echo "Created calibration: $RESPONSE"

# Extract calibration_id (you'll need to parse JSON)
CALIBRATION_ID=1753840813590716416  # Use actual ID from response

# 2. Tag the calibration for production
curl -X POST http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags \
  -H "Content-Type: application/json" \
  -d '{"tag_name": "production"}'

# 3. Tag it for quality review
curl -X POST http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags \
  -H "Content-Type: application/json" \
  -d '{"tag_name": "quality-review"}'

# 4. Get all production calibrations
curl "http://localhost:5000/api/v1/calibrations?tag_name=production"

# 5. Get tags for our calibration
curl http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags

# 6. Remove from quality review (approved)
curl -X DELETE http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags/quality-review

# 7. Get final state
curl http://localhost:5000/api/v1/calibrations/$CALIBRATION_ID/tags
```

## Filtering Examples

```bash
# Find all calibrations by Alice
curl "http://localhost:5000/api/v1/calibrations?username=alice"

# Find all offset calibrations
curl "http://localhost:5000/api/v1/calibrations?calibration_type=offset"

# Find all production-tagged calibrations
curl "http://localhost:5000/api/v1/calibrations?tag_name=production"

# Find Alice's offset calibrations in production
curl "http://localhost:5000/api/v1/calibrations?username=alice&calibration_type=offset&tag_name=production"

# Find calibrations from the last 24 hours
curl "http://localhost:5000/api/v1/calibrations?start_date=$(date -d '1 day ago' -Iseconds)"

# Paginated results
curl "http://localhost:5000/api/v1/calibrations?page=1&limit=5"
```

## Error Handling Examples

```bash
# Invalid schema (missing required fields)
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{"calibration_type": "offset"}'
# Returns: 400 Bad Request

# Invalid data type
curl -X POST http://localhost:5000/api/v1/calibrations \
  -H "Content-Type: application/json" \
  -d '{
    "calibration_type": "offset",
    "value": "not-a-number",
    "username": "alice"
  }'
# Returns: 400 Bad Request

# Non-existent calibration
curl http://localhost:5000/api/v1/calibrations/999999999999999999/tags
# Returns: 404 Not Found
```

### v1.0.0 (2025-08-06)
- Initial release
- Core CRUD operations for calibrations
- Tag management functionality
- Filtering by user, type, tag, and date
- Pagination support
- Comprehensive error handling
- API versioning support

---

### Common Calibration Types
- `offset` - Offset calibration
- `gain` - Gain calibration  
- `temperature` - Temperature calibration
- `pressure` - Pressure calibration
- `voltage` - Voltage calibration
- `current` - Current calibration
- `frequency` - Frequency calibration
- `phase` - Phase calibration

### HTTP Methods Used
- `GET` - Retrieve resources
- `POST` - Create resources
- `DELETE` - Remove resources

### Content Types
- Request: `application/json`
- Response: `application/json`
