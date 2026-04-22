# 🏗️ Project Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Lovable)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React Components                                    │  │
│  │  ├─ MolecularBindingDashboard (Main)               │  │
│  │  ├─ ChEMBLViewer                                    │  │
│  │  ├─ PDBBindViewer                                   │  │
│  │  └─ AffinityPredictor                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓ HTTP Requests                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    http://localhost:8000
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Endpoints:                                           │  │
│  │ GET  /              (health check)                  │  │
│  │ GET  /stats         (system info)                   │  │
│  │ GET  /chembl        (visualize molecules)           │  │
│  │ GET  /pdbbind       (visualize ligands)             │  │
│  │ POST /predict       (single prediction)             │  │
│  │ POST /batch-predict (multiple predictions)          │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│        ┌─────────────────┼─────────────────┐               │
│        ↓                 ↓                 ↓                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Data Loading │  │ Visualization │  │ ML Inference │     │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤     │
│  │ • ChEMBL     │  │ • RDKit      │  │ • GIN Model  │     │
│  │ • PDBBind    │  │ • PNG images │  │ • PyTorch    │     │
│  │ • CSV files  │  │ • Base64     │  │ • GPU/CPU    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│        ↓                 ↓                 ↓                │
└────────────────────────────────────────────────────────────┘
        ↓                 ↓                 ↓
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ Dataset    │  │ R results  │  │ Predictions│
    │ Files      │  │ (PNG)      │  │ (pKd)      │
    └────────────┘  └────────────┘  └────────────┘
```

---

## Data Flow Diagrams

### Flow 1: Visualize ChEMBL Molecules
```
User clicks button
      ↓
Frontend: GET /chembl?count=8
      ↓
Backend:
  1. Load chembl_36_chemreps.txt
  2. Parse first 500 rows
  3. Convert SMILES to RDKit molecules
  4. Draw 8×1 grid of molecules
  5. Convert PNG to base64
      ↓
Return: {
  "success": true,
  "image": "base64_png_data",
  "smiles": [...],
  "source": "ChEMBL 36"
}
      ↓
Frontend displays: <img src="data:image/png;base64,...">
```

### Flow 2: Make a Prediction
```
User enters SMILES: CC(=O)Oc1ccccc1C(=O)O
User clicks "Predict"
      ↓
Frontend: POST /predict
{
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "name": "Aspirin"
}
      ↓
Backend:
  1. Parse SMILES string
  2. Convert to RDKit molecule
  3. Convert molecule to PyG graph:
     ├─ Nodes: Atomic number, degree, charge...
     ├─ Edges: Bond connections
     └─ 6 features per atom
  4. Load trained GIN model
  5. Run inference:
     ├─ Forward pass through 2 GIN convolution layers
     ├─ Global pooling
     └─ Output pKd prediction
  6. Generate 2D structure image
  7. Encode everything to base64
      ↓
Return: {
  "success": true,
  "molecule_name": "Aspirin",
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "predicted_affinity_pKd": 5.234,
  "molecule_image": "base64_png_data",
  "interpretation": "Predicted binding strength: 5.23"
}
      ↓
Frontend displays:
├─ Molecule structure (image)
├─ pKd: 5.234
├─ SMILES
└─ Download button
```

### Flow 3: Batch Predictions
```
User enters 3 molecules
      ↓
Frontend: POST /batch-predict
{
  "molecules": [
    {"smiles": "CCO", "name": "Ethanol"},
    {"smiles": "CC(=O)O", "name": "Acetic Acid"},
    {"smiles": "CN1C=NC2...", "name": "Caffeine"}
  ]
}
      ↓
Backend:
  1. Validate all SMILES
  2. Convert all to graphs
  3. Batch them together
  4. Single model forward pass (EFFICIENT!)
  5. Return all predictions
      ↓
Return: {
  "success": true,
  "predictions": [
    {"name": "Ethanol", "valid": true, "predicted_affinity_pKd": 2.145},
    {"name": "Acetic Acid", "valid": true, "predicted_affinity_pKd": 3.876},
    {"name": "Caffeine", "valid": true, "predicted_affinity_pKd": 6.234}
  ]
}
      ↓
Frontend displays: Table with all predictions
```

---

## Model Architecture (GIN)

```
INPUT: Molecular Graph
├─ Nodes (atoms):
│  └─ 6 features each: [atomic_num, degree, charge, hybrid, aromatic, h_count]
└─ Edges (bonds):
   └─ Connection matrix

      ↓
   
