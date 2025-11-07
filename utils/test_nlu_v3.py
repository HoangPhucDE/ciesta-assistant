"""
Test script for evaluating NLU model performance
"""

import os
from rasa.nlu.model import Metadata, Interpreter
from rasa.shared.nlu.training_data.message import Message
from pathlib import Path
import tarfile
import tempfile
import shutil

def extract_nlu_model(model_path):
    """Extract NLU model from Rasa model archive"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with tarfile.open(model_path, 'r:gz') as tar:
            tar.extractall(temp_dir)
            
        # Find nlu directory
        nlu_dir = None
        for root, dirs, files in os.walk(temp_dir):
            if 'nlu' in dirs:
                nlu_dir = os.path.join(root, 'nlu')
                break
                
        if nlu_dir:
            return nlu_dir
        return None

def test_nlu():
    # Load test data
    test_cases = [
        Message(data={
            "text": "Giới thiệu về Hà Nội",
            "intent": "ask_culture",
            "entities": [{"entity": "location", "value": "Hà Nội", "start": 13, "end": 19}]
        }),
        Message(data={
            "text": "Ẩm thực Đà Nẵng có gì ngon",
            "intent": "ask_cuisine", 
            "entities": [{"entity": "location", "value": "Đà Nẵng", "start": 8, "end": 15}]
        }),
        Message(data={
            "text": "Hãy kể một câu chuyện",
            "intent": "out_of_scope",
            "entities": []
        }),
        Message(data={
            "text": "Văn hóa TP.HCM như thế nào",
            "intent": "ask_culture",
            "entities": [{"entity": "location", "value": "TP.HCM", "start": 8, "end": 14}]
        }),
        Message(data={
            "text": "Đặc sản Sài Gòn có những gì",
            "intent": "ask_cuisine",
            "entities": [{"entity": "location", "value": "Sài Gòn", "start": 8, "end": 15}]
        })
    ]
    
    # Load latest model
    model_dir = Path('models')
    model_files = sorted(model_dir.glob('*.tar.gz'))
    if not model_files:
        print("No model files found!")
        return
        
    model_file = model_files[-1]  # Latest model
    print(f"Using model: {model_file}")
    
    # Extract and load NLU model
    nlu_dir = extract_nlu_model(str(model_file))
    if not nlu_dir:
        print("Could not find NLU model in archive!")
        return
        
    # Create temporary directory and copy model
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy NLU model to temp dir
        temp_nlu = os.path.join(temp_dir, 'nlu')
        shutil.copytree(nlu_dir, temp_nlu)
        
        # Load model
        metadata = Metadata.load(temp_nlu)
        interpreter = Interpreter.create(metadata, component_builder=None)
    
        total = len(test_cases)
        intent_correct = 0
        entity_correct = 0
        
        print("\nRunning test cases...")
        print("-" * 50)
        
        for test in test_cases:
            text = test.get("text")
            expected_intent = test.get("intent")
            expected_entities = test.get("entities", [])
            
            # Get predictions
            result = interpreter.parse(text)
            predicted_intent = result["intent"]["name"]
            predicted_entities = result["entities"]
            
            # Check intent
            intent_match = predicted_intent == expected_intent
            if intent_match:
                intent_correct += 1
                
            # Check entities 
            entities_match = True
            if len(predicted_entities) == len(expected_entities):
                for p, e in zip(predicted_entities, expected_entities):
                    if p["entity"] != e["entity"] or p["value"] != e["value"]:
                        entities_match = False
                        break
            else:
                entities_match = False
                
            if entities_match:
                entity_correct += 1
                
            # Print results
            print(f"Text: {text}")
            print(f"Intent: {intent_match} (expected={expected_intent}, got={predicted_intent})")
            print(f"Entities: {entities_match}")
            print(f"Expected: {expected_entities}")
            print(f"Got: {predicted_entities}")
            print("-" * 50)
            
        # Print overall results
        print("\nOverall Results:")
        print(f"Intent accuracy: {intent_correct/total:.2%}")
        print(f"Entity accuracy: {entity_correct/total:.2%}")

if __name__ == "__main__":
    test_nlu()