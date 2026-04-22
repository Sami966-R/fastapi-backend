# Molecular Binding Affinity Predictor - Frontend Integration Guide

## 🚀 Quick Start

### 1. **Start the Backend**
```bash
cd c:\Users\Samiullah\Documents\backend
pip install -r requirements.txt
python main.py
```

Server runs at `http://localhost:8000`

### 2. **API Endpoints**

#### Get ChEMBL Molecules
```
GET http://localhost:8000/chembl?count=8
```
**Response:**
```json
{
  "success": true,
  "count": 8,
  "image": "base64_encoded_png...",
  "smiles": ["CC(=O)Oc1ccccc1C(=O)O", ...],
  "source": "ChEMBL 36"
}
```

#### Get PDBBind Ligands
```
GET http://localhost:8000/pdbbind?count=8
```
**Response:**
```json
{
  "success": true,
  "count": 8,
  "image": "base64_encoded_png...",
  "pdb_ids": ["1a30", "10gs", ...],
  "source": "PDBBind v2013"
}
```

#### Predict Binding Affinity (Single)
```
POST http://localhost:8000/predict
Content-Type: application/json

{
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "name": "Aspirin"
}
```
**Response:**
```json
{
  "success": true,
  "molecule_name": "Aspirin",
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "predicted_affinity_pKd": 5.234,
  "molecule_image": "base64_encoded_png...",
  "interpretation": "Predicted binding strength: 5.23 pKd/pKi"
}
```

#### Batch Predictions
```
POST http://localhost:8000/batch-predict
Content-Type: application/json

{
  "molecules": [
    {"smiles": "CCO", "name": "Ethanol"},
    {"smiles": "CC(=O)O", "name": "Acetic Acid"}
  ]
}
```

#### Get System Stats
```
GET http://localhost:8000/stats
```

---

## 📱 Lovable React Components

