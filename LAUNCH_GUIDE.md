# IMPORTANT
#### If you are running this on a windows machine, please navigate to cs362-grocery-list-project/package.json
#### From there, please change this line:
```bash
"backend": "cd lettuceSave && ./venv/bin/python manage.py runserver 8001",
```
### To:
```bash
"backend": "cd lettuceSave && venv\\Scripts\\python manage.py runserver 8001",
```

## Getting Started

### 1. Navigate to the main folder & frontend folder to install dependencies
```bash
cd cs362-grocery-list-project
rm -rf node_modules
rm package-lock.json
npm install
cd frontend
npm install
```

### 2. Activate the virtual environment
```bash
cd ../lettuceSave
python -m venv venv
```
**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install remaining dependencies
```bash
pip install -r requirements.txt
python manage.py migrate
```

### 4. Launch site!
```bash
cd ..
npm run dev
```

