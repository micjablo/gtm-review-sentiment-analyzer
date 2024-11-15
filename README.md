# GTM Review Sentiment Analyzer - Cloud Function

## Overview

Ever noticed how product reviews can be misleading? Like when someone gives a low rating because of delivery issues, even though the product itself is excellent? Or when they leave a glowing review for a product that clearly isn't compatible with their setup?

This tool was originally created for a MeasureCamp presentation but has evolved into a production-ready solution for understanding what customers really think about your products. It separates product-specific feedback from external factors like delivery or customer service, providing a clearer picture of product performance.

## How It Works

The analyzer uses OpenAI's GPT to break down review text into specific aspects (product quality, delivery, customer service, etc.). It:

1. Identifies positive, neutral, and negative aspects of each review
2. Calculates a sentiment index mapped to a 1-5 scale
3. Tags specific aspects for detailed analysis in GA4

### Sentiment Calculation

```python
sentiment_index = round(((((pos - neg) / (pos + neg)) + 1) * 2) + 1, 2)
```

This formula transforms the sentiment analysis into a 1-5 scale to match standard star ratings, making it compatible with existing metrics.

## Repository Structure

```
gtm-review-sentiment-analyzer/
├── cloud_function/
│   ├── main.py              # Main Cloud Function code
│   ├── prompt.txt           # OpenAI system prompt
│   ├── tags.txt            # Aspect categories
│   └── requirements.txt     # Python dependencies
├── gtm_tag.html            # GTM Custom HTML Tag code
├── LICENSE                 # GPL-3.0 License
└── README.md              # Documentation
```

## Setup Instructions

### 1. Google Cloud Function Setup

1. Create a new Cloud Function
2. Upload all files from the `cloud_function` directory:
   - `main.py`
   - `prompt.txt`
   - `tags.txt`
   - `requirements.txt`
3. Set the entry point to `analyze_sentiment`
4. Set runtime to Python 3.9+
5. Add environment variable:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key

### 2. Google Tag Manager Setup

1. Create a new Custom HTML tag
2. Copy the contents of `gtm_tag.html`
3. Create two GTM variables:
   - A variable that returns the review text
   - A variable containing your Cloud Function URL
4. In the HTML code, replace:
   - `{{REVIEW_TEXT_VARIABLE}}` with your review text variable name
   - `{{CLOUD_FUNCTION_URL}}` with your Cloud Function URL variable name
5. Set your trigger (typically on review submission)

Example variable setup:
```javascript
// For review text from data layer
Variable Name: dlv_review_text
Type: Data Layer Variable
Data Layer Variable Name: reviewText

// For Cloud Function URL
Variable Name: const_sentiment_function_url
Type: Constant
Value: https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/analyze_sentiment
```

## Example Output

```json
{
  "status": "success",
  "sentiment_index": 4.25,
  "positive_aspect": "sound quality",
  "neutral_aspect": "design",
  "negative_aspect": "delivery",
  "keyword": "Great product, poor service",
  "all_positive_aspects": ["sound quality", "comfort"],
  "all_neutral_aspects": ["design"],
  "all_negative_aspects": ["delivery"],
  "metrics": {
    "positive_count": 2,
    "negative_count": 1
  }
}
```

## Use Cases

- Separating product quality issues from service-related feedback
- Understanding the true reasons behind ratings
- Automating review analysis at scale
- Creating more detailed analytics in GA4

## Requirements

- Google Cloud Platform account
- OpenAI API key
- Google Tag Manager container
- Review collection system

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## Author

Created by [micjablo](https://github.com/micjablo)
