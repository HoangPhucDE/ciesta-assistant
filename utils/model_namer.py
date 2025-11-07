"""Helper to generate LLM-style model names for Rasa model artifacts.

Example output: ciesta-20251106-1.0.0
This is just a helper that prints a name; you can use it when running rasa train with
`--fixed-model-name $(python utils/model_namer.py)`
"""
import datetime
import sys

if __name__ == "__main__":
    now = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    # simple semantic version placeholder
    version = "1.0.0"
    name = f"ciesta-{now}-{version}"
    sys.stdout.write(name)
