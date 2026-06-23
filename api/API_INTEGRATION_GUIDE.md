# Automated Cafe Ordering System - API Integration Guide

**Version:** 1.0  
**Last Updated:** June 2026  
**Target Audience:** Frontend Engineers (Mobile App & Web App)

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL & Environment](#base-url--environment)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
   - [Authentication Endpoints](#authentication-endpoints)
   - [Menu Endpoints](#menu-endpoints)
   - [Order Endpoints](#order-endpoints)
   - [Report Endpoints](#report-endpoints)
   - [Health Check Endpoint](#health-check-endpoint)
5. [Error Handling](#error-handling)
6. [Security Considerations](#security-considerations)
7. [Response Formats](#response-formats)
8. [Integration Examples](#integration-examples)

---

## Overview

The Automated Cafe Ordering System is a Flask-based REST API designed to support:
- **Customer Mobile App**: Place orders, view QR codes, check order history
- **Chef Mobile App**: View pending orders, verify transactions
- **HR Web App**: Generate and download financial reports

The API uses **JWT (JSON Web Token)** authentication and role-based access control (RBAC) to secure endpoints. All assets (QR codes, PDFs) are hosted on **Supabase Storage** with time-limited signed URLs for secure access.

---

## Base URL & Environment

### Development
```
http://localhost:5000/
```

### Production (Render)
```
https://msg-cafeteria.onrender.com
```

### Headers (All Requests)
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <JWT_TOKEN>"
}
```

---

## Authentication

### JWT Token Structure

The API issues JWT tokens upon successful login. The token must be included in the `Authorization` header for all protected endpoints.

**Token Payload:**
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "role": "customer",
  "exp": 1719122400,
  "iat": 1719118800
}
```

**Token Validity:** 2 hours from issuance

### Roles & Permissions

| Role | Endpoints Accessible |
|------|----------------------|
| `customer` | Register, Login, Place Orders, View History, Get Menu |
| `chef` | Login, Verify Orders, View Inventory, Manage Menu, Update Menu |
| `hr_manager` | Login, Generate Reports, Download Reports |

---

## API Endpoints

### Authentication Endpoints

#### 1. Register User
- **Endpoint:** `POST /api/auth/register`
- **Authentication:** None (Public)
- **Description:** Create a new user account (customer, chef, or hr_manager)

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123!",
  "role": "customer"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user_id": 1
}
```

**Error Responses:**
- `400 Bad Request` - Missing required fields
- `409 Conflict` - Email already exists

---

#### 2. Login User
- **Endpoint:** `POST /api/auth/login`
- **Authentication:** None (Public)
- **Description:** Authenticate a user and receive a JWT token

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 1,
    "email": "john@example.com",
    "role": "customer",
    "verified": true
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `400 Bad Request` - Missing email or password

---

#### 3. Verify User Account
- **Endpoint:** `POST /api/auth/verify-user/<user_id>`
- **Authentication:** Required (HR Manager only)
- **Description:** Verify a user account (activate for ordering). Only HR managers can trigger this.

**Request Body:**
```json
{}
```

**Response (200 OK):**
```json
{
  "message": "User account verified successfully"
}
```

**Error Responses:**
- `403 Forbidden` - Insufficient role permissions
- `400 Bad Request` - User not found or already verified

---

#### 4. Get Current User Info
- **Endpoint:** `GET /api/auth/me`
- **Authentication:** Required (Customer, Chef, or HR Manager)
- **Description:** Retrieve current authenticated user's profile data

**Response (200 OK):**
```json
{
  "user_id": 1,
  "email": "john@example.com",
  "role": "customer",
  "verified": true,
  "created_at": "2026-06-15T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired token

---

### Menu Endpoints

#### 1. Get Public Menu
- **Endpoint:** `GET /api/menu/public`
- **Authentication:** Required (Customer, Chef, or HR Manager)
- **Description:** Retrieve all available menu items (filtered by `is_available=true`)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Nshima",
    "description": "Traditional maize meal",
    "price": 50.00,
    "is_available": true,
    "picture_url": null
  },
  {
    "id": 2,
    "name": "Sadza and Relish",
    "description": "Maize porridge with meat relish",
    "price": 75.00,
    "is_available": true,
    "picture_url": null
  }
]
```

---

#### 2. Get Full Inventory (Chef Only)
- **Endpoint:** `GET /api/menu/inventory`
- **Authentication:** Required (Chef only)
- **Description:** Retrieve all menu items including out-of-stock items

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Nshima",
    "description": "Traditional maize meal",
    "price": 50.00,
    "is_available": true
  },
  {
    "id": 3,
    "name": "Rice",
    "description": "Cooked rice",
    "price": 40.00,
    "is_available": false
  }
]
```

**Error Responses:**
- `403 Forbidden` - Only chefs can access inventory

---

#### 3. Add Menu Item
- **Endpoint:** `POST /api/menu/add`
- **Authentication:** Required (Chef only)
- **Description:** Add a new menu item to the catalog

**Request Body:**
```json
{
  "name": "Breakfast Special",
  "description": "Eggs, toast, and tea",
  "price": 120.00,
  "picture_url": null
}
```

**Response (201 Created):**
```json
{
  "message": "Menu item added successfully",
  "item": {
    "id": 5,
    "name": "Breakfast Special",
    "description": "Eggs, toast, and tea",
    "price": 120.00,
    "is_available": true
  }
}
```

**Error Responses:**
- `400 Bad Request` - Missing required fields (name, price)
- `403 Forbidden` - Insufficient permissions

---

#### 4. Update Menu Item
- **Endpoint:** `PUT /api/menu/update/<item_id>`
- **Authentication:** Required (Chef only)
- **Description:** Update an existing menu item's details or price

**Request Body:**
```json
{
  "name": "Breakfast Special",
  "description": "Eggs, toast, tea, and juice",
  "price": 150.00
}
```

**Response (200 OK):**
```json
{
  "message": "Menu item updated successfully",
  "item": {
    "id": 5,
    "name": "Breakfast Special",
    "description": "Eggs, toast, tea, and juice",
    "price": 150.00,
    "is_available": true
  }
}
```

**Error Responses:**
- `404 Not Found` - Item does not exist
- `403 Forbidden` - Insufficient permissions

---

#### 5. Toggle Item Availability
- **Endpoint:** `PATCH /api/menu/toggle/<item_id>`
- **Authentication:** Required (Chef only)
- **Description:** Quickly toggle an item's availability status (available/unavailable)

**Response (200 OK):**
```json
{
  "message": "Item availability toggled",
  "data": {
    "id": 5,
    "name": "Breakfast Special",
    "is_available": false
  }
}
```

**Error Responses:**
- `404 Not Found` - Item does not exist

---

### Order Endpoints

#### 1. Place Order
- **Endpoint:** `POST /api/orders/place`
- **Authentication:** Required (Customer only)
- **Description:** Place a new order and generate a QR code

**Request Body:**
```json
{
  "item_id": 1
}
```

**Response (201 Created):**
```json
{
  "message": "Order placed successfully. QR Code generated.",
  "transaction_id": 42,
  "token": "a1b2c3d4-e5f6-47a1-b2c3-d4e5f6g7h8i9",
  "qr_code_url": "https://supabase-bucket.com/signed-url?token=xyz&expires_at=...",
  "price_charged": 50.00
}
```

**Notes:**
- The `qr_code_url` is a **signed URL** (expires in 5 minutes)
- The `token` uniquely identifies this order and is embedded in the QR code
- The customer should save the `transaction_id` for history retrieval

**Error Responses:**
- `400 Bad Request` - Item unavailable or does not exist
- `401 Unauthorized` - Invalid or expired token

---

#### 2. Get Transaction QR Code (Retrieve Signed URL)
- **Endpoint:** `GET /api/orders/<transaction_id>/qr`
- **Authentication:** Required (Customer only)
- **Description:** Retrieve a new signed URL for an existing transaction's QR code (useful if the original URL expired)

**Response (200 OK):**
```json
{
  "qr_code_url": "https://supabase-bucket.com/signed-url?token=xyz&expires_at=..."
}
```

**Error Responses:**
- `404 Not Found` - Transaction not found or belongs to another customer
- `401 Unauthorized` - Invalid token

---

#### 3. Verify Order (Chef Scans QR)
- **Endpoint:** `POST /api/orders/verify`
- **Authentication:** Required (Chef only)
- **Description:** Verify an order by scanning the customer's QR code (or providing the token)

**Request Body:**
```json
{
  "token": "a1b2c3d4-e5f6-47a1-b2c3-d4e5f6g7h8i9"
}
```

**Response (200 OK):**
```json
{
  "message": "Success: Order #42 verified and fulfilled."
}
```

**Error Responses:**
- `400 Bad Request` - No token provided
- `401 Unauthorized` - Invalid token
- `400 Bad Request` - Token already used (order already fulfilled)

---

#### 4. Get Order History
- **Endpoint:** `GET /api/orders/history`
- **Authentication:** Required (Customer only)
- **Description:** Retrieve the order history for the logged-in customer

**Response (200 OK):**
```json
[
  {
    "transaction_id": 42,
    "customer_id": 1,
    "item_id": 1,
    "amount": 50.00,
    "token": "a1b2c3d4-e5f6-47a1-b2c3-d4e5f6g7h8i9",
    "status": "checked_out",
    "created_at": "2026-06-20T14:30:00Z",
    "checked_out_at": "2026-06-20T14:35:00Z"
  },
  {
    "transaction_id": 41,
    "customer_id": 1,
    "item_id": 2,
    "amount": 75.00,
    "token": "b2c3d4e5-f6a7-48b2-c3d4-e5f6g7h8i9j0",
    "status": "pending",
    "created_at": "2026-06-19T10:00:00Z",
    "checked_out_at": null
  }
]
```

---

#### 5. Get Chef Queue (Pending Orders)
- **Endpoint:** `GET /api/orders/queue`
- **Authentication:** Required (Chef only)
- **Description:** Retrieve all pending orders for the Chef's dashboard

**Response (200 OK):**
```json
[
  {
    "transaction_id": 41,
    "customer_id": 1,
    "item_id": 2,
    "amount": 75.00,
    "token": "b2c3d4e5-f6a7-48b2-c3d4-e5f6g7h8i9j0",
    "status": "pending",
    "created_at": "2026-06-19T10:00:00Z",
    "checked_out_at": null
  }
]
```

---

### Report Endpoints

#### 1. Generate Financial Report
- **Endpoint:** `POST /api/reports/generate`
- **Authentication:** Required (HR Manager only)
- **Description:** Generate a financial report for a specified date range

**Request Body:**
```json
{
  "start_date": "2026-06-01",
  "end_date": "2026-06-30"
}
```

**Notes:**
- Date format: `YYYY-MM-DD`
- If dates are omitted, the system defaults to the last 30 days

**Response (200 OK):**
```json
{
  "message": "Report generated successfully.",
  "report_details": {
    "report_url": "reports/report_20260623_143000.pdf",
    "transaction_count": 127,
    "generated_at": "2026-06-23T14:30:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid date format or no transactions found
- `403 Forbidden` - Insufficient permissions

---

#### 2. Download Report (Retrieve Signed URL)
- **Endpoint:** `GET /api/reports/download`
- **Authentication:** Required (HR Manager only)
- **Description:** Retrieve a time-limited signed URL to download a previously generated report

**Query Parameters:**
```
?path=reports/report_20260623_143000.pdf
```

**Response (200 OK):**
```json
{
  "download_url": "https://supabase-bucket.com/signed-url?token=xyz&expires_at=..."
}
```

**Notes:**
- The `download_url` is a signed URL (expires in 5 minutes)
- Use this URL to download the PDF directly

**Error Responses:**
- `404 Not Found` - Report file not found
- `403 Forbidden` - Invalid file access attempt

---

#### 3. Get Dashboard Summary
- **Endpoint:** `GET /api/reports/summary`
- **Authentication:** Required (HR Manager only)
- **Description:** Retrieve real-time dashboard metrics (today's revenue, order count, pending orders)

**Response (200 OK):**
```json
{
  "daily_revenue": 2350.50,
  "daily_order_count": 28,
  "pending_orders": 5
}
```

**Error Responses:**
- `403 Forbidden` - Insufficient permissions

---

### Health Check Endpoint

#### Health Status
- **Endpoint:** `GET /api/health/active_injection`
- **Authentication:** None (Public)
- **Description:** Simple health check to verify the API is running (used for Render cron jobs)

**Response (200 OK):**
```json
{
  "message": "healthy"
}
```

---

## Error Handling

### Standard Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Status Code | Meaning | Common Causes |
|---|---|---|
| `200 OK` | Request successful | N/A |
| `201 Created` | Resource created | Order placed, item added |
| `400 Bad Request` | Invalid request format | Missing fields, invalid data |
| `401 Unauthorized` | Authentication failed | Invalid/expired token, missing auth header |
| `403 Forbidden` | Insufficient permissions | Wrong role, access denied |
| `404 Not Found` | Resource not found | Item/transaction/report doesn't exist |
| `409 Conflict` | Resource already exists | Duplicate email during registration |
| `500 Internal Server Error` | Server error | Unexpected backend failure |

### Example Error Handling (Client-side)

**JavaScript/TypeScript:**
```javascript
try {
  const response = await fetch('https://api.example.com/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ email, password })
  });

  if (!response.ok) {
    const error = await response.json();
    console.error(`Error (${response.status}):`, error.error);
    // Handle error based on status code
    switch (response.status) {
      case 401:
        // Redirect to login
        break;
      case 403:
        // Show permission denied message
        break;
      default:
        // Show generic error
    }
  } else {
    const data = await response.json();
    // Handle success
  }
} catch (err) {
  console.error('Network error:', err);
}
```

---

## Security Considerations

### 1. JWT Token Management
- **Storage:** Store tokens securely (e.g., HttpOnly cookies on web, secure storage on mobile)
- **Transmission:** Always send over HTTPS in production
- **Expiration:** Tokens expire after 2 hours. Implement token refresh logic if needed.

### 2. Signed URLs
- **Expiration:** All signed URLs expire after 5 minutes
- **Single-Use:** Not enforced by the API; implement on the client to prevent abuse
- **HTTPS Only:** Always use HTTPS in production

### 3. Role-Based Access Control (RBAC)
- The API enforces role-based permissions on every protected endpoint
- Sending an invalid/expired token will result in a `401 Unauthorized` response
- Attempting to access an endpoint with insufficient permissions will return a `403 Forbidden` response

### 4. Data Validation
- All user inputs are validated server-side
- Email format and password complexity should be validated on both client and server
- Never trust client-side validation alone

### 5. HTTPS Requirement
- Always use HTTPS in production
- Development can use HTTP for local testing

---

## Response Formats

### Data Types

| Type | Format | Example |
|------|--------|---------|
| Integer | Whole number | `123` |
| Float | Decimal number | `50.00` |
| String | Text | `"Nshima"` |
| Boolean | True/False | `true` |
| DateTime | ISO 8601 | `"2026-06-23T14:30:00Z"` |
| UUID | String | `"a1b2c3d4-e5f6-47a1-b2c3-d4e5f6g7h8i9"` |

### Array Responses

When an endpoint returns multiple items, they are wrapped in a JSON array:

```json
[
  { "id": 1, "name": "Item 1" },
  { "id": 2, "name": "Item 2" }
]
```

### Pagination (Future Enhancement)

Currently, all list endpoints return all available records. Pagination may be added in future versions.

---

## Integration Examples

### Example 1: Customer Mobile App - Place Order

```javascript
const placeOrder = async (itemId, token) => {
  const response = await fetch('https://api.example.com/api/orders/place', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ item_id: itemId })
  });

  if (response.status === 201) {
    const data = await response.json();
    console.log('Order placed:', data.transaction_id);
    console.log('QR Code URL:', data.qr_code_url);
    // Display QR code to customer
    displayQRCode(data.qr_code_url);
  } else {
    const error = await response.json();
    console.error('Order failed:', error.error);
  }
};
```

### Example 2: Chef Mobile App - Verify Order

```javascript
const verifyOrder = async (token, jwtToken) => {
  const response = await fetch('https://api.example.com/api/orders/verify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwtToken}`
    },
    body: JSON.stringify({ token })
  });

  if (response.status === 200) {
    const data = await response.json();
    console.log('Order verified:', data.message);
    // Update UI to show success
  } else {
    const error = await response.json();
    console.error('Verification failed:', error.error);
  }
};
```

### Example 3: HR Web App - Generate & Download Report

```javascript
const generateReport = async (startDate, endDate, token) => {
  // Step 1: Generate report
  const genResponse = await fetch('https://api.example.com/api/reports/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ start_date: startDate, end_date: endDate })
  });

  if (genResponse.status === 200) {
    const genData = await genResponse.json();
    const reportPath = genData.report_details.report_url;
    console.log('Report generated:', reportPath);

    // Step 2: Get signed download URL
    const dlResponse = await fetch(
      `https://api.example.com/api/reports/download?path=${reportPath}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (dlResponse.status === 200) {
      const dlData = await dlResponse.json();
      console.log('Download URL:', dlData.download_url);
      // Open download URL in browser or download directly
      window.open(dlData.download_url, '_blank');
    }
  }
};
```

---

## Support & Troubleshooting

### Common Issues

**Q: Token expired, how do I get a new one?**  
A: Call the `/api/auth/login` endpoint again with your credentials.

**Q: Signed URL returns 403 Forbidden**  
A: The URL may have expired (5-minute limit). Request a new one using the appropriate endpoint.

**Q: Getting 401 Unauthorized on every request**  
A: Verify that:
- The token is included in the `Authorization: Bearer <token>` header
- The token hasn't expired
- The token is from the correct server

**Q: Getting 403 Forbidden even with a valid token**  
A: Verify that your user role has permission for the endpoint:
- Customers: Menu, Orders
- Chefs: Menu (full), Orders (verify)
- HR Managers: Reports

### Support Contact

For API issues or questions, contact the backend development team.

---

## Appendix: Database Schema Reference

### User Table
| Field | Type | Notes |
|-------|------|-------|
| id | Integer (PK) | Unique identifier |
| email | String (Unique) | User's email |
| password_hash | String | Hashed password (bcrypt) |
| role | String | 'customer', 'chef', or 'hr_manager' |
| verified | Boolean | Account verification status |
| created_at | DateTime | Account creation time |

### Menu Items Table
| Field | Type | Notes |
|-------|------|-------|
| id | Integer (PK) | Unique identifier |
| name | String | Item name |
| description | String | Item description |
| price | Float | Price in local currency (MWK) |
| is_available | Boolean | Availability status |
| picture_url | String | URL to item image (nullable) |
| created_at | DateTime | Item creation time |

### Transactions Table
| Field | Type | Notes |
|-------|------|-------|
| id | Integer (PK) | Unique identifier |
| customer_id | Integer (FK) | Reference to User |
| item_id | Integer (FK) | Reference to Menu Item |
| order_price | Float | Price at time of order |
| token | String (Unique) | Unique order token |
| qr_code_path | String | Supabase storage path to QR image |
| status | String | 'pending', 'checked_out', or 'cancelled' |
| created_at | DateTime | Order creation time |
| checked_out_at | DateTime | Fulfillment time (nullable) |

---

**End of Document**