GIN Layer 1 (127 nodes → 128 features):
├─ MLPConv1:
│  ├─ Linear(6 → 128)
│  ├─ ReLU
│  ├─ Linear(128 → 128)
│  └─ Apply to graph neighbors
└─ Aggregate neighbor information

      ↓

ReLU Activation

      ↓

GIN Layer 2 (128 nodes → 128 features):
├─ MLPConv2:
│  ├─ Linear(128 → 128)
│  ├─ ReLU
│  ├─ Linear(128 → 128)
│  └─ Apply to graph neighbors
└─ Aggregate neighbor information

      ↓

ReLU Activation

      ↓

Global Pooling (average all node features):
└─ [128 features] → Single vector per molecule

      ↓

MLP Head (classification to pKd):
├─ Linear(128 → 64)
├─ ReLU
└─ Linear(64 → 1)  ← Binding affinity prediction

      ↓

OUTPUT: pKd value (continuous, float)
       Range: typically 2-12
       Higher = Stronger binding
```

---

## Technology Stack

### Frontend (Lovable)
```
React 18
├─ JSX/TSX components
├─ Hooks (useState, useEffect)
└─ Fetch API for HTTP requests

Tailwind CSS
├─ Responsive design
├─ Color utilities
└─ Flex/Grid layout

Lucide Icons
└─ UI icons (Loader, AlertCircle, Download)

shadcn/ui Components (optional)
└─ Tabs for navigation
```

### Backend (FastAPI/Python)
```
Python 3.10+
├─ FastAPI web framework
├─ Uvicorn ASGI server
└─ Pydantic for validation

Scientific Computing:
├─ PyTorch (neural networks)
├─ PyTorch Geometric (graph NN)
├─ RDKit (chemistry)
├─ Pandas (data loading)
├─ NumPy (numerical operations)
└─ Matplotlib (visualization)

Other:
├─ Pillow (image processing)
├─ Base64 encoding
├─ CORS middleware
└─ JSON serialization
```

---

## Data Flow: Complete Example

### User Action: "Predict Aspirin Binding"

```
STEP 1: User Interface (Lovable Frontend)
────────────────────────────────────
Name input field: "Aspirin"
SMILES input: "CC(=O)Oc1ccccc1C(=O)O"
Button: "Predict Affinity"

STEP 2: HTTP Request
────────────────────
POST http://localhost:8000/predict
Content-Type: application/json
Body: {
  "name": "Aspirin",
  "smiles": "CC(=O)Oc1ccccc1C(=O)O"
}

STEP 3: Backend Processing
──────────────────────────
Parse JSON ✓
│
Validate SMILES ✓
│
rdkit.Chem.MolFromSmiles()
├─ Parse: CC(=O)Oc1ccccc1C(=O)O
└─ Result: RDKit Mol object
  
Convert to Graph ✓
├─ Extract atoms: C, C, O, O, ...
├─ For each atom:
│  ├─ Atomic number: 6 (Carbon)
│  ├─ Degree: 2
│  ├─ Formal charge: 0
│  ├─ Hybridization: sp2
│  ├─ Aromatic: False
│  └─ Hydrogen count: 0
├─ Feature vector: [6, 2, 0, 2, 0, 0]
├─ Extract bonds: C-C, C-O, ...
└─ Create edge list

Create PyG Data object ✓
├─ x: Node features (21 atoms × 6 features)
├─ edge_index: Edge connections (2D tensor)
└─ batch: Which graph (0, for single)

Load GIN Model ✓
├─ Model: GINModel(in=6, hidden=128, out=1)
├─ Weights: final_model_trained.pt
└─ Device: GPU or CPU

Inference ✓
├─ Forward pass:
│  ├─ GINConv Layer 1 (21 atoms → 128 features each)
│  ├─ ReLU
│  ├─ GINConv Layer 2 (128 → 128 features)
│  ├─ ReLU
│  ├─ Global pooling (128-dim vector)
│  └─ Dense layers → pKd value
├─ Result: tensor(5.234)
└─ Extract: 5.234

Visualize Molecule ✓
├─ rdkit.Chem.AllChem.Compute2DCoords(mol)
├─ rdkit.Chem.Draw.MolToImage(mol)
├─ PIL Image object
├─ Save to BytesIO buffer
└─ base64.b64encode()

Create Response ✓
{
  "success": true,
  "molecule_name": "Aspirin",
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "predicted_affinity_pKd": 5.234,
  "molecule_image": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "interpretation": "Predicted binding strength: 5.23 pKd/pKi"
}

