# Cafe Ordering System
**Backend Documentation**

## 1. Project Overview
This system is designed to streamline cafe operations by digitizing the order-to-fulfillment lifecycle. It specifically addresses role-based access control (RBAC) for three primary actors: **Customers**, **Chefs**, and **HR Managers**.

### Core Process Mapping (DFD Reference)
* **Process 1.0 (User Management):** Managed via `authService.py`. Handles registration, secure login, and HR verification.
* **Process 2.0 (Menu Management):** Managed via `menuService.py`. Allows the Chef to maintain the $D2$ Menu store.
* **Process 3.0 (Ordering):** Managed via `orderService.py`. Handles transaction logging ($D3$), QR token generation, and fulfillment validation.
* **Process 4.0 (Reporting):** Managed via `reportService.py`. Generates financial snapshots for the Finance Department.

## 2. Control Framework
The system implements the following security and integrity controls:

| Control Category | Implementation | Goal |
| :--- | :--- | :--- |
| **Identity Management** | Bcrypt Password Hashing | Data at Rest Protection |
| **Authorization** | JWT (JSON Web Tokens) with RBAC | Principal of Least Privilege |
| **Input Validation** | Price & Date Range checking | Data Integrity |
| **Non-Repudiation** | UUID4 Transaction Tokens | Prevention of Order Guessing |
| **Audit Trail** | `checked_out_at` Timestamps | Traceability of Fulfillment |

## 3. Installation & Setup

### Prerequisites
* Python 3.10+

### Steps
1. **Clone the repository** and navigate to the root directory.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment:** create an .env file in root directory and add your secret details ( SECRET_KEY, DATABASE_URI, .., ..,).
4. **Initialize database migration:**
Use the Migration Engine to ensure schema integrity:

   ```bash
   # Initialize the migration repository (first time only)
   flask db init

   # Generate the initial migration script
   flask db migrate -m "Initial migration for D1, D2, and D3"

   # Apply the migration to create the physical database
   flask db upgrade
   ```
## 4. API Summary
The system is organized into four main API Blueprints, ensuring segregation of duties as required for Auditing.

| **Blueprint** | **Endpoint** | **Role** | **description** |
| :--- | :--- | :--- | :--- |
| auth | /login | All | Validate credentials and returns JWT. |
| auth | /register | All | Register users and returns JSON. |
| auth | /verify-user/<int:user_id> | HR | Verify pending users and returns message. |
| auth | /me | All | Validate the token and return current session data. |
| menu | /public | All | Fetch menu and returns only items that are currently marked as available. |
| menu | /inventory | Chef | returns all items, including out-of-stock items. |
| menu | /add | Chef | Allows the Chef to add new resources to D2(menu_table). |
| menu | /update/<int:item_id> | Chef | Allows the Chef to modify existing item details or prices. |
| menu | /toggle/<int:item_id> | Chef | Quick toggle for availability status. |
| orders | /place | Customer | Places an order. |
| orders | /verify | Chef | Validates an order. |
| orders | /history | Customer | Returns the order history for the logged in customer. |
| orders | /queue | Chef | Returns all pending orders for the Chef's dashboard. |
| reports | /generate | HR | Aggregates D3 data and generates a PDF for Finance. |
| reports | /download | HR | retrieve the generated file (pdf). |
| reports | /summary | HR | Provides real-time metrics for the HR Manager's dashboard. |

## 5. Directory Structure
The project follows a N-Tier Architecture to separate concerns and improve maintainability:

.
├── app.py                    # FLASK_APP entry point
├── app/
│   ├── __init__.py           # Factory pattern (create_app)
│   ├── config.py             # Environmental Configuration
│   ├── security.py           # Auth Decorators & Cryptography
│   ├── models/               # Data Entities (SQLAlchemy Models)
│   │   ├── user.py           # User model (D1)
│   │   ├── menuItem.py       # Menu model (D2)
│   │   └── Transaction.py    # Order model (D3)
│   ├── api/                  # REST endpoints (Route Handlers)
│   ├── services/             # Business Logic Layer (Process Logic)
│   ├── static/               # File Storage (Generated QRs & Reports)
│   ├── repositories/         # Data Access Layer (Direct DB CRUD)
│   └── utils/                # Helper Tools (QR & PDF Generators)
├── .env                      # Secret Environment Variables (Hidden)
├── README.md                 # Project Documentation
├── requirements.txt          # System Dependencies
├── instance/                 # database location in development
│   ├── cafe_system.db        # SQLite database
├── migrations/               # Database version control
└── tests/                    # Testing scripts




