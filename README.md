# 🧬 Molecular Binding Affinity Predictor - Backend

A FastAPI-based REST API for predicting molecular binding affinity using Graph Isomorphism Networks (GIN). This backend works seamlessly with your Lovable frontend.

## 📋 Features

- ✅ **Single Molecule Prediction**: Predict binding affinity from SMILES notation
- ✅ **Batch Predictions**: Process multiple molecules at once
- ✅ **ChEMBL Integration**: Visualize molecules from ChEMBL dataset
- ✅ **PDBBind Integration**: Display ligands from PDBBind database
- ✅ **CORS Enabled**: Ready for frontend integration
- ✅ **GPU Support**: Automatic CUDA detection
- ✅ **Base64 Image Output**: Display molecular structures on frontend

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
cd c:\Users\Samiullah\Documents\backend
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
python main.py
```

Server runs at: `http://localhost:8000`

### Step 3: Test the API
```bash
python test_api.py
```

This will run comprehensive tests of all endpoints.

## 📊 API Documentation

### Available Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Health check & endpoint list |
| `GET` | `/stats` | System configuration & dataset info |
| `GET` | `/chembl` | Retrieve ChEMBL molecules |
| `GET` | `/pdbbind` | Retrieve PDBBind ligands |
| `POST` | `/predict` | Single molecule affinity prediction |
| `POST` | `/batch-predict` | Batch molecule predictions |

### Detailed Endpoint Docs

#### 1. GET `/` - Health Check
```bash
curl http://localhost:8000/
```
**Response:**
```json
{
  "status": "online",
  "api": "Molecular Binding Affinity Predictor",
  "endpoints": {...}
}
```

---

#### 2. GET `/stats` - System Information
```bash
curl http://localhost:8000/stats
```
**Response:**
```json
{
  "chembl": {
    "available": true,
    "file": "chembl_36_chemreps.txt"
  },
  "pdbbind": {
    "available": true,
    "path": "dataset/pbdbind/v2013-core",
    "ligand_count": 245
  },
  "model": {
    "type": "Graph Isomorphism Network (GIN)",
    "input_features": 6,
    "hidden_channels": 128,
    "output": "binding_affinity_pKd",
    "device": "cpu",
    "trained": true
  }
}
```

---

#### 3. GET `/chembl` - ChEMBL Molecules
```bash
curl "http://localhost:8000/chembl?count=8"
```

**Query Parameters:**
- `count` (optional): Number of molecules (default: 8)

**Response:**
```json
{
  "success": true,
  "count": 8,
  "image": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "smiles": [
    "CC(=O)Oc1ccccc1C(=O)O",
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    ...
  ],
  "source": "ChEMBL 36"
}
```

---

#### 4. GET `/pdbbind` - PDBBind Ligands
```bash
curl "http://localhost:8000/pdbbind?count=8"
```

**Query Parameters:**
- `count` (optional): Number of ligands (default: 8)

**Response:**
```json
{
  "success": true,
  "count": 8,
  "image": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "pdb_ids": ["1a30", "10gs", "1bcu", ...],
  "source": "PDBBind v2013"
}
```

---

#### 5. POST `/predict` - Single Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "name": "Aspirin"
  }'
```

**Request Body:**
```json
{
  "smiles": "string (required) - SMILES notation of molecule",
  "name": "string (optional) - Molecule name"
}
```

**Response:**
```json
{
  "success": true,
  "molecule_name": "Aspirin",
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "predicted_affinity_pKd": 5.234,
  "confidence": "Medium",
  "molecule_image": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "interpretation": "Predicted binding strength: 5.23 pKd/pKi"
}
```

---

#### 6. POST `/batch-predict` - Batch Predictions
```bash
curl -X POST http://localhost:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "molecules": [
      {"smiles": "CCO", "name": "Ethanol"},
      {"smiles": "CC(=O)O", "name": "Acetic Acid"},
      {"smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "name": "Caffeine"}
    ]
  }'
