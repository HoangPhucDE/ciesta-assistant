"""
Test script for evaluating NLU model performance
"""

from rasa.core.agent import Agent
from rasa.shared.nlu.training_data.message import Message
from pathlib import Path
import asyncio

async def test_nlu():
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
    
    # Initialize RASA pipeline
    from rasa.core.agent import Agent
    agent = Agent.load(str(model_file))
    
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
        result = await agent.parse_message(text)
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
    asyncio.run(test_nlu())