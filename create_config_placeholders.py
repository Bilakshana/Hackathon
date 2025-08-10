import os
import json
from datetime import datetime

config_dir = "configs"
os.makedirs(config_dir, exist_ok=True)

# Enhanced Edge Cases Configuration
enhanced_edge_cases = {
    "edge_cases": [
        {
            "id": "ec_001",
            "name": "empty_input",
            "description": "Test behavior with completely empty input",
            "category": "input_validation",
            "severity": "high",
            "test_data": {
                "input": "",
                "expected_behavior": "graceful_error",
                "error_message": "Input cannot be empty"
            },
            "tags": ["validation", "empty", "boundary"]
        },
        {
            "id": "ec_002",
            "name": "extremely_long_input",
            "description": "Test with input exceeding maximum length",
            "category": "performance",
            "severity": "medium",
            "test_data": {
                "input": "x" * 10000,
                "expected_behavior": "truncate_or_error",
                "max_length": 5000
            },
            "tags": ["performance", "length", "boundary"]
        },
        {
            "id": "ec_003",
            "name": "special_characters",
            "description": "Test handling of special characters and unicode",
            "category": "encoding",
            "severity": "medium",
            "test_data": {
                "input": "café, naïve, résumé, \\n\\t",
                "expected_behavior": "preserve_encoding",
                "encoding": "utf-8"
            },
            "tags": ["unicode", "encoding", "special_chars"]
        },
        {
            "id": "ec_004",
            "name": "sql_injection_attempt",
            "description": "Test protection against SQL injection",
            "category": "security",
            "severity": "critical",
            "test_data": {
                "input": "'; DROP TABLE users; --",
                "expected_behavior": "sanitize_and_block",
                "security_level": "high"
            },
            "tags": ["security", "sql_injection", "malicious"]
        }
    ],
    "metadata": {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "total_cases": 4
    }
}

# ...other config dictionaries (safety_profiles, model_configs, etc.)...
# Paste the rest of your provided config dictionaries here (for brevity, omitted in this snippet).

# Dictionary of all configurations
files_and_content = {
    "enhanced_edge_cases.json": enhanced_edge_cases,
    # Add all other config dicts here as shown in your prompt
    # "safety_profiles.json": safety_profiles,
    # "model_configs.json": model_configs,
    # ...
}

# Create all configuration files
for filename, content in files_and_content.items():
    with open(os.path.join(config_dir, filename), "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2)

print("All configuration files created successfully!")