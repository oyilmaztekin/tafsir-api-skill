#!/usr/bin/env python3
"""
Menhec (methodology) matcher for tafsir selection.

This module provides functions to match menhec types to appropriate tafsir editions.
"""

# Tafsir editions database (same as in fetch_tafsir.py)
# Updated with comprehensive metadata from JSON
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

# Priority mapping for menhec types - updated with comprehensive categories
MENHEC_PRIORITY = {
    # Core methodology categories
    "riwayah": ["en-tafisr-ibn-kathir", "ar-tafsir-ibn-kathir", "ar-tafsir-al-baghawi", "ar-tafsir-al-tabari", "en-asbab-al-nuzul-by-al-wahidi", "en-tafsir-ibn-abbas", "ar-tafseer-tanwir-al-miqbas"],
    "dirayah": ["en-tafsir-maarif-ul-quran", "en-tazkirul-quran", "en-al-jalalayn", "ar-tafsir-al-wasit", "ar-tafseer-al-qurtubi"],
    "ishari": ["en-kashf-al-asrar-tafsir", "en-al-qushairi-tafsir", "en-kashani-tafsir"],
    "athari": ["en-tafisr-ibn-kathir", "ar-tafsir-ibn-kathir", "ar-tafseer-al-saddi", "ar-tafsir-al-baghawi"],
    
    # Historical periods
    "14th-century": ["en-tafisr-ibn-kathir", "ar-tafsir-ibn-kathir", "en-kashani-tafsir"],
    "20th-century": ["en-tafsir-maarif-ul-quran", "en-tazkirul-quran", "ar-tafseer-al-saddi", "ar-tafsir-al-wasit", "ar-tafsir-muyassar"],
    "classical": ["ar-tafsir-al-baghawi", "ar-tafsir-al-tabari", "ar-tafseer-al-qurtubi", "en-al-qushairi-tafsir", "en-al-jalalayn"],
    "10th-century": ["ar-tafsir-al-tabari"],
    "12th-century": ["ar-tafsir-al-baghawi", "en-kashf-al-asrar-tafsir"],
    "13th-century": ["ar-tafseer-al-qurtubi"],
    "15th-16th-century": ["en-al-jalalayn", "en-tafsir-ibn-abbas", "ar-tafseer-tanwir-al-miqbas"],
    "21st-century": ["ar-tafsir-muyassar"],
    
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
    "hadith-comprehensive": ["ar-tafsir-ibn-kathir"],
    "jurisprudential": ["en-tafsir-maarif-ul-quran", "ar-tafseer-al-qurtubi"],
    "linguistic": ["en-al-jalalayn", "ar-tafsir-al-wasit", "ar-tafsir-al-tabari"],
    "asbab-al-nuzul": ["en-asbab-al-nuzul-by-al-wahidi"],
    "sebebi-nuzul": ["en-asbab-al-nuzul-by-al-wahidi"],
    "legal-focus": ["ar-tafseer-al-qurtubi", "en-tafsir-maarif-ul-quran"],
    "simplified": ["ar-tafsir-muyassar", "ar-tafseer-al-saddi"],
    "modern": ["en-tazkirul-quran", "ar-tafsir-al-wasit", "ar-tafsir-muyassar"],
    "reflective": ["en-tazkirul-quran"],
    "contemplative-dirayah": ["en-tazkirul-quran"],
    "da'wah": ["en-tazkirul-quran"],
    
    # Language preferences
    "english": ["en-tafisr-ibn-kathir", "en-tafsir-maarif-ul-quran", "en-tazkirul-quran", "en-kashf-al-asrar-tafsir", "en-al-qushairi-tafsir", "en-kashani-tafsir", "en-asbab-al-nuzul-by-al-wahidi", "en-tafsir-ibn-abbas", "en-al-jalalayn"],
    "arabic": ["ar-tafsir-ibn-kathir", "ar-tafseer-al-saddi", "ar-tafsir-al-baghawi", "ar-tafseer-tanwir-al-miqbas", "ar-tafsir-al-wasit", "ar-tafsir-al-tabari", "ar-tafsir-muyassar", "ar-tafseer-al-qurtubi"],
    
    # Other specific categories
    "quran-by-quran": ["en-tafisr-ibn-kathir"],
    "anti-israiliyyat": ["en-tafisr-ibn-kathir"],
    "socio-moral": ["en-tafsir-maarif-ul-quran"],
    "contemporary-problems": ["en-tafsir-maarif-ul-quran"],
    "taisir-al-karim": ["ar-tafseer-al-saddi"],
    "brief-explanation": ["ar-tafseer-al-saddi", "ar-tafsir-muyassar"],
    "al-azhar-style": ["ar-tafsir-al-wasit"],
    "systematic-analysis": ["ar-tafsir-al-wasit"],
    "ijma-focused": ["ar-tafsir-al-tabari"],
    "encyclopedic": ["ar-tafsir-al-tabari"],
    "sened-based": ["ar-tafsir-al-tabari"],
    "salafi-oriented": ["ar-tafsir-muyassar"],
    "ahkam-jurisprudence": ["ar-tafseer-al-qurtubi"],
    "dirayah-riwayah-hybrid": ["ar-tafseer-al-qurtubi"],
    "ethical-linguistic": ["ar-tafseer-al-qurtubi"],
    "persian-intellectual-tradition": ["en-kashf-al-asrar-tafsir"],
    "mystical-linguistic": ["en-kashf-al-asrar-tafsir"],
    "spiritual-allusions": ["en-al-qushairi-tafsir"],
    "ashari-kalam": ["en-al-qushairi-tafsir"],
    "psychological-spiritual": ["en-al-qushairi-tafsir"],
    "isna-asher": ["en-kashani-tafsir"],
    "ithna-ashari": ["en-kashani-tafsir"],
    "wahdat-al-wujud": ["en-kashani-tafsir"],
    "philosophical-sufism": ["en-kashani-tafsir"],
    "irfan": ["en-kashani-tafsir"],
    "occasions-of-revelation": ["en-asbab-al-nuzul-by-al-wahidi"],
    "historical-context": ["en-asbab-al-nuzul-by-al-wahidi"],
    "ibn-abbas": ["en-tafsir-ibn-abbas", "ar-tafseer-tanwir-al-miqbas"],
    "early-tradition": ["en-tafsir-ibn-abbas"],
    "narrative-exegesis": ["en-tafsir-ibn-abbas"],
    "concise-literal": ["en-al-jalalayn"],
    "word-for-word-clarity": ["en-al-jalalayn"]
}

