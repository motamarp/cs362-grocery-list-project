# Django Setup Instructions

## Getting Started

### 1. Create a Virtual Environment
```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Copy `.env.example` to `.env` and update values:
```bash
copy .env.example .env
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create a Superuser
```bash
python manage.py createsuperuser
```

### 7. Start the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Admin Interface
Access the Django admin at: `http://localhost:8000/admin`

## API Endpoints
- **Grocery Lists**: `/api/grocery-lists/`
- **Grocery Items**: `/api/grocery-items/`
- **Recipes**: `/api/recipes/`

## Project Structure
```
lettucesave_project/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── lettucesave_project/     # Main project settings
│   ├── __init__.py
│   ├── settings.py          # Project settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
└── lettuce_app/             # Main Django app
    ├── models.py            # Data models
    ├── views.py             # API views
    ├── serializers.py       # DRF serializers
    ├── urls.py              # App URL patterns
    ├── admin.py             # Admin interface
    └── migrations/          # Database migrations
```

## Available Models
- **GroceryList**: Main grocery list container
- **GroceryItem**: Individual items in a grocery list
- **Recipe**: Recipe storage with ingredients and instructions
