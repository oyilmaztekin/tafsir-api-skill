#!/usr/bin/env python3
"""
Fetch Quranic tafsir (exegesis) from API.

Usage:
    python3 fetch_tafsir.py --surah 2 --ayah 16 --slug en-tafisr-ibn-kathir
    python3 fetch_tafsir.py --surah 1 --ayah 1 --menhec riwayah
    python3 fetch_tafsir.py --verse "2:16" --slug en-tafisr-ibn-kathir

Parameters can be extracted from user input like "2:16, ibn kesir" or "Bakara 255, menhec ishari"
"""

import argparse
import json
import sys
import requests
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urljoin
from datetime import datetime, timedelta
from functools import lru_cache

# Base API URL
BASE_URL = "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/"
ALTERNATE_URL = "https://raw.githubusercontent.com/spa5k/tafsir_api/main/tafsir/"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cache for API responses (in-memory, persists for script lifetime)
_response_cache = {}
_cache_expiry = timedelta(hours=24)
_last_request_time = 0
MIN_REQUEST_INTERVAL = 1.0  # seconds between requests

# Tafsir editions database (updated with comprehensive metadata)
# Source: JSON metadata with rich menhec categories
TAFSIR_EDITIONS = [
    {
        "author_name": "Hafiz Ibn Kathir",
        "slug": "en-tafisr-ibn-kathir",
        "name": "Tafsir Ibn Kathir (abridged)",
        "language": "english",
        "menhec": ["14th-century", "riwayah", "athari", "sunni", "hadith-based", "quran-by-quran", "anti-israiliyyat"]
    },
    {
        "author_name": "Hafiz Ibn Kathir",
        "slug": "ar-tafsir-ibn-kathir",
        "name": "Tafsir Ibn Kathir",
        "language": "arabic",
        "menhec": ["14th-century", "riwayah", "athari", "sunni", "hadith-comprehensive", "shafi-jurisprudence"]
    },
    {
        "author_name": "Mufti Muhammad Shafi",
        "slug": "en-tafsir-maarif-ul-quran",
        "name": "Maarif-ul-Quran",
        "language": "english",
        "menhec": ["20th-century", "hanafi", "deobandi", "dirayah", "jurisprudential", "socio-moral", "contemporary-problems"]
    },
    {
        "author_name": "Saddi",
        "slug": "ar-tafseer-al-saddi",
        "name": "Tafseer Al Saddi",
        "language": "arabic",
        "menhec": ["20th-century", "sunni", "salafi", "athari", "taisir-al-karim", "simple-dirayah", "brief-explanation"]
    },
    {
        "author_name": "Baghawy",
        "slug": "ar-tafsir-al-baghawi",
        "name": "Tafseer Al-Baghawi",
        "language": "arabic",
        "menhec": ["12th-century", "riwayah", "athari", "shafi", "hadith-focused", "sunni", "classical-tradition"]
    },
    {
        "author_name": "Tanweer",
        "slug": "ar-tafseer-tanwir-al-miqbas",
        "name": "Tafseer Tanwir al-Miqbas",
        "language": "arabic",
        "menhec": ["15th-century-compilation", "ibn-abbas-attribution", "riwayah", "early-narratives", "sunni"]
    },
    {
        "author_name": "Waseet",
        "slug": "ar-tafsir-al-wasit",
        "name": "Tafsir Al Wasit",
        "language": "arabic",
        "menhec": ["20th-century", "dirayah", "al-azhar-style", "linguistic", "modern-sunni", "systematic-analysis"]
    },
    {
        "author_name": "Tabari",
        "slug": "ar-tafsir-al-tabari",
        "name": "Tafsir al-Tabari",
        "language": "arabic",
        "menhec": ["10th-century", "riwayah-foundational", "ijma-focused", "linguistic-analysis", "sunni", "encyclopedic", "sened-based"]
    },
    {
        "author_name": "المیسر",
        "slug": "ar-tafsir-muyassar",
        "name": "Tafsir Muyassar",
        "language": "arabic",
        "menhec": ["21st-century", "sunni", "salafi-oriented", "simplified", "brief-explanation"]
    },
    {
        "author_name": "Qurtubi",
        "slug": "ar-tafseer-al-qurtubi",
        "name": "Tafseer Al Qurtubi",
        "language": "arabic",
        "menhec": ["13th-century", "ahkam-jurisprudence", "maliki", "dirayah-riwayah-hybrid", "ethical-linguistic", "legal-focus"]
    },
    {
        "author_name": "Maulana Wahid Uddin Khan",
        "slug": "en-tazkirul-quran",
        "name": "Tazkirul Quran(Maulana Wahiduddin Khan)",
        "language": "english",
        "menhec": ["20th-century", "reflective", "contemplative-dirayah", "da'wah", "modern-english-style"]
    },
    {
        "author_name": "Kashf Al-Asrar Tafsir",
        "slug": "en-kashf-al-asrar-tafsir",
        "name": "Kashf Al-Asrar Tafsir",
        "language": "english",
        "menhec": ["12th-century", "sufism", "ishari", "tasawwuf", "persian-intellectual-tradition", "mystical-linguistic"]
    },
    {
        "author_name": "Al Qushairi Tafsir",
        "slug": "en-al-qushairi-tafsir",
        "name": "Al Qushairi Tafsir",
        "language": "english",
        "menhec": ["11th-century", "ishari", "tasawwuf", "spiritual-allusions", "ashari-kalam", "psychological-spiritual"]
    },
    {
        "author_name": "Kashani Tafsir",
        "slug": "en-kashani-tafsir",
        "name": "Kashani Tafsir",
        "language": "english",
        "menhec": ["14th-century", "shia", "isna-asher", "ithna-ashari", "ishari", "wahdat-al-wujud", "philosophical-sufism", "irfan"]
    },
    # Note: en-tafsir-al-tustari is not available in API (HTTP 403)
    {
        "author_name": "Asbab Al-Nuzul by Al-Wahidi",
        "slug": "en-asbab-al-nuzul-by-al-wahidi",
        "name": "Asbab Al-Nuzul by Al-Wahidi",
        "language": "english",
        "menhec": ["11th-century", "asbab-al-nuzul", "sebebi-nuzul", "occasions-of-revelation", "riwayah", "historical-context"]
    },
    {
        "author_name": "Tanwîr al-Miqbâs min Tafsîr Ibn ‘Abbâs",
        "slug": "en-tafsir-ibn-abbas",
        "name": "Tanwîr al-Miqbâs min Tafsîr Ibn ‘Abbâs",
        "language": "english",
        "menhec": ["15th-century-compilation", "ibn-abbas", "early-tradition", "riwayah", "narrative-exegesis"]
    },
    {
        "author_name": "Al-Jalalayn",
        "slug": "en-al-jalalayn",
        "name": "Al-Jalalayn",
        "language": "english",
        "menhec": ["15th-16th-century", "dirayah", "linguistic", "concise-literal", "shafi-context", "word-for-word-clarity"]
    }
]