# Minimal synonym mapping for offline fallback only
# LLM should handle synonym normalization in most cases
# This is only for when LLM fails or offline operation
MINIMAL_SYNONYMS = {
    "riwayah": ["rivayet"],        # Turkish
    "ishari": ["işari"],           # Turkish
    "dirayah": ["diraye"],         # Turkish  
    "tasawwuf": ["sufi", "tasavvuf"],  # English/Turkish
}

def normalize_menhec(menhec: str) -> str:
    """
    Minimal normalization for offline fallback only.
    LLM should handle synonym normalization in most cases.
    
    Args:
        menhec: Input menhec string
    
    Returns:
        str: Normalized menhec key if found in minimal mapping, otherwise original
    """
    menhec = menhec.lower().strip()
    
    # Direct match with priority mapping
    if menhec in MENHEC_PRIORITY:
        return menhec
    
    # Minimal synonym fallback (offline/LLM failure case)
    for primary, synonyms in MINIMAL_SYNONYMS.items():
        if menhec == primary or menhec in synonyms:
            return primary
    
    # Return original if no minimal match found
    return menhec

def get_tafsir_for_menhec(menhec: str, return_all: bool = False):
    """
    Get tafsir slug(s) for a given menhec type.
    
    Args:
        menhec: Methodology type (e.g., "riwayah", "dirayah", "ishari")
        return_all: If True, return all matching tafsirs, otherwise return first match
    
    Returns:
        str or list: Tafsir slug(s) matching the menhec
    """
    # Normalize menhec input (minimal fallback only)
    normalized_menhec = normalize_menhec(menhec)
    if normalized_menhec != menhec:
        # Silent normalization for fallback cases
        pass
    menhec = normalized_menhec
    
    # Check priority mapping first
    if menhec in MENHEC_PRIORITY:
        slugs = MENHEC_PRIORITY[menhec]
        # Filter to ensure slugs exist in our database
        valid_slugs = [slug for slug in slugs if any(edition["slug"] == slug for edition in TAFSIR_EDITIONS)]
        
        if valid_slugs:
            if return_all:
                return valid_slugs
            else:
                return valid_slugs[0]
    
    # If not in priority mapping, search in tafsir menhec lists
    matching_slugs = []
    for edition in TAFSIR_EDITIONS:
        if menhec in edition["menhec"]:
            matching_slugs.append(edition["slug"])
    
    if matching_slugs:
        if return_all:
            return matching_slugs
        else:
            return matching_slugs[0]
    
    # Default to Ibn Kathir if no match found
    return "en-tafisr-ibn-kathir"

