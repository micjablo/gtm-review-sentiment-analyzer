"""
GTM Review Sentiment Analyzer - Cloud Function
Author: micjablo (https://github.com/micjablo)
License: GPL-3.0
"""

import functions_framework
import openai
import os
import json
from typing import Dict, List, Union, Tuple

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_file(filename: str) -> str:
    """Load content from a file safely."""
    try:
        with open(filename, "r", encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return ""

def calculate_sentiment_index(pos: int, neg: int) -> float:
    """Calculate sentiment index on a 1-5 scale."""
    try:
        # Ensure we're working with numbers
        pos = int(pos) if isinstance(pos, (int, str, float)) else 0
        neg = int(neg) if isinstance(neg, (int, str, float)) else 0
        
        if (pos + neg) > 0:
            return round(((((pos - neg) / (pos + neg)) + 1) * 2) + 1, 2)
        return 3.00  # Neutral value if no aspects found
    except (ZeroDivisionError, ValueError, TypeError):
        return 3.00  # Neutral value if any calculation error

def extract_aspects_count(analysis_result: Dict) -> Tuple[int, int]:
    """Safely extract positive and negative aspect counts."""
    try:
        # Get aspects lists
        positive_aspects = analysis_result.get('aspects', {}).get('positive', [])
        negative_aspects = analysis_result.get('aspects', {}).get('negative', [])
        
        # Count aspects, ensuring we have lists
        pos_count = len(positive_aspects) if isinstance(positive_aspects, list) else 0
        neg_count = len(negative_aspects) if isinstance(negative_aspects, list) else 0
        
        return pos_count, neg_count
    except Exception as e:
        print(f"Error counting aspects: {str(e)}")
        return 0, 0

def analyze_review(review_text: str, allowed_aspects: List[str]) -> Dict:
    """Analyze review using OpenAI API."""
    try:
        system_prompt = load_file("prompt.txt")
        user_prompt = f"""Analyze this product review and categorize sentiments.
Only use these aspects: {', '.join(allowed_aspects)}
Review: {review_text}

Return ONLY a JSON object with this exact structure:
{{
  "aspects": {{
    "positive": [],
    "neutral": [],
    "negative": []
  }},
  "summary": {{
    "main_positive": "none",
    "main_neutral": "none",
    "main_negative": "none",
    "keyword": ""
  }}
}}"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )

        # Parse and validate response
        result = json.loads(response.choices[0].message.content)
        
        # Ensure required structure exists
        if 'aspects' not in result or 'summary' not in result:
            raise ValueError("Invalid response structure from OpenAI")
            
        return result

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        # Return a valid default structure
        return {
            "aspects": {"positive": [], "neutral": [], "negative": []},
            "summary": {
                "main_positive": "none",
                "main_neutral": "none",
                "main_negative": "none",
                "keyword": ""
            }
        }
    except Exception as e:
        print(f"Error in analyze_review: {str(e)}")
        raise

@functions_framework.http
def analyze_sentiment(request) -> Tuple[str, int, Dict]:
    """
    Main Cloud Function for sentiment analysis.
    Returns: (response_body, status_code, headers)
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600'
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    try:
        # Get review text from request
        review_text = None
        if request.method == 'GET':
            review_text = request.args.get('review', '')
        elif request.method == 'POST':
            request_json = request.get_json(silent=True)
            if request_json and 'review' in request_json:
                review_text = request_json['review']

        # Validate review text
        if not review_text:
            return (json.dumps({
                "error": "No review text provided",
                "status": "error"
            }), 400, headers)

        if len(review_text) > 2000:
            return (json.dumps({
                "error": "Review text too long (max 2000 characters)",
                "status": "error"
            }), 400, headers)

        # Load allowed aspects
        allowed_aspects = [aspect.strip() for aspect in load_file("tags.txt").split(',')]
        if not allowed_aspects:
            return (json.dumps({
                "error": "Failed to load aspect categories",
                "status": "error"
            }), 500, headers)

        # Analyze the review
        analysis_result = analyze_review(review_text, allowed_aspects)

        # Safely calculate metrics
        pos_count, neg_count = extract_aspects_count(analysis_result)

        # Format the response
        response_data = {
            "status": "success",
            "sentiment_index": calculate_sentiment_index(pos_count, neg_count),
            "positive_aspect": analysis_result.get('summary', {}).get('main_positive', 'none'),
            "neutral_aspect": analysis_result.get('summary', {}).get('main_neutral', 'none'),
            "negative_aspect": analysis_result.get('summary', {}).get('main_negative', 'none'),
            "keyword": analysis_result.get('summary', {}).get('keyword', ''),
            "all_positive_aspects": analysis_result.get('aspects', {}).get('positive', []),
            "all_neutral_aspects": analysis_result.get('aspects', {}).get('neutral', []),
            "all_negative_aspects": analysis_result.get('aspects', {}).get('negative', []),
            "metrics": {
                "positive_count": pos_count,
                "negative_count": neg_count
            }
        }

        return (json.dumps(response_data), 200, headers)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return (json.dumps({
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }), 500, headers)

if __name__ == "__main__":
    print("Cloud Function is ready.")