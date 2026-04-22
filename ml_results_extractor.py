"""
ML Results Extractor
Extracts ML metrics and results from the training pipeline
and formats them for frontend consumption
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os


class MLResultsExtractor:
    """Extract and format ML results for frontend"""
    
    def __init__(self):
        self.results = {}
        self.timestamp = datetime.now().isoformat()
    
    
    def add_classification_metrics(self, 
                                  model_name: str,
                                  train_acc: float,
                                  test_acc: float,
                                  metrics: Dict[str, float]) -> None:
        """
        Add classification model metrics
        
        Args:
            model_name: Name of the model (e.g., 'Random Forest', 'SVM')
            train_acc: Training accuracy (0-100)
            test_acc: Test accuracy (0-100)
            metrics: Dict with additional metrics like MAE, RMSE, R2
        """
        if 'classification_metrics' not in self.results:
            self.results['classification_metrics'] = {}
        
        self.results['classification_metrics'][model_name] = {
            'train_accuracy': float(round(train_acc, 2)),
            'test_accuracy': float(round(test_acc, 2)),
            'mae': float(round(metrics.get('mae', 0), 2)),
            'rmse': float(round(metrics.get('rmse', 0), 2)),
            'r2': float(round(metrics.get('r2', 0), 3))
        }
    
    
    def add_training_curve(self, 
                          train_losses: List[float],
                          val_losses: List[float],
                          epoch_range: Optional[int] = None) -> None:
        """
        Add training curve data
        
        Args:
            train_losses: List of training losses per epoch
            val_losses: List of validation losses per epoch
            epoch_range: Number of epochs to include
        """
        if epoch_range:
            train_losses = train_losses[:epoch_range]
            val_losses = val_losses[:epoch_range]
        
        self.results['training_curve'] = {
            'epochs': len(train_losses),
            'train_losses': [float(round(x, 4)) for x in train_losses],
            'val_losses': [float(round(x, 4)) for x in val_losses],
            'final_train_loss': float(round(train_losses[-1], 4)) if train_losses else 0,
            'final_val_loss': float(round(val_losses[-1], 4)) if val_losses else 0
        }
    
    
    def add_error_distribution(self,
                              train_errors: np.ndarray,
                              test_errors: np.ndarray,
                              bins: int = 30) -> None:
        """
        Add error distribution data for histograms
        
        Args:
            train_errors: Array of training errors
            test_errors: Array of test errors
            bins: Number of histogram bins
        """
        def get_histogram_data(errors, num_bins):
            counts, edges = np.histogram(errors, bins=num_bins, density=True)
            return {
                'counts': [float(c) for c in counts],
                'bins': [float(e) for e in edges[:-1]],
                'mean': float(np.mean(errors)),
                'std': float(np.std(errors))
            }
        
        self.results['error_distribution'] = {
            'train_set': get_histogram_data(train_errors, bins),
            'test_set': get_histogram_data(test_errors, bins),
            'zero_error_line': 0
        }
    
    
    def add_model_comparison(self, 
                            models: Dict[str, Tuple[float, float, float]]) -> None:
        """
        Add model comparison radar data
        
        Args:
            models: Dict with model_name -> (accuracy, speed, precision)
                   All values should be 0-1 or 0-100
        """
        comparison = {}
        for model_name, (accuracy, speed, precision) in models.items():
            comparison[model_name] = {
                'accuracy': float(round(accuracy, 3)),
                'speed': float(round(speed, 3)),
                'precision': float(round(precision, 3)),
                'f1_score': float(round((2 * accuracy * precision) / (accuracy + precision) if (accuracy + precision) > 0 else 0, 3))
            }
        
        self.results['model_comparison'] = comparison
    
    
    def add_actual_vs_predicted(self,
                               y_true: np.ndarray,
                               y_pred: np.ndarray,
                               limit: Optional[int] = None) -> None:
        """
        Add actual vs predicted values for scatter plot
        
        Args:
            y_true: True values
            y_pred: Predicted values
            limit: Max number of points to include
        """
        if limit:
            indices = np.random.choice(len(y_true), min(limit, len(y_true)), replace=False)
            y_true = y_true[indices]
            y_pred = y_pred[indices]
        
        self.results['actual_vs_predicted'] = {
            'actual': [float(y) for y in y_true],
            'predicted': [float(y) for y in y_pred],
            'count': len(y_true),
            'correlation': float(np.corrcoef(y_true, y_pred)[0, 1]) if len(y_true) > 1 else 0
        }
    
    
    def add_test_set_metrics(self,
                            r2_score: float,
                            rmse: float,
                            mae: float) -> None:
        """
        Add test set evaluation metrics
        
        Args:
            r2_score: R² Score (0-1)
            rmse: Root Mean Squared Error
            mae: Mean Absolute Error
        """
        self.results['test_set_metrics'] = {
            'r2_score': float(round(r2_score, 4)),
            'rmse': float(round(rmse, 4)),
            'mae': float(round(mae, 4)),
            'description': 'Test Set Evaluation Metrics'
        }
    
    
    def get_results(self) -> Dict:
        """Get all results as dictionary"""
        return {
            'timestamp': self.timestamp,
            'data': self.results
        }
    
    
    def to_json(self, filepath: Optional[str] = None) -> str:
        """
        Convert results to JSON string

        Args:
            filepath: Optional path to save JSON file

        Returns:
            JSON string
        """
        results = self.get_results()

        # Function to recursively convert numpy types to Python types
        def convert_numpy_types(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.float32, np.float64, np.float16)):
                return float(obj)
            elif isinstance(obj, (np.int32, np.int64, np.int16, np.int8)):
                return int(obj)
            elif isinstance(obj, (np.bool_)):
                return bool(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj

        # Convert all numpy types in results
        results = convert_numpy_types(results)

        json_str = json.dumps(results, indent=2)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
            print(f"Results saved to {filepath}")

        return json_str

def create_sample_results() -> Dict:
    """Create sample results for testing dashboard"""
    extractor = MLResultsExtractor()
    
    # Add classification metrics
    extractor.add_classification_metrics(
        'Random Forest',
        train_acc=94.2,
        test_acc=89.1,
        metrics={'mae': 0.42, 'rmse': 0.58, 'r2': 0.89}
    )
    extractor.add_classification_metrics(
        'SVM',
        train_acc=91.8,
        test_acc=86.3,
        metrics={'mae': 0.51, 'rmse': 0.67, 'r2': 0.85}
    )
    extractor.add_classification_metrics(
        'Gradient Boost',
        train_acc=96.1,
        test_acc=91.4,
        metrics={'mae': 0.35, 'rmse': 0.48, 'r2': 0.92}
    )
    extractor.add_classification_metrics(
        'Neural Network',
        train_acc=97.3,
        test_acc=90.8,
        metrics={'mae': 0.38, 'rmse': 0.52, 'r2': 0.91}
    )
    
    # Add training curve
    np.random.seed(42)
    epochs = 100
    train_losses = np.exp(-np.linspace(0, 2, epochs)) * 2 + np.random.normal(0, 0.05, epochs)
    val_losses = np.exp(-np.linspace(0, 1.8, epochs)) * 2.2 + np.random.normal(0, 0.07, epochs)
    extractor.add_training_curve(train_losses, val_losses)
    
    # Add error distribution
    train_errors = np.random.normal(0, 0.3, 500)
    test_errors = np.random.normal(0.1, 0.4, 200)
    extractor.add_error_distribution(train_errors, test_errors)
    
    # Add model comparison
    extractor.add_model_comparison({
        'Random Forest': (0.94, 0.8, 0.92),
        'SVM': (0.92, 0.7, 0.90),
        'Gradient Boost': (0.96, 0.75, 0.95),
        'Neural Network': (0.97, 0.6, 0.96)
    })
    
    # Add actual vs predicted
    y_true = np.random.uniform(-60, 35, 200)
    y_pred = y_true + np.random.normal(0, 5, 200)
    extractor.add_actual_vs_predicted(y_true, y_pred)
    
    # Add test set metrics
    extractor.add_test_set_metrics(
        r2_score=0.915,
        rmse=0.52,
        mae=0.38
    )
    
    return extractor.get_results()


if __name__ == "__main__":
    # Generate and save sample results
    results = create_sample_results()
    
    # Save to file
    with open('ml_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Sample ML results generated and saved to ml_results.json")
    print(json.dumps(results, indent=2)[:500] + "...")
