#!/usr/bin/env python3
"""
Extended test suite for Tafsir API skill.
Focuses on menhec synonym support and various user input patterns.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_tafsir import (
    parse_verse_input,
    select_tafsir_by_menhec,
    get_tafsir_info
)
from methodology_matcher import (
    normalize_menhec,
    get_tafsir_for_menhec,
    get_menhec_options
)

def test_menhec_synonyms_extended():
    """Test minimal menhec synonym fallback (LLM should handle normalization)."""
    print("=" * 60)
    print("Minimal Menhec Synonym Fallback Tests")
    print("=" * 60)
    print("Note: LLM should handle synonym normalization. This is minimal fallback only.")
    
    # Minimal fallback synonyms (Turkish only)
    minimal_cases = [
        ("rivayet", "riwayah", "en-tafisr-ibn-kathir"),
        ("işari", "ishari", "en-kashf-al-asrar-tafsir"),
        ("diraye", "dirayah", "en-tafsir-maarif-ul-quran"),
        ("sufi", "tasawwuf", "en-al-qushairi-tafsir"),
        ("tasavvuf", "tasawwuf", "en-al-qushairi-tafsir"),
    ]
    
    print("\n1. Minimal Fallback Synonyms (Turkish):")
    for input_menhec, expected_norm, expected_slug in minimal_cases:
        norm = normalize_menhec(input_menhec)
        slug = get_tafsir_for_menhec(input_menhec, return_all=False)
        tafsir_info = get_tafsir_info(slug)
        tafsir_name = tafsir_info.get("name", slug) if tafsir_info else slug
        
        norm_ok = "✓" if norm == expected_norm else "✗"
        slug_ok = "✓" if slug == expected_slug else "✗"
        
        print(f"  {norm_ok}{slug_ok} '{input_menhec}' -> '{norm}' -> {tafsir_name} ({slug})")
    
    # Test that non-minimal synonyms are NOT normalized (LLM's job)
    non_normalized_cases = [
        ("narrative", "narrative"),  # Should NOT normalize to riwayah
        ("mystical", "mystical"),    # Should NOT normalize to ishari
        ("rational", "rational"),    # Should NOT normalize to dirayah
        ("رواية", "رواية"),          # Should NOT normalize (Arabic)
        ("إشاري", "إشاري"),          # Should NOT normalize (Arabic)
    ]
    
    print("\n2. Non-Normalized Synonyms (LLM's responsibility):")
    for input_menhec, expected_norm in non_normalized_cases:
        norm = normalize_menhec(input_menhec)
        # These should NOT be normalized by script
        norm_ok = "✓" if norm == expected_norm else "✗"
        explanation = "(LLM should normalize)" if norm != expected_norm else "(correctly not normalized)"
        print(f"  {norm_ok} '{input_menhec}' -> '{norm}' {explanation}")

def test_real_world_commands():
    """Test real-world command patterns."""
    print("\n" + "=" * 60)
    print("Real-World Command Tests")
    print("=" * 60)
    
    test_cases = [
        # (description, command, expected_slug)
        ("Turkish rivayet", "--verse '2:16' --menhec 'rivayet'", "en-tafisr-ibn-kathir"),
        ("Turkish işari", "--verse 'Bakara 255' --menhec 'işari'", "en-kashf-al-asrar-tafsir"),
        ("English mystical (not normalized)", "--verse '1:1' --menhec 'mystical'", "en-tafisr-ibn-kathir"),
        ("English narrative (not normalized)", "--verse '2:16' --menhec 'narrative'", "en-tafisr-ibn-kathir"),
        ("Exact slug", "--verse '2:16' --slug 'en-tafisr-ibn-kathir'", "en-tafisr-ibn-kathir"),
        ("Default (no specification)", "--verse '2:16'", "en-tafisr-ibn-kathir"),
    ]
    
    for desc, cmd_part, expected_slug in test_cases:
        # Simulate the command parsing
        if "--menhec" in cmd_part:
            # Extract menhec value
            import re
            match = re.search(r"--menhec\s+'([^']+)'", cmd_part)
            if match:
                menhec = match.group(1)
                slug = select_tafsir_by_menhec(menhec)
            else:
                slug = "parse_error"
        elif "--slug" in cmd_part:
            # Extract slug value
            import re
            match = re.search(r"--slug\s+'([^']+)'", cmd_part)
            if match:
                slug = match.group(1)
            else:
                slug = "parse_error"
        else:
            # Default
            slug = "en-tafisr-ibn-kathir"
        
        status = "✓" if slug == expected_slug else "✗"
        print(f"  {status} {desc}: {cmd_part}")
        print(f"      → Slug: {slug} (expected: {expected_slug})")

def test_verse_parsing_edge_cases():
    """Test edge cases in verse parsing."""
    print("\n" + "=" * 60)
    print("Verse Parsing Edge Cases")
    print("=" * 60)
    
    edge_cases = [
        ("2 : 16", (2, 16), "Spaces around colon"),
        ("surah2ayah16", (2, 16), "No spaces"),
        ("SURAH 2 AYAH 16", (2, 16), "Uppercase"),
        ("surah   2   verse   16", (2, 16), "Multiple spaces"),
        ("2:16 with extra text", (2, 16), "Extra text after"),
        ("text before 2:16", (2, 16), "Extra text before"),
        ("Al-Fatiha 1", (1, 1), "Al- prefix"),
        ("An-Nisa 4", (4, 4), "An- prefix"),
        ("Ya-Sin 1", (36, 1), "Ya-Sin with hyphen"),
    ]
    
    for input_str, expected, description in edge_cases:
        try:
            result = parse_verse_input(input_str)
            status = "✓" if result == expected else "✗"
            print(f"  {status} {description}: '{input_str}' -> {result}")
        except Exception as e:
            print(f"  ✗ {description}: '{input_str}' -> ERROR: {e}")

def test_menhec_priority():
    """Test menhec priority mapping."""
    print("\n" + "=" * 60)
    print("Menhec Priority Tests")
    print("=" * 60)
    
    # Test that primary menhec gets highest priority tafsir
    menhec_priority = {
        "riwayah": "en-tafisr-ibn-kathir",  # Ibn Kathir first
        "dirayah": "en-tafsir-maarif-ul-quran",  # Maarif first
        "ishari": "en-kashf-al-asrar-tafsir",  # Kashf al-Asrar first
        "tasawwuf": "en-al-qushairi-tafsir",  # Qushairi first
    }
    
    for menhec, expected_slug in menhec_priority.items():
        slug = get_tafsir_for_menhec(menhec, return_all=False)
        tafsir_info = get_tafsir_info(slug)
        tafsir_name = tafsir_info.get("name", slug) if tafsir_info else slug
        
        status = "✓" if slug == expected_slug else "✗"
        print(f"  {status} '{menhec}' -> {tafsir_name} ({slug})")
        
        # Also test return_all to see options
        all_slugs = get_tafsir_for_menhec(menhec, return_all=True)
        print(f"      All options: {', '.join(all_slugs)}")

def run_all_extended_tests():
    """Run all extended tests."""
    print("\n" + "=" * 80)
    print("TAFSIR API SKILL - EXTENDED TEST SUITE")
    print("=" * 80)
    
    test_menhec_synonyms_extended()
    test_real_world_commands()
    test_verse_parsing_edge_cases()
    test_menhec_priority()
    
    print("\n" + "=" * 80)
    print("Extended test suite completed.")
    print("=" * 80)

if __name__ == "__main__":
    run_all_extended_tests()