# Menhec to tafsir mapping (priority order) - updated with comprehensive categories
MENHEC_MAPPING = {
    # Core methodology categories
    "riwayah": ["en-tafisr-ibn-kathir", "ar-tafsir-ibn-kathir", "ar-tafsir-al-baghawi", "ar-tafsir-al-tabari", "en-asbab-al-nuzul-by-al-wahidi", "en-tafsir-ibn-abbas", "ar-tafseer-tanwir-al-miqbas"],
    "dirayah": ["en-tafsir-maarif-ul-quran", "en-tazkirul-quran", "en-al-jalalayn", "ar-tafsir-al-wasit", "ar-tafseer-al-qurtubi"],
    "ishari": ["en-kashf-al-asrar-tafsir", "en-al-qushairi-tafsir", "en-kashani-tafsir"],
    "athari": ["en-tafisr-ibn-kathir", "ar-tafsir-ibn-kathir", "ar-tafseer-al-saddi", "ar-tafsir-al-baghawi"],
    
    # Historical periods
    "14th-century": ["en-tafisr-ibn-kathir", "ar-tafsir-ibn-kathir", "en-kashani-tafsir"],
    "20th-century": ["en-tafsir-maarif-ul-quran", "en-tazkirul-quran", "ar-tafseer-al-saddi", "ar-tafsir-al-wasit", "ar-tafsir-muyassar"],
    "classical": ["ar-tafsir-al-baghawi", "ar-tafsir-al-tabari", "ar-tafseer-al-qurtubi", "en-al-qushairi-tafsir", "en-al-jalalayn"],
    
    # Schools of thought
    "sunni": ["en-tafisr-ibn-kathir", "ar-tafsir-ibn-kathir", "ar-tafseer-al-saddi", "ar-tafsir-al-baghawi", "ar-tafsir-al-tabari", "ar-tafsir-muyassar", "ar-tafsir-al-wasit", "ar-tafseer-al-qurtubi"],
    "salafi": ["ar-tafseer-al-saddi", "ar-tafsir-muyassar"],
    "hanafi": ["en-tafsir-maarif-ul-quran"],
    "shafi": ["ar-tafsir-ibn-kathir", "ar-tafsir-al-baghawi", "en-al-jalalayn"],
    "maliki": ["ar-tafseer-al-qurtubi"],
    "deobandi": ["en-tafsir-maarif-ul-quran"],
    "shia": ["en-kashani-tafsir"],
    
    # Specialized categories
    "tasawwuf": ["en-al-qushairi-tafsir", "en-kashani-tafsir", "en-kashf-al-asrar-tafsir"],
    "sufism": ["en-kashf-al-asrar-tafsir", "en-al-qushairi-tafsir", "en-kashani-tafsir"],
    "hadith-based": ["en-tafisr-ibn-kathir", "ar-tafsir-ibn-kathir", "ar-tafsir-al-baghawi"],
    "jurisprudential": ["en-tafsir-maarif-ul-quran", "ar-tafseer-al-qurtubi"],
    "linguistic": ["en-al-jalalayn", "ar-tafsir-al-wasit", "ar-tafsir-al-tabari"],
    "asbab-al-nuzul": ["en-asbab-al-nuzul-by-al-wahidi"],
    "legal-focus": ["ar-tafseer-al-qurtubi", "en-tafsir-maarif-ul-quran"],
    "simplified": ["ar-tafsir-muyassar", "ar-tafseer-al-saddi"],
    "modern": ["en-tazkirul-quran", "ar-tafsir-al-wasit", "ar-tafsir-muyassar"],
    
    # Language preferences
    "english": ["en-tafisr-ibn-kathir", "en-tafsir-maarif-ul-quran", "en-tazkirul-quran", "en-kashf-al-asrar-tafsir", "en-al-qushairi-tafsir", "en-kashani-tafsir", "en-asbab-al-nuzul-by-al-wahidi", "en-tafsir-ibn-abbas", "en-al-jalalayn"],
    "arabic": ["ar-tafsir-ibn-kathir", "ar-tafseer-al-saddi", "ar-tafsir-al-baghawi", "ar-tafseer-tanwir-al-miqbas", "ar-tafsir-al-wasit", "ar-tafsir-al-tabari", "ar-tafsir-muyassar", "ar-tafseer-al-qurtubi"]
}