def get_menhec_options() -> dict:
    """
    Get all available menhec options with descriptions.
    
    Returns:
        dict: {menhec_type: description}
    """
    return {
        # Core methodology categories
        "riwayah": "Narrative-based exegesis, relying on hadith and early reports",
        "dirayah": "Rational/jurisprudential exegesis, using reason and legal analysis",
        "ishari": "Mystical/allegorical exegesis, seeking inner meanings",
        "athari": "Textual/traditional exegesis, strictly following texts",
        
        # Historical periods
        "10th-century": "10th century classical works (e.g., Tabari)",
        "12th-century": "12th century works (e.g., Baghawi, Kashf al-Asrar)",
        "13th-century": "13th century works (e.g., Qurtubi)",
        "14th-century": "14th century works (e.g., Ibn Kathir, Kashani)",
        "15th-16th-century": "15th-16th century works (e.g., Al-Jalalayn)",
        "20th-century": "20th century modern works",
        "21st-century": "21st century contemporary works",
        "classical": "Classical period tafsirs",
        "modern": "Modern period tafsirs",
        
        # Schools of thought
        "sunni": "Sunni school tafsirs",
        "salafi": "Salafi school tafsirs",
        "hanafi": "Hanafi school tafsirs",
        "shafi": "Shafi'i school tafsirs",
        "maliki": "Maliki school tafsirs",
        "deobandi": "Deobandi school tafsirs",
        "shia": "Shia tafsirs (e.g., Kashani)",
        
        # Specialized categories
        "tasawwuf": "Sufi spiritual exegesis",
        "sufism": "Sufi mystical interpretation",
        "hadith-based": "Exegesis heavily reliant on hadith literature",
        "hadith-comprehensive": "Comprehensive hadith-based exegesis",
        "jurisprudential": "Legal and jurisprudential analysis",
        "linguistic": "Linguistic and grammatical analysis",
        "asbab-al-nuzul": "Exegesis focusing on occasions of revelation (sebebi-nuzul)",
        "sebebi-nuzul": "Occasions of revelation (Turkish: sebebi nuzul)",
        "legal-focus": "Focus on legal rulings (ahkam)",
        "simplified": "Simplified explanation for general readers",
        "modern-english-style": "Modern English writing style",
        "reflective": "Reflective and contemplative approach",
        "contemplative-dirayah": "Contemplative rational exegesis",
        "da'wah": "Da'wah (invitation to Islam) oriented",
        
        # Language preferences
        "english": "English language tafsirs",
        "arabic": "Arabic language tafsirs",
        
        # Other specific categories
        "quran-by-quran": "Quran interpreting Quran approach",
        "anti-israiliyyat": "Rejects Isra'iliyyat (Jewish/Christian narratives)",
        "socio-moral": "Social and moral commentary",
        "contemporary-problems": "Addresses contemporary issues",
        "taisir-al-karim": "Simplified explanation style",
        "brief-explanation": "Brief and concise explanation",
        "al-azhar-style": "Al-Azhar University academic style",
        "systematic-analysis": "Systematic analytical approach",
        "ijma-focused": "Focuses on scholarly consensus",
        "encyclopedic": "Encyclopedic comprehensive approach",
        "sened-based": "Based on chain of narrators (isnad)",
        "salafi-oriented": "Salafi-oriented approach",
        "ahkam-jurisprudence": "Jurisprudential rulings focus",
        "dirayah-riwayah-hybrid": "Combines rational and narrative approaches",
        "ethical-linguistic": "Ethical and linguistic analysis",
        "persian-intellectual-tradition": "Persian intellectual tradition",
        "mystical-linguistic": "Mystical linguistic analysis",
        "spiritual-allusions": "Spiritual allusions and hints",
        "ashari-kalam": "Ash'ari theological school",
        "psychological-spiritual": "Psychological and spiritual analysis",
        "isna-asher": "Isna Ashari (Twelver Shia)",
        "ithna-ashari": "Ithna Ashari (Twelver Shia)",
        "wahdat-al-wujud": "Unity of existence philosophy",
        "philosophical-sufism": "Philosophical Sufism",
        "irfan": "Islamic mysticism (Irfan)",
        "occasions-of-revelation": "Historical context of revelation",
        "historical-context": "Historical context analysis",
        "ibn-abbas": "Attributed to Ibn Abbas tradition",
        "early-tradition": "Early Islamic tradition",
        "narrative-exegesis": "Narrative-based exegesis",
        "concise-literal": "Concise literal interpretation",
        "word-for-word-clarity": "Word-for-word clarity focus"
    }

