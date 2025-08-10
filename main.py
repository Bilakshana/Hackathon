import re
import json
import hashlib
import logging
import os
import time
import threading
from typing import List, Dict, Optional, Tuple, Any
from groq import Groq
from dotenv import load_dotenv
from dataclasses import dataclass,asdict
from datetime import datetime
from collections import defaultdict

load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class SafetyConfig:
    max_tokens: int = 1000
    confidence_threshold: float = 0.7
    enable_fact_checking: bool = True
    enable_bias_detection: bool = True
    enable_harm_detection: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    model: str = "llama3-8b-8192"
    temperature: float = 0.7


@dataclass
class Response:
    content: str
    confidence: float
    safety_score: float
    Warnings: List[str]
    sources: List[str]
    processing_time: float
    retry_count: int
    model_version: str
    passed_safety: bool = True


class HarmDetector:
    def __init__(self):
        self.harmful_patterns = [
            r'\b(violence|kill|murder|harm|hurt|attack)\b',
            r'\b(hate|racist|discrimination|bias)\b',
            r'\b(illegal|criminal|fraud|scam)\b',
            r'\b(suicide|self-harm|depression)\b'
        ]

    def detect_harm(self, text: str) -> Tuple[bool, List[str]]:
        warnings = []
        is_harmful = False

        for pattern in self.harmful_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                is_harmful = True
                warnings.append(
                    f"Detected potentially harmful content: {', '.join(matches)}")
        negative_words = ['terrible', 'awful',
                          'horrible', 'disgusting', 'hate']
        negative_count = sum(
            1 for word in negative_words if word in text.lower())
        if negative_count > 3:
            warnings.append("High concentration of negative language detected")
            is_harmful = True
        return is_harmful, warnings


class BiasDetector:
    def __init__(self):
        self.bias_indicators = {
            'gender': ['men are', 'women are', 'boys are', 'girls are'],
            'racial': ['people from', 'race is', 'ethnicity'],
            'age': ['young people', 'old people', 'millennials', 'boomers'],
            'religious': ['christians', 'muslims', 'jews', 'atheists']
        }

    def detect_bias(self, text: str) -> Tuple[bool, List[str]]:
        warnings = []
        has_bias = False
        text_lower = text.lower()

        for bias_type, indicators in self.bias_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    pattern = rf'{indicator}.*?(always|never|all|most|generally|typically)'
                    if re.search(pattern, text_lower):
                        warnings.append(
                            f"Potential {bias_type} bias detected: overgeneralization")
                        has_bias = True
        return has_bias, warnings


class FactChecker:
    def __init__(self):
        self.facts_db = {
            "earth": {"shape": "sphere", "age": "4.5 billion years"},
            "water": {"boiling_point": "100°C", "formula": "H2O"},
            "python": {"type": "programming language", "created": "1991"}
        }

    def check_facts(self, text: str) -> Tuple[float, List[str]]:
        confidence = 0.8
        warnings = []

        if "earth is flat" in text.lower():
            confidence = 0.1
            warnings.append(
                "Statement contradicts established scientific facts")

        if "water boils at 0" in text.lower():
            confidence = 0.2
            warnings.append("Incorrect scientific information detected")

        claim_patterns = [
            r"studies show",
            r"research proves",
            r"scientists say",
            r"according to experts"
        ]
        for pattern in claim_patterns:
            if re.search(pattern, text.lower()):
                if "source:" not in text.lower():
                    warnings.append("Unsupported claim without sources")
                    confidence *= 0.9

        return confidence, warnings
class GuardianLayer:
    def __init__(self,config:SafetyConfig):
        self.config=config
        self.harm_detector=HarmDetector()
        self.bias_detector=BiasDetector()
        self.fact_checker=FactChecker()
        self.monitoring_active=True
    
    def validate_input(self,user_input:str) -> Tuple[bool,List[str]]:
        warnings=[]
        is_safe=True

        if len(user_input)>5000:
            warnings.append("Input too long, truncating for safety")
            is_safe=False

        
        injection_patterns=[
            r"ignore previous",
            r"forget instructions",
            r"new instructions",
            r"system prompt"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern,user_input.lower()):
                warnings.append("Potential prompt injection detected")
                is_safe=False
                
        is_harmful,harm_warnings=self.harm_detector.detect_harm(user_input)

        if is_harmful:
            warnings.extend(harm_warnings)
            is_safe=False

        return is_safe,warnings
    
    def validate_output(self,output:str) -> Tuple[bool,float,List[str]]:
        warnings=[]
        safety_score=1.0
        is_safe=True

        
        