### Component 1: ChEMBL Visualizer
```jsx
'use client';
import { useState } from 'react';
import { AlertCircle, Loader } from 'lucide-react';

export function ChEMBLViewer() {
  const [image, setImage] = useState(null);
  const [smiles, setSmiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchChEMBL = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/chembl?count=8`);
      if (!response.ok) throw new Error('Failed to fetch ChEMBL data');
      
      const data = await response.json();
      if (data.success) {
        setImage(`data:image/png;base64,${data.image}`);
        setSmiles(data.smiles);
      } else {
        setError(data.detail || 'Unknown error');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">ChEMBL Molecules</h2>
      
      <button
        onClick={fetchChEMBL}
        disabled={loading}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 mb-4"
      >
        {loading ? (
          <>
            <Loader className="inline mr-2 animate-spin" size={18} />
            Loading...
          </>
        ) : (
          'Load ChEMBL Molecules'
        )}
      </button>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg mb-4 text-red-700">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {image && (
        <div className="space-y-4">
          <img src={image} alt="ChEMBL Molecules" className="w-full border rounded-lg" />
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-2">SMILES Strings:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {smiles.map((s, i) => (
                <code key={i} className="text-sm p-2 bg-white border rounded break-all">
                  {s}
                </code>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Component 2: PDBBind Visualizer
```jsx
'use client';
import { useState } from 'react';
import { AlertCircle, Loader } from 'lucide-react';

export function PDBBindViewer() {
  const [image, setImage] = useState(null);
  const [pdbIds, setPdbIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchPDBBind = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/pdbbind?count=8`);
      if (!response.ok) throw new Error('Failed to fetch PDBBind data');
      
      const data = await response.json();
      if (data.success) {
        setImage(`data:image/png;base64,${data.image}`);
        setPdbIds(data.pdb_ids);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">PDBBind Ligands</h2>
      
      <button
        onClick={fetchPDBBind}
        disabled={loading}
        className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 mb-4"
      >
        {loading ? (
          <>
            <Loader className="inline mr-2 animate-spin" size={18} />
            Loading...
          </>
        ) : (
          'Load PDBBind Ligands'
        )}
      </button>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg mb-4 text-red-700">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {image && (
        <div className="space-y-4">
          <img src={image} alt="PDBBind Ligands" className="w-full border rounded-lg" />
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-2">PDB IDs:</h3>
            <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
              {pdbIds.map((id, i) => (
                <span key={i} className="text-center p-2 bg-white border rounded font-mono">
                  {id}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Component 3: Binding Affinity Predictor
```jsx
'use client';
import { useState } from 'react';
import { AlertCircle, Loader, Download } from 'lucide-react';

export function AffinityPredictor() {
  const [smiles, setSmiles] = useState('');
  const [name, setName] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const predictAffinity = async () => {
    if (!smiles.trim()) {
      setError('Please enter a SMILES string');
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);
    setImage(null);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          smiles: smiles.trim(),
          name: name || 'Molecule'
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Prediction failed');
      }

      const data = await response.json();
      if (data.success) {
        setPrediction(data);
        setImage(`data:image/png;base64,${data.molecule_image}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (image) {
      const link = document.createElement('a');
      link.href = image;
      link.download = `${name || 'molecule'}.png`;
      link.click();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Predict Binding Affinity</h2>

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Molecule Name (Optional)
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Aspirin"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            SMILES String *
          </label>
          <textarea
            value={smiles}
            onChange={(e) => setSmiles(e.target.value)}
            placeholder="Enter SMILES notation, e.g., CC(=O)Oc1ccccc1C(=O)O"
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono"
          />
        </div>

        <button
          onClick={predictAffinity}
          disabled={loading}
          className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 font-medium"
        >
          {loading ? (
            <>
              <Loader className="inline mr-2 animate-spin" size={18} />
              Predicting...
            </>
          ) : (
            'Predict Affinity'
          )}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg mb-4 text-red-700">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {prediction && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {image && (
              <div>
                <h3 className="font-semibold mb-3">Molecule Structure</h3>
                <img src={image} alt="Molecule" className="w-full border rounded-lg" />
                <button
                  onClick={handleDownload}
                  className="mt-2 w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center justify-center gap-2"
                >
                  <Download size={18} />
                  Download Image
                </button>
              </div>
            )}

            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-sm text-gray-600 mb-1">Molecule Name</p>
                <p className="text-xl font-bold text-gray-800">{prediction.molecule_name}</p>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-gray-600 mb-1">Predicted Binding Affinity</p>
                <p className="text-3xl font-bold text-blue-600">{prediction.predicted_affinity_pKd}</p>
                <p className="text-xs text-gray-600 mt-1">pKd/pKi (Higher ≈ Stronger Binding)</p>
              </div>

              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <p className="text-sm text-gray-600 mb-1">Interpretation</p>
                <p className="text-gray-700">{prediction.interpretation}</p>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">SMILES</p>
                <code className="text-xs block p-3 bg-white border rounded overflow-auto break-all">
                  {prediction.smiles}
                </code>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Component 4: Combined Dashboard
```jsx
'use client';
import { ChEMBLViewer } from './ChEMBLViewer';
import { PDBBindViewer } from './PDBBindViewer';
import { AffinityPredictor } from './AffinityPredictor';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function MolecularBindingDashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-gray-900">
          Molecular Binding Affinity Predictor
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Powered by Graph Isomorphism Networks (GIN)
        </p>

        <Tabs defaultValue="predict" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="predict">Predict</TabsTrigger>
            <TabsTrigger value="chembl">ChEMBL</TabsTrigger>
            <TabsTrigger value="pdbbind">PDBBind</TabsTrigger>
          </TabsList>

          <TabsContent value="predict">
            <AffinityPredictor />
          </TabsContent>

          <TabsContent value="chembl">
            <ChEMBLViewer />
          </TabsContent>

          <TabsContent value="pdbbind">
            <PDBBindViewer />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
```

---

## 🔧 Environment Configuration

Create a `.env.local` file in your Lovable project:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production deployment:
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

---

## 🚢 Production Deployment

### Option 1: Deploy Backend to Render
1. Push your backend folder to GitHub
2. Create new project on [render.com](https://render.com)
3. Set `Start Command`: `pip install -r requirements.txt && python main.py`
4. Update `NEXT_PUBLIC_API_URL` in Lovable

### Option 2: Deploy Backend to Railway
1. Push to GitHub
2. Create project on [railway.app](https://railway.app)
3. Connect and deploy automatically
4. Get your public URL and update `.env.local`

### Option 3: Docker Deployment
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## ✅ Testing

### Test ChEMBL endpoint:
```bash
curl http://localhost:8000/chembl
```

### Test Prediction:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles":"CCO","name":"Ethanol"}'
```

### Check System Stats:
```bash
curl http://localhost:8000/stats
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Run `pip install -r requirements.txt` |
| CORS errors | Check backend CORS settings (should allow all origins) |
| No model found | Train model in Colab and download `final_model_trained.pt` |
| Port 8000 in use | `python main.py --port 8001` |
| SMILES rejected | Validate SMILES on [SMILES Parser](https://www.meta-sequence.com/) |

---

## 📊 Example SMILES Strings for Testing

- Aspirin: `CC(=O)Oc1ccccc1C(=O)O`
- Caffeine: `CN1C=NC2=C1C(=O)N(C(=O)N2C)C`
- Ethanol: `CCO`
- Ibuprofen: `CC(C)Cc1ccc(cc1)C(C)C(=O)O`

