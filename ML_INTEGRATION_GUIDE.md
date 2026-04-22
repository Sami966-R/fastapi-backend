# ML Backend to Frontend Integration Guide

## Overview

This guide explains how to integrate your machine learning backend with the Lovable frontend to create a complete ML dashboard application.

## Architecture

```
┌─────────────────────┐
│   Jupyter Notebook  │
│  (final_BE.ipynb)   │
│  - Training         │
│  - Evaluation       │
└──────────┬──────────┘
           │
           │ Results extraction
           ▼
┌─────────────────────┐
│  ml_results.json    │
│  - Metrics          │
│  - Charts data      │
│  - Predictions      │
└──────────┬──────────┘
           │
           │ Read by API
           ▼
┌────────────────────────┐
│   FastAPI Backend      │
│  /ml-dashboard/* endpoints
│  - Classification metrics
│  - Training curves
│  - Error distribution
│  - Model comparison
└──────────┬─────────────┘
           │
           │ HTTP/JSON
           ▼
┌─────────────────────┐
│  Lovable Frontend   │
│  React Dashboard    │
│  - Charts           │
│  - Metrics cards    │
│  - Visualizations   │
└─────────────────────┘
```

---

## Step 1: Extract Results from Notebook

### Option A: Manual Extraction (Recommended for first run)

After your notebook finishes training, extract the key metrics:

```python
from ml_results_extractor import MLResultsExtractor
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error

# Create extractor
extractor = MLResultsExtractor()

# Add classification metrics (for each model you trained)
extractor.add_classification_metrics(
    model_name='Random Forest',
    train_acc=94.2,
    test_acc=89.1,
    metrics={
        'mae': 0.42,
        'rmse': 0.58,
        'r2': 0.89
    }
)

# Add training curves
extractor.add_training_curve(
    train_losses=train_losses_list,  # From your training loop
    val_losses=val_losses_list        # From your training loop
)

# Add error distribution
y_train_true, y_train_pred = get_predictions(train_loader, model)
y_test_true, y_test_pred = get_predictions(test_loader, model)
train_errors = y_train_true - y_train_pred
test_errors = y_test_true - y_test_pred

extractor.add_error_distribution(train_errors, test_errors)

# Add model comparison radar data
extractor.add_model_comparison({
    'Random Forest': (0.94, 0.8, 0.92),   # (accuracy, speed, precision)
    'SVM': (0.92, 0.7, 0.90),
    'Gradient Boost': (0.96, 0.75, 0.95),
    'Neural Network': (0.97, 0.6, 0.96)
})

# Add actual vs predicted
extractor.add_actual_vs_predicted(y_test_true, y_test_pred)

# Add test metrics
r2 = r2_score(y_test_true, y_test_pred)
rmse = np.sqrt(mean_squared_error(y_test_true, y_test_pred))
mae = np.mean(np.abs(y_test_true - y_test_pred))
extractor.add_test_set_metrics(r2, rmse, mae)

# Save to JSON
results_json = extractor.to_json('ml_results.json')
print("Results saved!")
```

### Option B: Automatic Extraction from Final Notebook Cells

Add this cell at the end of `final_BE.ipynb`:

```python
# Extract all results to JSON for frontend
import sys
sys.path.append('.')

from ml_results_extractor import MLResultsExtractor
import json

# Initialize extractor
extractor = MLResultsExtractor()

# Fill in your metrics from training
extractor.add_classification_metrics('Your Model', train_acc, test_acc, metrics_dict)
extractor.add_training_curve(train_losses, val_losses)
extractor.add_error_distribution(train_errors, test_errors)
extractor.add_model_comparison(model_comparison_dict)
extractor.add_actual_vs_predicted(y_test_true, y_test_pred)
extractor.add_test_set_metrics(r2_score, rmse, mae)

# Save results
extractor.to_json('ml_results.json')
print("✅ ML Results exported to ml_results.json")
```

---

## Step 2: Verify Backend Setup

### Check that ml_results.json is accessible:

```bash
# From backend directory
python -c "from ml_results_extractor import create_sample_results; import json; results = create_sample_results(); f = open('ml_results.json', 'w'); json.dump(results, f); print('Sample results generated')"
```

### Test the API endpoints:

```bash
# Terminal 1: Start the backend
python main.py

# Terminal 2: Test endpoints
curl http://localhost:8000/ml-dashboard/results
curl http://localhost:8000/ml-dashboard/classification-metrics
curl http://localhost:8000/ml-dashboard/training-curve
curl http://localhost:8000/ml-dashboard/error-distribution
curl http://localhost:8000/ml-dashboard/model-comparison
curl http://localhost:8000/ml-dashboard/actual-vs-predicted
curl http://localhost:8000/ml-dashboard/test-metrics
```