def get_tafsir_by_slug(slug: str) -> dict:
    """Get tafsir metadata by slug."""
    for edition in TAFSIR_EDITIONS:
        if edition["slug"] == slug:
            return edition
    return {}

def get_all_tafsirs_for_menhec(menhec: str) -> list:
    """Get all tafsir editions matching a menhec type."""
    menhec = menhec.lower().strip()
    results = []
    
    for edition in TAFSIR_EDITIONS:
        if menhec in edition["menhec"]:
            results.append({
                "slug": edition["slug"],
                "name": edition["name"],
                "author": edition["author_name"],
                "menhec_list": edition["menhec"]
            })
    
    return results

def explain_menhec(menhec: str) -> str:
    """Get explanation of a menhec type."""
    descriptions = get_menhec_options()
    if menhec in descriptions:
        return descriptions[menhec]
    
    # Try to find similar menhec
    menhec_lower = menhec.lower()
    for key in descriptions:
        if menhec_lower in key or key in menhec_lower:
            return descriptions[key]
    
    return f"Menhec type '{menhec}' not found. Available types: {', '.join(sorted(descriptions.keys()))}"

if __name__ == "__main__":
    # Test the module
    import sys
    
    if len(sys.argv) > 1:
        menhec = sys.argv[1]
        print(f"Menhec: {menhec}")
        print(f"Explanation: {explain_menhec(menhec)}")
        
        tafsir = get_tafsir_for_menhec(menhec)
        tafsir_info = get_tafsir_by_slug(tafsir)
        
        print(f"\nRecommended tafsir: {tafsir_info.get('name', tafsir)}")
        print(f"Slug: {tafsir}")
        print(f"Author: {tafsir_info.get('author_name', 'Unknown')}")
        
        all_tafsirs = get_all_tafsirs_for_menhec(menhec)
        if len(all_tafsirs) > 1:
            print(f"\nAll tafsirs for '{menhec}':")
            for t in all_tafsirs:
                print(f"  - {t['name']} ({t['slug']})")
    else:
        print("Usage: python3 menhec_matcher.py <menhec_type>")
        print("\nAvailable menhec types:")
        for menhec, desc in get_menhec_options().items():
            print(f"  {menhec}: {desc}")