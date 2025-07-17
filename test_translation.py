#!/usr/bin/env python3
"""
Test script to verify translation functionality
"""

import os
import sys
sys.path.append('.')

# Test the translation function
def test_translation():
    from app import translate_to_spanish
    
    # Test text
    test_text = """
# Investment Analysis Report

## Key Findings:
- Current Price: $150.50
- Expected Return: 12%
- Risk Level: Medium
- Recommendation: BUY

This is a test report for translation functionality.
"""
    
    print("Testing translation function...")
    print("Original text:")
    print(test_text)
    print("\n" + "="*50 + "\n")
    
    # Translate
    translated = translate_to_spanish(test_text)
    print("Translated text:")
    print(translated)
    
    return translated

if __name__ == "__main__":
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OpenAI API key not found in environment variables")
        print("Please set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    print("OpenAI API key found, testing translation...")
    test_translation()