Expected responses should be JSON with `success: true` and the data.

---

## Step 3: Frontend Setup with Lovable

### 3.1 Create Frontend Project

Use this prompt in Lovable:

```
Create a React TypeScript dashboard application with the following requirements:

## Project Specifications

**Name:** Molecular Binding Affinity ML Dashboard
**Framework:** React 18+ with TypeScript
**Styling:** Tailwind CSS + shadcn/ui
**Charts:** Recharts library

## Pages Required

### 1. Classical ML Benchmarking Page
- Header with title and description
- 4 metric cards showing Random Forest, SVM, Gradient Boost, and Neural Network results
- Each card displays: Train Acc, Test Acc, MAE, RMSE, R² Score
- Grouped bar chart comparing accuracy across models
- Radar chart comparing model performance dimensions

### 2. Results Dashboard Page
- Actual vs Predicted scatter plot
- Model Comparison bar chart (R² scores)
- Error Distribution histogram
- Training & Validation Loss line chart
- All charts should be responsive and interactive

## Data Integration

API Base URL: http://localhost:8000 (or environment variable)

Fetch data from these endpoints:
- GET /ml-dashboard/classification-metrics
- GET /ml-dashboard/training-curve
- GET /ml-dashboard/error-distribution
- GET /ml-dashboard/model-comparison
- GET /ml-dashboard/actual-vs-predicted
- GET /ml-dashboard/test-metrics

## Features
- Error handling and loading states
- TypeScript interfaces for all API responses
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Navigation between pages
- Data caching to reduce API calls
```

### 3.2 Configure API Base URL

Create a `.env.local` file in your frontend project:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

For production, update to your deployed backend URL:

```env
REACT_APP_API_BASE_URL=https://your-backend-domain.com
```

### 3.3 Add TypeScript Interfaces

Create `src/types/ml-dashboard.ts`:

```typescript
export interface ClassificationMetrics {
  train_accuracy: number;
  test_accuracy: number;
  mae: number;
  rmse: number;
  r2: number;
}

export interface TrainingCurve {
  epochs: number;
  train_losses: number[];
  val_losses: number[];
  final_train_loss: number;
  final_val_loss: number;
}

export interface HistogramData {
  counts: number[];
  bins: number[];
  mean: number;
  std: number;
}

export interface ErrorDistribution {
  train_set: HistogramData;
  test_set: HistogramData;
  zero_error_line: number;
}

export interface ModelComparison {
  accuracy: number;
  speed: number;
  precision: number;
  f1_score: number;
}

export interface ActualVsPredicted {
  actual: number[];
  predicted: number[];
  count: number;
  correlation: number;
}

export interface TestMetrics {
  r2_score: number;
  rmse: number;
  mae: number;
  description: string;
}
```

---

## Step 4: Jupyter Notebook Integration

### Extract Results from final_BE.ipynb

Add this to a new cell at the end of your notebook:

```python
# =================== EXPORT RESULTS FOR FRONTEND ===================

# Copy this to your final notebook cell to export results

import sys
import json
from datetime import datetime

# Add project root to path
if '.' not in sys.path:
    sys.path.insert(0, '.')

from ml_results_extractor import MLResultsExtractor

# Get your test predictions
y_test_true, y_test_pred = get_predictions(test_loader, model)  # From your training code

# Calculate metrics
r2 = r2_score(y_test_true, y_test_pred)
rmse = np.sqrt(mean_squared_error(y_test_true, y_test_pred))
mae = np.mean(np.abs(y_test_true - y_test_pred))

# Get errors for distribution
train_errors = y_train_true - y_train_pred
test_errors = y_test_true - y_test_pred

# Create extractor
extractor = MLResultsExtractor()

# Add all metrics
# Note: Replace values with your actual training results
extractor.add_classification_metrics(
    'Random Forest', 94.2, 89.1, 
    {'mae': 0.42, 'rmse': 0.58, 'r2': 0.89}
)
extractor.add_classification_metrics(
    'SVM', 91.8, 86.3,
    {'mae': 0.51, 'rmse': 0.67, 'r2': 0.85}
)
extractor.add_classification_metrics(
    'Gradient Boost', 96.1, 91.4,
    {'mae': 0.35, 'rmse': 0.48, 'r2': 0.92}
)
extractor.add_classification_metrics(
    'Neural Network', 97.3, 90.8,
    {'mae': 0.38, 'rmse': 0.52, 'r2': 0.91}
)

# Add training curves
extractor.add_training_curve(train_losses, val_losses)

# Add error distribution
extractor.add_error_distribution(train_errors, test_errors)

# Add model comparison
extractor.add_model_comparison({
    'Random Forest': (0.942, 0.8, 0.91),
    'SVM': (0.918, 0.7, 0.86),
    'Gradient Boost': (0.961, 0.75, 0.95),
    'Neural Network': (0.973, 0.6, 0.96)
})

# Add actual vs predicted
extractor.add_actual_vs_predicted(y_test_true, y_test_pred)

# Add test metrics
extractor.add_test_set_metrics(r2, rmse, mae)

# Save to JSON file
results_json = extractor.to_json('ml_results.json')

print("✅ Results exported successfully!")
print(f"Timestamp: {extractor.timestamp}")
print(f"Models: {len(extractor.results.get('classification_metrics', {}))} models")
print(f"Epochs: {extractor.results.get('training_curve', {}).get('epochs', 0)}")
```