STEP 4: HTTP Response
─────────────────────
Status: 200 OK
Content-Type: application/json
Body: {full response above}

STEP 5: Frontend Display
────────────────────────
Parse JSON ✓
│
Update state ✓
│
Render components:
├─ <img src="data:image/png;base64,..." />
├─ <div>Aspirin</div>
├─ <div className="text-3xl">5.234</div>
├─ <code>CC(=O)Oc1ccccc1C(=O)O</code>
└─ <button onClick={handleDownload}>Download</button>

STEP 6: User Sees
──────────────────
✓ Molecule structure (2D image)
✓ Predicted pKd: 5.234
✓ SMILES notation
✓ Can download image
```

---

## Understanding pKd (Output Metric)

```
pKd = -log10(Kd)

Where Kd = Dissociation constant (in Molar)

Example:
  Kd = 10^-5 M → pKd = 5.0 (moderate binding)
  Kd = 10^-9 M → pKd = 9.0 (strong binding)
  Kd = 10^-12 M → pKd = 12.0 (very strong binding)

Scale:
  ├─ pKd < 3: Very weak binding
  ├─ pKd 3-5: Weak binding
  ├─ pKd 5-7: Moderate binding
  ├─ pKd 7-9: Strong binding
  └─ pKd > 9: Very strong binding

What the model predicts:
  Your trained GIN model outputs a single float
  This float represents the predicted pKd value
  Higher = stronger binding
```

---

## Error Handling Flow

```
User inputs invalid SMILES: "INVALID_SMILES"
      ↓
Frontend: POST /predict {"smiles": "INVALID_SMILES"}
      ↓
Backend:
  rdkit.Chem.MolFromSmiles("INVALID_SMILES")
  └─ Returns: None (invalid molecule)
      ↓
  if result is None:
    raise HTTPException(status_code=400, detail="Invalid SMILES string")
      ↓
  Response: 
  {
    "detail": "Invalid SMILES string"
  }
      ↓
Frontend:
  if (!response.ok):
    setError(response.detail)
      ↓
Display: "Error: Invalid SMILES string"
```

---

## Performance Characteristics

```
Operation Timing (approximate):
├─ Load model: 500ms (one-time on startup)
├─ Parse SMILES: 5-50ms
├─ Convert to graph: 10-50ms
├─ GNN inference: 10-50ms (CPU) / <5ms (GPU)
├─ Draw image: 50-200ms
└─ Total prediction: 100-400ms (typical)

Batch Processing (efficient):
├─ Single prediction: 1 mol → 200ms
├─ 10 predictions: 10 mol → 250ms (batched)
├─ 100 predictions: 100 mol → 350ms (batched)
└─ Speedup: ~4-10x for large batches

Memory Usage:
├─ Model weights: ~5MB
├─ Per prediction: <1MB
├─ Can handle large batches efficiently
```

---

## Integration Points

### Frontend ↔ Backend Communication

```json
REQUEST (Frontend → Backend):
POST /predict
{
  "smiles": "string",
  "name": "string"
}

RESPONSE (Backend → Frontend):
200 OK
{
  "success": true,
  "molecule_name": "string",
  "smiles": "string",
  "predicted_affinity_pKd": float,
  "molecule_image": "base64_string",
  "interpretation": "string"
}

ERROR:
{
  "detail": "error message"
}
```

---

## Deployment Architecture

### Local Development
```
Your Computer:
├─ Terminal 1: python main.py (Backend on port 8000)
├─ Terminal 2: npm run dev (Frontend on port 3000)
└─ Browser: http://localhost:3000
```

### Production Deployment
```
Cloud (Render/Railway):
├─ Frontend (Lovable): Hosted on Lovable platform
├─ Backend Server: Deployed containerized API
│  ├─ Python 3.10
│  ├─ All dependencies installed
│  ├─ Model weights loaded
│  └─ Running on public URL
└─ Data: Datasets in container or mounted
```

---

## Summary Metrics

| Metric | Value |
|--------|-------|
| **API Endpoints** | 6 total |
| **Model Type** | Graph Isomorphism Network |
| **Input Features** | 6 per atom |
| **Hidden Channels** | 128 |
| **Model Layers** | 2 GNN convs + MLP head |
| **Output** | 1 float (pKd prediction) |
| **Prediction Time** | 100-400ms |
| **Batch Capable** | Yes |
| **GPU Support** | Auto-detected |
| **CORS Enabled** | Yes |
| **Base64 Images** | Yes (embedded) |

---

**This architecture is scalable, production-ready, and optimized for both single and batch predictions!**
