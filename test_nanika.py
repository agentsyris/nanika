import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_nanika():
    # Check health
    health = requests.get(f"{BASE_URL}/health")
    print(f"Health: {health.json()}")
    
    # Start validation search
    validation = requests.post(
        f"{BASE_URL}/calmops/validate",
        json={"market": "new_jersey", "week": 1}
    )
    print(f"Validation task: {validation.json()}")
    
    task_id = validation.json()['task_id']
    
    # Check result after a few seconds
    time.sleep(5)
    result = requests.get(f"{BASE_URL}/task/{task_id}")
    print(f"Result: {json.dumps(result.json(), indent=2)}")

if __name__ == "__main__":
    test_nanika()