---

## Step 5: Running the Complete Stack

### Terminal 1: Start Backend

```bash
cd backend
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Frontend

```bash
cd frontend
npm start
# or
yarn start
```

Expected output:
```
Compiled successfully!
You can now view molecular-binding-dashboard in the browser.
http://localhost:3000
```

### Terminal 3: Run Notebook (Optional)

```bash
jupyter notebook final_BE.ipynb
```

Run all cells to generate fresh `ml_results.json`

---

## Step 6: Verify Integration

### Check if everything works:

1. **Backend Health**
   ```bash
   curl http://localhost:8000/
   ```
   Should return API endpoints info

2. **ML Dashboard Endpoints**
   ```bash
   curl http://localhost:8000/ml-dashboard/results
   ```
   Should return ML results with data

3. **Frontend Loading**
   - Navigate to http://localhost:3000
   - Should see dashboard pages
   - Charts should populate with data from API

4. **Browser Console**
   - No CORS errors
   - No 404 errors
   - Network tab shows API calls succeeding

---

## Deployment Guide

### Deploy Backend

#### Option 1: Railway (Recommended)

1. Ensure `Procfile` contains:
   ```
   web: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. Connect to Railway and deploy:
   ```bash
   railway link
   railway up
   ```

3. Get the public URL from Railway dashboard

#### Option 2: Heroku

```bash
heroku create molecular-binding-api
git push heroku main
heroku logs --tail
```

#### Option 3: Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Deploy Frontend

#### Option 1: Vercel (Recommended)

```bash
vercel deploy --prod
```

#### Option 2: Netlify

```bash
npm run build
netlify deploy --prod --dir=build
```

#### Option 3: GitHub Pages

```bash
npm run build
# Push build/ to gh-pages branch
```

### Update Environment Variables

Update frontend `.env` with production backend URL:

```env
REACT_APP_API_BASE_URL=https://your-backend.railway.app
```

---

## Troubleshooting

### CORS Issues

If you get CORS errors from frontend:

1. **Backend already configured** to allow all origins (for development)

2. **For production**, update CORS in `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],
       allow_methods=["GET", "POST", "OPTIONS"],
       allow_headers=["*"],
   )
   ```

### API Returns Empty Data

**Check if `ml_results.json` exists:**

```bash
ls -la ml_results.json
```

**If not, generate sample data:**

```bash
python -c "from ml_results_extractor import create_sample_results; import json; f=open('ml_results.json','w'); json.dump(create_sample_results(), f); print('Sample data generated')"
```

### Charts Not Rendering

1. Check browser console for errors
2. Verify data structure matches TypeScript interfaces
3. Ensure Recharts library is installed: `npm install recharts`
4. Check API response format in Network tab

### Slow Loading

1. Implement response caching with SWR or React Query
2. Add loading skeletons while data fetches
3. Paginate large datasets
4. Use IndexedDB for local caching

---

## File Structure

```
project/
├── backend/
│   ├── main.py                    # FastAPI app with dashboard endpoints
│   ├── ml_results_extractor.py   # ML results extraction utility
│   ├── ml_results.json           # Generated ML results
│   ├── final_BE.ipynb            # Training notebook
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ClassicalMLBenchmarking.tsx
│   │   │   └── ResultsDashboard.tsx
│   │   ├── components/
│   │   │   ├── MetricsCard.tsx
│   │   │   ├── AccuracyChart.tsx
│   │   │   ├── RadarChart.tsx
│   │   │   ├── ScatterPlot.tsx
│   │   │   ├── HistogramChart.tsx
│   │   │   └── LineChart.tsx
│   │   ├── types/
│   │   │   └── ml-dashboard.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── ...
│   ├── .env.local
│   ├── package.json
│   └── ...
└── README.md
```

---

## Next Steps

1. ✅ Set up backend API endpoints
2. ✅ Create ML results extractor utility
3. ✅ Run Jupyter notebook to generate results
4. ✅ Start FastAPI backend
5. ✅ Use Lovable prompt to build frontend
6. ✅ Integration test both systems
7. ✅ Deploy to production

Your ML dashboard will now display all training metrics, visualizations, and model comparisons from your notebook!
