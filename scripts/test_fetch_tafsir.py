#!/usr/bin/env python3
"""
Test script for fetch_tafsir.py functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_tafsir import (
    parse_verse_input,
    select_tafsir_by_menhec,
    get_tafsir_info,
    TAFSIR_EDITIONS
)

def test_parse_verse_input():
    """Test verse input parsing."""
    test_cases = [
        ("2:16", (2, 16)),
        ("1:1", (1, 1)),
        ("114:3", (114, 3)),
        ("Bakara 255", (2, 255)),
        ("fatiha 1", (1, 1)),
        ("surah 2 ayah 16", (2, 16)),
        ("surah 1 verse 1", (1, 1)),
        ("Al-Baqarah 255", (2, 255)),
        ("Yasin 1", (36, 1)),
        ("ar-rahman 1", (55, 1)),
    ]
    
    print("Testing parse_verse_input()...")
    for input_str, expected in test_cases:
        try:
            result = parse_verse_input(input_str)
            status = "✓" if result == expected else "✗"
            print(f"  {status} '{input_str}' -> {result} (expected: {expected})")
        except Exception as e:
            print(f"  ✗ '{input_str}' -> ERROR: {e}")
    
    print()

def test_select_tafsir_by_menhec():
    """Test menhec-based tafsir selection."""
    test_cases = [
        ("riwayah", "en-tafisr-ibn-kathir"),
        ("dirayah", "en-tafsir-maarif-ul-quran"),
        ("ishari", "en-kashf-al-asrar-tafsir"),
        ("athari", "en-tafisr-ibn-kathir"),
        ("tasawwuf", "en-al-qushairi-tafsir"),
        ("rivayet", "en-tafisr-ibn-kathir"),  # Turkish synonym
        ("işari", "en-kashf-al-asrar-tafsir"),  # Turkish synonym
        ("mystical", "en-kashf-al-asrar-tafsir"),  # English synonym
    ]
    
    print("Testing select_tafsir_by_menhec()...")
    for menhec, expected_slug in test_cases:
        try:
            result = select_tafsir_by_menhec(menhec)
            tafsir_info = get_tafsir_info(result)
            tafsir_name = tafsir_info.get("name", result) if tafsir_info else result
            status = "✓" if result == expected_slug else "✗"
            print(f"  {status} '{menhec}' -> {tafsir_name} ({result})")
        except Exception as e:
            print(f"  ✗ '{menhec}' -> ERROR: {e}")
    
    print()

def test_tafsir_database():
    """Test tafsir database integrity."""
    print("Testing tafsir database...")
    
    # Check all slugs are unique
    slugs = [edition["slug"] for edition in TAFSIR_EDITIONS]
    unique_slugs = set(slugs)
    
    if len(slugs) == len(unique_slugs):
        print("  ✓ All tafsir slugs are unique")
    else:
        print(f"  ✗ Duplicate slugs found: {len(slugs) - len(unique_slugs)}")
    
    # Check required fields
    required_fields = ["slug", "name", "author_name", "menhec"]
    for edition in TAFSIR_EDITIONS:
        missing_fields = [field for field in required_fields if field not in edition]
        if missing_fields:
            print(f"  ✗ Missing fields in {edition.get('slug', 'unknown')}: {missing_fields}")
        elif not edition["menhec"]:
            print(f"  ✗ Empty menhec list in {edition['slug']}")
        else:
            print(f"  ✓ {edition['slug']}: {edition['name']}")
    
    print()

def test_menhec_synonyms():
    """Test minimal menhec synonym fallback."""
    from methodology_matcher import normalize_menhec
    
    print("Testing minimal menhec synonym fallback (LLM should handle normalization)...")
    
    # Only minimal fallback synonyms should be normalized
    minimal_cases = [
        ("rivayet", "riwayah"),
        ("işari", "ishari"),
        ("diraye", "dirayah"),
        ("sufi", "tasawwuf"),
        ("tasavvuf", "tasawwuf"),
    ]
    
    for input_menhec, expected in minimal_cases:
        result = normalize_menhec(input_menhec)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_menhec}' -> '{result}' (expected: '{expected}')")
    
    # These should NOT be normalized by script
    non_normalized = [
        ("narrative", "narrative"),
        ("mystical", "mystical"),
        ("textual", "textual"),
        ("grammatical", "grammatical"),
    ]
    
    print("\n  Non-normalized (LLM's responsibility):")
    for input_menhec, expected in non_normalized:
        result = normalize_menhec(input_menhec)
        status = "✓" if result == expected else "✗"
        note = " (should not normalize)" if result == expected else " (incorrectly normalized!)"
        print(f"  {status} '{input_menhec}' -> '{result}'{note}")
    
    print()

def test_api_endpoints():
    """Test API endpoint construction."""
    print("Testing API endpoint construction...")
    
    test_cases = [
        ("en-tafisr-ibn-kathir", 2, 255, 
         "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/en-tafisr-ibn-kathir/2/255.json"),
        ("en-al-jalalayn", 1, 1,
         "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/en-al-jalalayn/1/1.json"),
        ("en-kashf-al-asrar-tafsir", 18, 1,
         "https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/en-kashf-al-asrar-tafsir/18/1.json"),
    ]
    
    from fetch_tafsir import BASE_URL
    
    for slug, surah, ayah, expected in test_cases:
        constructed = f"{BASE_URL}{slug}/{surah}/{ayah}.json"
        status = "✓" if constructed == expected else "✗"
        print(f"  {status} {slug}/{surah}/{ayah} -> {constructed}")
    
    print()

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Tafsir API Skill - Test Suite")
    print("=" * 60)
    print()
    
    test_parse_verse_input()
    test_select_tafsir_by_menhec()
    test_tafsir_database()
    test_menhec_synonyms()
    test_api_endpoints()
    
    print("=" * 60)
    print("Test suite completed.")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()