#!/usr/bin/env python
"""
Quick test script to verify the backend API is working correctly
Run this AFTER starting the backend with: python main.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   API: {response.json()['api']}")
            return True
        else:
            print("❌ Server returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Start with: python main.py")
        return False

def test_stats():
    """Test stats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/stats")
        data = response.json()
        print("\n✅ Stats Endpoint:")
        print(f"   ChEMBL available: {data['chembl']['available']}")
        print(f"   PDBBind available: {data['pdbbind']['available']}")
        print(f"   Model type: {data['model']['type']}")
        print(f"   Device: {data['model']['device']}")
        return True
    except Exception as e:
        print(f"❌ Stats endpoint failed: {e}")
        return False

def test_predict_single():
    """Test single prediction"""
    try:
        test_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"smiles": test_smiles, "name": "Aspirin"}
        )
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Single Prediction (Aspirin):")
            print(f"   SMILES: {test_smiles}")
            print(f"   Predicted pKd: {data['predicted_affinity_pKd']}")
            print(f"   Interpretation: {data['interpretation']}")
            return True
        else:
            print(f"❌ Prediction failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Prediction test failed: {e}")
        return False

def test_batch_predict():
    """Test batch predictions"""
    try:
        molecules = [
            {"smiles": "CCO", "name": "Ethanol"},
            {"smiles": "CC(=O)O", "name": "Acetic Acid"},
            {"smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "name": "Caffeine"}
        ]
        
        response = requests.post(
            f"{BASE_URL}/batch-predict",
            json={"molecules": molecules}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Batch Predictions:")
            print(f"   Total molecules: {data['total_molecules']}")
            print(f"   Valid molecules: {data['valid_molecules']}")
            for pred in data['predictions']:
                if pred['valid']:
                    print(f"   - {pred['name']}: {pred['predicted_affinity_pKd']} pKd")
            return True
        else:
            print(f"❌ Batch prediction failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Batch prediction test failed: {e}")
        return False

def test_chembl():
    """Test ChEMBL endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/chembl?count=4")
        if response.status_code == 200:
            data = response.json()
            print("\n✅ ChEMBL Endpoint:")
            print(f"   Molecules loaded: {data['count']}")
            print(f"   Image size: {len(data['image'])} bytes (base64)")
            print(f"   Source: {data['source']}")
            return True
        else:
            print(f"❌ ChEMBL endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ChEMBL test failed: {e}")
        return False

def test_pdbbind():
    """Test PDBBind endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/pdbbind?count=4")
        if response.status_code == 200:
            data = response.json()
            print("\n✅ PDBBind Endpoint:")
            print(f"   Ligands loaded: {data['count']}")
            print(f"   PDB IDs: {', '.join(data['pdb_ids'][:4])}")
            print(f"   Image size: {len(data['image'])} bytes (base64)")
            return True
        else:
            print(f"❌ PDBBind endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ PDBBind test failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 Molecular Binding Affinity API - Test Suite")
    print("="*60)
    
    tests = [
        ("Health Check", test_health),
        ("System Stats", test_stats),
        ("Single Prediction", test_predict_single),
        ("Batch Predictions", test_batch_predict),
        ("ChEMBL Endpoint", test_chembl),
        ("PDBBind Endpoint", test_pdbbind),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n🔍 Testing: {name}...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed == 0:
        print("✨ All tests passed! Your API is ready for Lovable.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