def parse_verse_input(verse_input: str) -> tuple[int, int]:
    """
    Parse verse input in various formats:
    - "2:16" -> (2, 16)
    - "Bakara 255" -> (2, 255)  
    - "fatiha 1" -> (1, 1)
    - "surah 2 ayah 16" -> (2, 16)
    - "surah 2 verse 16" -> (2, 16)
    """
    import re
    
    # Convert to lowercase and remove extra spaces
    verse_input = verse_input.lower().strip()
    
    # Define surah names mapping (local to avoid circular imports)
    surah_names = {
        "fatiha": 1, "al-fatiha": 1, "al-fatihah": 1, "opening": 1,
        "bakara": 2, "al-baqarah": 2, "baqara": 2, "cow": 2,
        "ali imran": 3, "al-imran": 3, "imran": 3, "family of imran": 3,
        "nisa": 4, "al-nisa": 4, "an-nisa": 4, "women": 4,
        "maidah": 5, "al-maidah": 5, "al-ma'idah": 5, "table": 5,
        "anam": 6, "al-anam": 6, "al-an'am": 6, "cattle": 6,
        "araf": 7, "al-araf": 7, "al-a'raf": 7, "heights": 7,
        "anfal": 8, "al-anfal": 8, "spoils of war": 8,
        "tawba": 9, "at-tawba": 9, "repentance": 9,
        "yunus": 10, "jonah": 10,
        "hud": 11,
        "yusuf": 12, "joseph": 12,
        "rad": 13, "ar-rad": 13, "thunder": 13,
        "ibrahim": 14, "abraham": 14,
        "hijr": 15, "al-hijr": 15, "rocky tract": 15,
        "nahl": 16, "an-nahl": 16, "bee": 16,
        "isra": 17, "al-isra": 17, "night journey": 17,
        "kahf": 18, "al-kahf": 18, "cave": 18,
        "maryam": 19, "mary": 19,
        "ta-ha": 20, "taha": 20,
        "yasin": 36, "ya-sin": 36,
        "rahman": 55, "ar-rahman": 55,
        "mulk": 67, "al-mulk": 67,
        "nas": 114, "an-nas": 114,
    }
    
    # Try multiple patterns in order of specificity
    
    # Pattern 1: "surah X ayah Y" or "surah X verse Y"
    pattern1 = r'^(?:surah|surat|sure|chapter)\s+(\d+|[a-z\s\-]+)\s+(?:ayah|verse|ayat|ayet|ayeti)\s+(\d+)$'
    match1 = re.search(pattern1, verse_input, re.IGNORECASE)
    if match1:
        try:
            surah_str = match1.group(1).strip()
            ayah = int(match1.group(2))
            
            if surah_str.isdigit():
                surah = int(surah_str)
            else:
                # Check if it's a known surah name
                if surah_str in surah_names:
                    surah = surah_names[surah_str]
                else:
                    # Try partial match
                    for name, num in surah_names.items():
                        if name in surah_str or surah_str in name:
                            surah = num
                            break
                    else:
                        raise ValueError(f"Unknown surah name: {surah_str}")
            
            return surah, ayah
        except (ValueError, IndexError):
            pass
    
    # Pattern 2: "X:Y" format
    pattern2 = r'^(\d+)\s*[:]\s*(\d+)$'
    match2 = re.search(pattern2, verse_input)
    if match2:
        try:
            surah = int(match2.group(1))
            ayah = int(match2.group(2))
            return surah, ayah
        except ValueError:
            pass
    
    # Pattern 3: "SurahName Number" format (e.g., "Bakara 255")
    pattern3 = r'^([a-z\s\-]+)\s+(\d+)$'
    match3 = re.search(pattern3, verse_input)
    if match3:
        try:
            surah_str = match3.group(1).strip()
            ayah = int(match3.group(2))
            
            if surah_str in surah_names:
                surah = surah_names[surah_str]
                return surah, ayah
            else:
                # Try partial match
                for name, num in surah_names.items():
                    if name in surah_str or surah_str in name:
                        surah = num
                        return surah, ayah
        except (ValueError, IndexError):
            pass
    
    # Pattern 4: Extract any two numbers
    numbers = re.findall(r'\d+', verse_input)
    if len(numbers) >= 2:
        try:
            surah = int(numbers[0])
            ayah = int(numbers[1])
            return surah, ayah
        except ValueError:
            pass
    
    # Pattern 5: Single number with surah name
    if len(numbers) == 1:
        ayah = int(numbers[0])
        # Try to find surah name
        for name, num in surah_names.items():
            if name in verse_input:
                surah = num
                return surah, ayah
    
    raise ValueError(f"Could not parse verse input: {verse_input}. Supported formats: '2:16', 'Bakara 255', 'surah 2 ayah 16', 'surah 2 verse 16'")

