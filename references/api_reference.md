# Tafsir API Reference

## API Endpoint

### Base URL
```
https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/
```

### Request Format
```
GET /{slug}/{surah}/{ayah}.json
```

### Parameters
| Parameter | Type | Required | Description | Valid Values |
|-----------|------|----------|-------------|--------------|
| `slug` | string | Yes | Tafsir edition identifier | See [Tafsir Editions](#tafsir-editions) |
| `surah` | integer | Yes | Surah number | 1-114 |
| `ayah` | integer | Yes | Ayah (verse) number | 1-286 (varies by surah) |

### Example Requests
```bash
# Ibn Kathir tafsir for Surah 2, Ayah 255
curl "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/en-tafisr-ibn-kathir/2/255.json"

# Al-Jalalayn tafsir for Surah 1, Ayah 1
curl "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/en-al-jalalayn/1/1.json"

# Kashf Al-Asrar tafsir for Surah 18, Ayah 1
curl "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/en-kashf-al-asrar-tafsir/18/1.json"
```

## Response Format

### Success Response (200 OK)
```json
{
  "surah": 2,
  "ayah": 255,
  "text": "Allah! There is no deity except Him, the Ever-Living, the Sustainer of [all] existence..."
}
```

### Extended Response (with metadata)
When using the `fetch_tafsir.py` script, additional metadata is added:
```json
{
  "surah": 2,
  "ayah": 255,
  "text": "Allah! There is no deity except Him...",
  "tafsir_name": "Tafsir Ibn Kathir (abridged)",
  "author": "Hafiz Ibn Kathir",
  "slug": "en-tafisr-ibn-kathir"
}
```

## Error Responses

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Tafsir not available for Surah {surah}:{ayah} in {slug}",
  "surah": 2,
  "ayah": 300,
  "slug": "en-tafisr-ibn-kathir"
}
```

**Common causes:**
- Ayah number exceeds surah length (e.g., Surah 2 has 286 ayahs, requesting ayah 300)
- Tafsir doesn't cover that specific surah/ayah
- Invalid slug

### 500 Internal Server Error
```json
{
  "error": "server_error",
  "message": "Internal server error"
}
```

### Network Errors
```json
{
  "error": "network_error",
  "message": "Network error: {error_details}"
}
```

## Rate Limiting and Caching

### Rate Limits
- No explicit rate limits documented
- Use reasonable request intervals (≥1 second between requests)
- Implement exponential backoff for retries

### Caching Strategy
- API responses are static content (tafsir texts don't change)
- Implement client-side caching:
  - Cache successful responses locally
  - Cache duration: 24 hours for same surah:ayah:slug combination
  - Cache invalidated on error responses

### Recommended Implementation
```python
import requests
import time
from functools import lru_cache
from datetime import datetime, timedelta

class TafsirAPIClient:
    def __init__(self):
        self.base_url = "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
        
    @lru_cache(maxsize=100)
    def get_tafsir(self, slug: str, surah: int, ayah: int):
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        url = f"{self.base_url}{slug}/{surah}/{ayah}.json"
        response = requests.get(url, timeout=10)
        self.last_request_time = time.time()
        
        return response.json()
```

## Performance Tips

### Batch Requests
- Avoid making multiple rapid requests
- If fetching multiple ayahs from same surah, consider slight delays
- Example batch fetching:

```python
def fetch_multiple_ayahs(slug, surah, ayah_list):
    results = []
    for ayah in ayah_list:
        result = fetch_tafsir(slug, surah, ayah)
        results.append(result)
        time.sleep(0.5)  # Small delay between requests
    return results
```

### Error Recovery
- Implement retry logic for network errors
- Maximum 3 retries with exponential backoff
- Skip to next tafsir if one fails (when menhec matching)

```python
def fetch_with_retry(slug, surah, ayah, max_retries=3):
    for attempt in range(max_retries):
        try:
            return fetch_tafsir(slug, surah, ayah)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
```

## Alternative Endpoints

### CDN Alternatives
If the primary CDN is unavailable, try:
- `https://raw.githubusercontent.com/spa5k/tafsir_api/main/tafsir/{slug}/{surah}/{ayah}.json`
- Note: GitHub raw may have rate limits

### Local Cache Fallback
Consider maintaining a local cache of frequently requested tafsirs:
```python
local_cache = {
    ("en-tafisr-ibn-kathir", 1, 1): {
        "text": "In the Name of God the Compassionate the Merciful...",
        "cached_at": "2024-01-01T00:00:00Z"
    }
}
```

## Monitoring and Logging

### Recommended Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_tafsir_with_logging(slug, surah, ayah):
    logger.info(f"Fetching tafsir: {slug} for {surah}:{ayah}")
    try:
        result = fetch_tafsir(slug, surah, ayah)
        logger.info(f"Success: {surah}:{ayah}")
        return result
    except Exception as e:
        logger.error(f"Error fetching {surah}:{ayah}: {e}")
        raise
```

### Metrics to Track
- Request success rate
- Average response time
- Most requested surahs/ayahs
- Most popular tafsir editions
- Error rates by tafsir/surah