```

**Request Body:**
```json
{
  "molecules": [
    {
      "smiles": "string (required)",
      "name": "string (optional)"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "total_molecules": 3,
  "valid_molecules": 3,
  "predictions": [
    {
      "name": "Ethanol",
      "smiles": "CCO",
      "valid": true,
      "predicted_affinity_pKd": 2.145
    },
    {
      "name": "Acetic Acid",
      "smiles": "CC(=O)O",
      "valid": true,
      "predicted_affinity_pKd": 3.876
    },
    {
      "name": "Caffeine",
      "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
      "valid": true,
      "predicted_affinity_pKd": 6.234
    }
  ]
}
```

---

## 🔗 Connect with Lovable Frontend

See `LOVABLE_INTEGRATION.md` in this directory for complete React components and integration guide.

### Quick Setup:
1. Copy the React components from `LOVABLE_INTEGRATION.md`
2. Create `.env.local` in your Lovable project:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Import and use components in your pages

---

## 📦 Project Structure

```
backend/
├── main.py                      # FastAPI application
├── models.py                    # ML model definitions (empty, models in main.py)
├── utils.py                     # Utility functions (empty, utils in main.py)
├── requirements.txt             # Python dependencies
├── test_api.py                  # Test suite
├── LOVABLE_INTEGRATION.md       # Frontend integration guide
├── README.md                    # This file
└── dataset/
    ├── chembl_36_chemreps.txt   # ChEMBL dataset
    └── pbdbind/
        └── v2013-core/          # PDBBind molecules
```

---

## 🧪 Running Tests

```bash
python test_api.py
```

Expected output:
```
============================================================
🧪 Molecular Binding Affinity API - Test Suite
============================================================

🔍 Testing: Health Check...
✅ Server is running
   API: Molecular Binding Affinity Predictor

🔍 Testing: System Stats...
✅ Stats Endpoint:
   ChEMBL available: True
   PDBBind available: True
   Model type: Graph Isomorphism Network (GIN)
   Device: cpu

... (more tests)

📊 Results: 6 passed, 0 failed
============================================================

✨ All tests passed! Your API is ready for Lovable.
```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file (optional):
```env
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=1
```

### Advanced Startup Options
```bash
# Run with different port
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8001)"

# Run with auto-reload (development)
python -m uvicorn main:app --reload

# Run with multiple workers (production)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🚢 Production Deployment

### Option 1: Render.com (Recommended)
1. Push to GitHub
2. Create new service on [render.com](https://render.com)
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `python main.py`
5. Get public URL and update Lovable's `.env.local`

### Option 2: Railway.app
1. Push to GitHub
2. Create project on [railway.app](https://railway.app)
3. Connect repository - auto-deploys
4. Get public domain URL

### Option 3: Docker (Any Cloud)
Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t molecular-api .
docker run -p 8000:8000 molecular-api
```

### Option 4: Traditional VPS (AWS EC2, DigitalOcean, etc.)
```bash
# SSH into server
ssh user@your-server.com

# Install Python and dependencies
sudo apt-get update
sudo apt-get install python3.10 python3-pip

# Clone repo
git clone <your-repo>
cd backend

# Install requirements
pip install -r requirements.txt

# Run with PM2 (process manager)
npm install -g pm2
pm2 start main.py --name "molecular-api"
pm2 save
```

---

## 📊 Understanding the Model

### Architecture: Graph Isomorphism Network (GIN)
- **Input**: Molecular graphs with 6 node features per atom
  - Atomic number
  - Degree
  - Formal charge
  - Hybridization
  - Aromaticity
  - Hydrogen count

- **Layers**: 2 GNN convolution layers
- **Output**: Predicted binding affinity (pKd/pKi value)

### Training Data
- **Pre-training**: ChEMBL molecules (10,000+)
- **Fine-tuning**: PDBBind complexes with real experimental binding affinity

### Output Interpretation
- **pKd/pKi range**: 2 - 12
- **Higher values**: Stronger binding (lower dissociation constant)
- **Lower values**: Weaker binding (higher dissociation constant)

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### ModuleNotFoundError
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### CORS Issues
If frontend can't reach backend:
1. Ensure `CORS` middleware is enabled in `main.py` ✅
2. Check frontend's `NEXT_PUBLIC_API_URL` matches backend URL
3. Try opening `http://localhost:8000/` in browser

### RDKit Issues (Windows)
```bash
# Reinstall with conda
conda install -c conda-forge rdkit
```

### Model Not Found
1. Download trained weights from Colab Google Drive
2. Place `final_model_trained.pt` in backend root directory
3. Restart server

---

## 📚 Example SMILES Strings

Test these molecules:

| Molecule | SMILES |
|----------|--------|
| Aspirin | `CC(=O)Oc1ccccc1C(=O)O` |
| Caffeine | `CN1C=NC2=C1C(=O)N(C(=O)N2C)C` |
| Ibuprofen | `CC(C)Cc1ccc(cc1)C(C)C(=O)O` |
| Penicillin G | `CC(C)CC(NC(=O)C1CCCN1C(=O)C(C)(C)C(=O)O)C(=O)Nc2ccccc2` |
| Ethanol | `CCO` |
| Glucose | `C(C(C(C(C(=O)O)O)O)O)O` |

---

## 📞 Support

For issues or questions:
1. Check test output: `python test_api.py`
2. Review logs in terminal
3. Check Firebase/backend logs in production
4. Verify dataset files exist in `dataset/` directory

---

## 📝 License

This project is part of your FYP (Final Year Project). Modify as needed for your presentation and submission.

---

**Last Updated**: March 2025
**Status**: Production Ready ✅