def select_tafsir_by_menhec(menhec: str) -> str:
    """
    Select tafsir slug based on menhec type.
    Returns the first matching tafsir slug.
    Uses methodology_matcher module for menhec matching.
    """
    try:
        # Import methodology_matcher module
        from methodology_matcher import get_tafsir_for_menhec
        return get_tafsir_for_menhec(menhec, return_all=False)
    except ImportError:
        # Fallback to local logic if methodology_matcher not available
        menhec = menhec.lower().strip()
        
        # Check direct mapping
        if menhec in MENHEC_MAPPING:
            for slug in MENHEC_MAPPING[menhec]:
                # Verify slug exists in our database
                if any(edition["slug"] == slug for edition in TAFSIR_EDITIONS):
                    return slug
        
        # Check if menhec matches any tafsir's menhec list
        for edition in TAFSIR_EDITIONS:
            if menhec in edition["menhec"]:
                return edition["slug"]
        
        # Default to Ibn Kathir
        return "en-tafisr-ibn-kathir"

def get_tafsir_info(slug: str) -> Dict[str, Any]:
    """Get tafsir metadata by slug."""
    for edition in TAFSIR_EDITIONS:
        if edition["slug"] == slug:
            return edition
    return {}

def enforce_rate_limit():
    """Enforce minimum time between API requests."""
    global _last_request_time
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    
    if time_since_last < MIN_REQUEST_INTERVAL:
        sleep_time = MIN_REQUEST_INTERVAL - time_since_last
        logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    _last_request_time = time.time()

