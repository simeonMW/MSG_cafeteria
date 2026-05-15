# Cafe Ordering System - Startup Guide
---

## Step-by-Step Startup Instructions

### Step 1: Navigate to Project Directory
```bash
cd c:\Users\USER\Desktop\cafeOrdering\cafeOrderingSystem
```

### Step 2: Set Flask Environment Variable (Required!)
**On Windows (PowerShell):**
```powershell
$env:FLASK_APP="app.py"
```

**On Windows (Command Prompt):**
```cmd
set FLASK_APP=app.py
```

**On macOS/Linux:**
```bash
export FLASK_APP=app.py
```

### Step 3: (First Time Only) Initialize Database
If you haven't run these commands yet:
```bash
# Create migrations folder
flask db init

# Generate initial migration based on models
flask db migrate -m "Initial schema"

# Apply migration to create database and tables
flask db upgrade
```
✅ Database setup is complete! The `cafe_system.db` created directory.

### Step 4: Start the Server
```bash
python app.py
```

**Expected Output:**
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.16.35.82:5000
```

The server is now accessible at: **http://127.0.0.1:5000**

### Step 5: Stop the Server
Press `CTRL+C` in the terminal to stop the server.

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user

### Menu Management
- `GET /api/menu/public` - Get available menu items
- `GET /api/menu/inventory` - Get full inventory (Chef only)
- `POST /api/menu/add` - Add menu item (Chef only)

### Orders
- `POST /api/orders/place` - Place an order
- `POST /api/orders/validate` - Validate order (Chef only)

### Reports
- `POST /api/reports/generate` - Generate financial report (HR only)

---

## Testing the API

test the API endpoints using:
- **Postman** - GUI API client
- **cURL** - Command line tool
- **Python requests** library
- **Thunder Client** VS Code extension

Example cURL request:
```bash
curl -X GET http://127.0.0.1:5000/api/menu/public \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Running Tests
```bash
python tests/systemTest1.py
```

---

## Environment (.env) File (Optional)
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///cafe_system.db
FLASK_DEBUG=True
```

---

## Note

1. **FLASK_APP Must Be Set Every Time**
   - Each terminal session requires: `set FLASK_APP=app.py`
   - Or add it to your .env file

2. **Database Location**
   - SQLite database: `cafe_system.db` (in project root)
   - Created automatically on first `flask db upgrade`

3. **QR Codes & Reports**
   - QR codes stored in: `app/static/qrcodes/`
   - Reports stored in: `app/static/reports/`
   - Directories created automatically on app start

4. **Development vs Production**
   - Current setup is for development (debug mode on)
   - For production, use a WSGI server like Gunicorn or Waitress

---

## Next Steps

1.  Start the server: `python app.py`
2.  Create test users via `/api/auth/register`
3.  Test API endpoints
4.  Set up menu items and test orders