def get_cache_key(slug: str, surah: int, ayah: int) -> str:
    """Generate cache key for API response."""
    return f"{slug}:{surah}:{ayah}"

def check_cache(slug: str, surah: int, ayah: int) -> Optional[Dict[str, Any]]:
    """Check if response is in cache and not expired."""
    cache_key = get_cache_key(slug, surah, ayah)
    
    if cache_key in _response_cache:
        cached_data, cached_time = _response_cache[cache_key]
        if datetime.now() - cached_time < _cache_expiry:
            logger.debug(f"Cache hit for {cache_key}")
            return cached_data
        else:
            logger.debug(f"Cache expired for {cache_key}")
            del _response_cache[cache_key]
    
    return None

def set_cache(slug: str, surah: int, ayah: int, data: Dict[str, Any]):
    """Store response in cache."""
    cache_key = get_cache_key(slug, surah, ayah)
    _response_cache[cache_key] = (data, datetime.now())
    logger.debug(f"Cached response for {cache_key}")

def fetch_with_fallback(url: str, timeout: int = 10) -> requests.Response:
    """Fetch from URL with fallback to alternate URL if needed."""
    try:
        enforce_rate_limit()
        logger.info(f"Fetching from primary URL: {url}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.warning(f"Primary URL failed: {e}, trying alternate URL")
        # Try alternate URL
        if BASE_URL in url:
            alt_url = url.replace(BASE_URL, ALTERNATE_URL)
        else:
            alt_url = url.replace(ALTERNATE_URL, BASE_URL)
        
        try:
            enforce_rate_limit()
            logger.info(f"Fetching from alternate URL: {alt_url}")
            response = requests.get(alt_url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as alt_e:
            logger.error(f"Alternate URL also failed: {alt_e}")
            raise

def fetch_tafsir(slug: str, surah: int, ayah: int, use_cache: bool = True) -> Dict[str, Any]:
    """
    Fetch tafsir from API with caching and fallback support.
    
    Returns:
        dict with keys: surah, ayah, text, tafsir_name, author
        or error dict with keys: error, message
    """
    logger.info(f"Fetching tafsir: {slug} for Surah {surah}:{ayah}")
    
    # Check cache first
    if use_cache:
        cached_result = check_cache(slug, surah, ayah)
        if cached_result:
            logger.info(f"Using cached result for {surah}:{ayah}")
            return cached_result
    
    # Construct URL
    url = f"{BASE_URL}{slug}/{surah}/{ayah}.json"
    
    try:
        response = fetch_with_fallback(url, timeout=15)
        
        data = response.json()
        
        # Add tafsir metadata
        tafsir_info = get_tafsir_info(slug)
        if tafsir_info:
            data["tafsir_name"] = tafsir_info["name"]
            data["author"] = tafsir_info["author_name"]
            data["slug"] = slug
        
        # Add timestamp
        data["fetched_at"] = datetime.now().isoformat()
        data["source"] = "api"
        
        # Cache the result
        if use_cache:
            set_cache(slug, surah, ayah, data)
        
        logger.info(f"Successfully fetched tafsir for {surah}:{ayah}")
        return data
        
    except requests.exceptions.HTTPError as e:
        error_response = {
            "error": "http_error",
            "message": f"HTTP error {response.status_code}: {str(e)}",
            "surah": surah,
            "ayah": ayah,
            "slug": slug,
            "fetched_at": datetime.now().isoformat()
        }
        
        if response.status_code == 404:
            error_response["error"] = "not_found"
            error_response["message"] = f"Tafsir not available for Surah {surah}:{ayah} in {slug}"
            logger.warning(f"Tafsir not found: {surah}:{ayah} in {slug}")
        else:
            logger.error(f"HTTP error {response.status_code} for {surah}:{ayah}: {e}")
        
        return error_response
        
    except requests.exceptions.RequestException as e:
        error_response = {
            "error": "network_error",
            "message": f"Network error: {str(e)}",
            "surah": surah,
            "ayah": ayah,
            "slug": slug,
            "fetched_at": datetime.now().isoformat()
        }
        logger.error(f"Network error for {surah}:{ayah}: {e}")
        return error_response
        
    except json.JSONDecodeError as e:
        error_response = {
            "error": "invalid_json",
            "message": f"Invalid JSON response: {str(e)}",
            "surah": surah,
            "ayah": ayah,
            "slug": slug,
            "fetched_at": datetime.now().isoformat()
        }
        logger.error(f"JSON decode error for {surah}:{ayah}: {e}")
        return error_response

def fetch_tafsir_with_fallback(slug: str, surah: int, ayah: int, fallback_slugs: List[str] = None) -> Dict[str, Any]:
    """
    Fetch tafsir with fallback to alternative tafsirs if primary fails.
    
    Args:
        slug: Primary tafsir slug
        surah: Surah number
        ayah: Ayah number
        fallback_slugs: List of alternative slugs to try (default: based on menhec)
    
    Returns:
        dict with tafsir data or error
    """
    # Try primary slug
    result = fetch_tafsir(slug, surah, ayah)
    
    # If success, return
    if "error" not in result:
        return result
    
    # If not found error, try fallbacks
    if result["error"] == "not_found" and fallback_slugs:
        logger.info(f"Primary tafsir not found, trying {len(fallback_slugs)} fallbacks")
        
        for fallback_slug in fallback_slugs:
            if fallback_slug == slug:
                continue  # Skip primary
                
            logger.info(f"Trying fallback tafsir: {fallback_slug}")
            fallback_result = fetch_tafsir(fallback_slug, surah, ayah)
            
            if "error" not in fallback_result:
                logger.info(f"Fallback successful: {fallback_slug}")
                # Add note about fallback
                fallback_result["fallback_used"] = True
                fallback_result["original_slug"] = slug
                return fallback_result
            
            # If also not found, continue to next fallback
            if fallback_result["error"] == "not_found":
                continue
            else:
                # Other error (network, etc.), return original error
                break
    
    # Return original error if no fallback succeeded
    return result

def format_output(result: Dict[str, Any], verbose: bool = False) -> str:
    """Format API result for display."""
    if "error" in result:
        # Enhanced error messages
        error_type = result.get("error", "unknown")
        message = result.get("message", "Unknown error")
        
        if error_type == "not_found":
            return f"❌ Tafsir not found: {message}\n💡 Try a different tafsir edition or check the surah/ayah numbers."
        elif error_type == "network_error":
            return f"🌐 Network error: {message}\n💡 Check your internet connection and try again."
        elif error_type == "http_error":
            return f"⚠️ Server error: {message}\n💡 The API server might be experiencing issues."
        else:
            return f"❌ Error: {message}"
    
    output = []
    
    if verbose:
        # Header with metadata
        if result.get("fallback_used"):
            original_slug = result.get("original_slug", "unknown")
            tafsir_info = get_tafsir_info(original_slug)
            original_name = tafsir_info.get("name", original_slug) if tafsir_info else original_slug
            output.append(f"⚠️ Note: Using fallback tafsir (original: {original_name} not available)")
        
        output.append(f"📖 Tafsir: {result.get('tafsir_name', 'Unknown')}")
        output.append(f"✍️ Author: {result.get('author', 'Unknown')}")
        output.append(f"📚 Surah: {result['surah']}, Ayah: {result['ayah']}")
        
        if result.get('source') == 'cache':
            fetched_at = result.get('fetched_at', 'unknown')
            output.append(f"💾 Source: Cached (fetched: {fetched_at})")
        else:
            output.append(f"🌐 Source: API (live)")
        
        output.append("─" * 40)
    
    # Main text
    output.append(result['text'])
    
    # Footer for verbose mode
    if verbose:
        output.append("─" * 40)
        if result.get('slug'):
            output.append(f"🔗 Slug: {result['slug']}")
    
    return "\n".join(output)

def get_fallback_slugs(slug: str, menhec: str = None) -> List[str]:
    """Get list of fallback tafsir slugs based on primary slug or menhec."""
    fallback_slugs = []
    
    # If menhec specified, get all tafsirs for that menhec
    if menhec:
        from methodology_matcher import get_all_tafsirs_for_menhec
        menhec_tafsirs = get_all_tafsirs_for_menhec(menhec)
        fallback_slugs = [t["slug"] for t in menhec_tafsirs]
    else:
        # Otherwise, get tafsirs with similar menhec
        tafsir_info = get_tafsir_info(slug)
        if tafsir_info and "menhec" in tafsir_info:
            primary_menhec = tafsir_info["menhec"][0] if tafsir_info["menhec"] else "riwayah"
            from methodology_matcher import get_all_tafsirs_for_menhec
            menhec_tafsirs = get_all_tafsirs_for_menhec(primary_menhec)
            fallback_slugs = [t["slug"] for t in menhec_tafsirs]
    
    # Remove primary slug from fallbacks if present
    if slug in fallback_slugs:
        fallback_slugs.remove(slug)
    
    return fallback_slugs[:3]  # Limit to 3 fallbacks

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Quranic tafsir from API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --verse "2:16" --slug en-tafisr-ibn-kathir
  %(prog)s --surah 1 --ayah 1 --menhec riwayah
  %(prog)s --verse "Bakara 255" --menhec ishari --verbose
  %(prog)s --verse "fatiha 1" --no-cache --verbose
  
Common surah names: fatiha, bakara, ali imran, nisa, maidah, yasin, rahman, mulk
        """
    )
    parser.add_argument("--surah", type=int, help="Surah number (1-114)")
    parser.add_argument("--ayah", type=int, help="Ayah number")
    parser.add_argument("--verse", type=str, help="Verse in format '2:16', 'Bakara 255', 'fatiha 1', etc.")
    parser.add_argument("--slug", type=str, help="Tafsir slug (e.g., en-tafisr-ibn-kathir)")
    parser.add_argument("--menhec", type=str, help="Methodology type (riwayah, dirayah, ishari, etc.)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output with metadata")
    parser.add_argument("--no-cache", action="store_true", help="Disable response caching")
    parser.add_argument("--no-fallback", action="store_true", help="Disable fallback to alternative tafsirs")
    parser.add_argument("--list-tafsirs", action="store_true", help="List all available tafsir editions")
    parser.add_argument("--list-menhec", action="store_true", help="List all available menhec types")
    
    args = parser.parse_args()
    
    # List tafsirs if requested
    if args.list_tafsirs:
        print("Available Tafsir Editions:")
        print("-" * 80)
        for edition in TAFSIR_EDITIONS:
            print(f"Slug: {edition['slug']}")
            print(f"Name: {edition['name']}")
            print(f"Author: {edition['author_name']}")
            print(f"Methodology: {', '.join(edition['menhec'])}")
            print("-" * 80)
        sys.exit(0)
    
    # List menhec types if requested
    if args.list_menhec:
        from methodology_matcher import get_menhec_options
        print("Available Menhec (Methodology) Types:")
        print("-" * 80)
        for menhec, desc in get_menhec_options().items():
            print(f"{menhec}: {desc}")
        sys.exit(0)
    
    # Parse verse input
    if args.verse:
        try:
            surah, ayah = parse_verse_input(args.verse)
            logger.info(f"Parsed verse '{args.verse}' as Surah {surah}, Ayah {ayah}")
        except ValueError as e:
            print(f"❌ Error parsing verse: {e}")
            print("💡 Supported formats: '2:16', 'Bakara 255', 'fatiha 1', 'surah 2 ayah 16'")
            sys.exit(1)
    elif args.surah and args.ayah:
        surah = args.surah
        ayah = args.ayah
        logger.info(f"Using provided Surah {surah}, Ayah {ayah}")
    else:
        print("❌ Error: Must provide either --verse or both --surah and --ayah")
        print("💡 Use --help for usage examples")
        sys.exit(1)
    
    # Validate surah and ayah ranges
    if not (1 <= surah <= 114):
        print(f"❌ Error: Surah number must be between 1 and 114 (got {surah})")
        sys.exit(1)
    
    # Determine tafsir slug
    if args.slug:
        slug = args.slug
        # Validate slug
        if not any(edition["slug"] == slug for edition in TAFSIR_EDITIONS):
            print(f"❌ Error: Invalid tafsir slug: {slug}")
            print("💡 Use --list-tafsirs to see available slugs")
            sys.exit(1)
    elif args.menhec:
        slug = select_tafsir_by_menhec(args.menhec)
        if args.verbose:
            tafsir_info = get_tafsir_info(slug)
            print(f"Selected tafsir: {tafsir_info.get('name', slug)} (for menhec: {args.menhec})")
    else:
        # Default to Ibn Kathir
        slug = "en-tafisr-ibn-kathir"
        if args.verbose:
            print("Using default tafsir: Tafsir Ibn Kathir")
    
    # Get fallback slugs if enabled
    fallback_slugs = None
    if not args.no_fallback:
        fallback_slugs = get_fallback_slugs(slug, args.menhec)
        if args.verbose and fallback_slugs:
            print(f"Fallback tafsirs: {', '.join(fallback_slugs)}")
    
    # Fetch tafsir
    use_cache = not args.no_cache
    if fallback_slugs and not args.no_fallback:
        result = fetch_tafsir_with_fallback(slug, surah, ayah, fallback_slugs)
    else:
        result = fetch_tafsir(slug, surah, ayah, use_cache)
    
    # Format and display output
    print(format_output(result, args.verbose))
    
    # Return exit code based on success
    if "error" in result:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()