# LLM Prompt Guidelines for Tafsir API Skill

## Overview
This document provides guidance for LLMs (Language Models) on how to parse user requests and call the Tafsir API skill effectively. The skill handles Quranic tafsir (exegesis) requests via a REST API.

## Core Philosophy
- **LLM parses natural language, script handles complex logic**
- LLM extracts: verse reference, tafsir preference (slug/menhec), optional flags
- **LLM handles synonym normalization** (Turkish/English/Arabic → standard menhec terms)
- Script handles: input validation, API calls, caching, fallback, error handling
- Keep LLM prompts simple and focused on extraction

## Synonym Normalization Strategy

### Primary Responsibility: LLM
The LLM should normalize all menhec synonyms to these standard terms:

| Standard Term | Common Synonyms (LLM should normalize) |
|---------------|----------------------------------------|
| `riwayah`     | `rivayet`, `narrative`, `hadith-based`, `رواية` |
| `ishari`      | `işari`, `mystical`, `allegorical`, `symbolic`, `إشاري` |
| `dirayah`     | `diraye`, `rational`, `reason-based`, `دراية` |
| `tasawwuf`    | `sufi`, `sufism`, `tasavvuf`, `تصوف`, `spiritual` |

**Examples:**
- User says `"rivayet tefsiri"` → LLM extracts `menhec=riwayah`
- User says `"işari tefsir"` → LLM extracts `menhec=ishari`
- User says `"mystical tafsir"` → LLM extracts `menhec=ishari`
- User says `"sufi tefsiri"` → LLM extracts `menhec=tasawwuf`

### Fallback: Script (Minimal)
The script has minimal synonym mapping **only for offline/LLM failure cases**:
- `rivayet` → `riwayah`
- `işari` → `ishari`
- `diraye` → `dirayah`
- `sufi` → `tasawwuf`

**Best Practice:** Always normalize synonyms in the LLM layer. The script's fallback is for edge cases only.

## User Input Patterns

### 1. Verse References (Multiple Formats)
Extract surah and ayah numbers from these patterns:

```
"2:16"                    → surah=2, ayah=16
"Bakara 255"              → surah=2, ayah=255  
"fatiha 1"                → surah=1, ayah=1
"surah 2 ayah 16"         → surah=2, ayah=16
"surah 1 verse 1"         → surah=1, ayah=1
"Al-Baqarah 255"          → surah=2, ayah=255
"Yasin 1"                 → surah=36, ayah=1
"ar-rahman 1"             → surah=55, ayah=1
```

**Note:** Script handles 100+ surah name variations (English/Arabic/Turkish).

### 2. Tafsir Specification
Extract either `slug` (exact edition) or `menhec` (methodology):

#### By Slug (Exact Edition)
```
"Ibn Kathir tefsiri"      → slug=en-tafisr-ibn-kathir
"İbn Kesir"               → slug=en-tafisr-ibn-kathir
"Al-Jalalayn"             → slug=en-al-jalalayn
"Maarif-ul-Quran"         → slug=en-tafsir-maarif-ul-quran
"Kashf al-Asrar"          → slug=en-kashf-al-asrar-tafsir
```

#### By Menhec (Methodology)
```
"rivayet tefsiri"         → menhec=riwayah
"işari tefsir"            → menhec=ishari
"diraye tefsiri"          → menhec=dirayah
"narrative tafsir"        → menhec=riwayah
"mystical tafsir"         → menhec=ishari
"sufi tafsir"             → menhec=tasawwuf
```

**Synonym Support:** Script normalizes Turkish/English/Arabic variations.

### 3. Combined Requests
Parse combined patterns:

```
"2:16, ibn kesir"                    → verse=2:16, slug=en-tafisr-ibn-kathir
"Bakara 255, menhec ishari"          → verse=Bakara 255, menhec=ishari
"fatiha 1, rivayet tefsiri"          → verse=fatiha 1, menhec=riwayah
"surah 2 ayah 16, en-al-jalalayn"   → verse=surah 2 ayah 16, slug=en-al-jalalayn
```

## LLM Decision Logic

### 1. Parse User Request
```python
def parse_user_request(user_input: str) -> dict:
    """
    Extract parameters from user input.
    
    Returns dict with:
    - verse: str (raw verse input)
    - slug: str or None (tafsir slug if specified)
    - menhec: str or None (methodology if specified)
    - verbose: bool (if user wants details)
    """
```

### 2. Determine Tafsir Preference
Priority order:
1. **Explicit slug**: If user mentions specific edition (Ibn Kathir, Al-Jalalayn, etc.)
2. **Menhec**: If user specifies methodology (rivayet, işari, diraye)
3. **Default**: Use Ibn Kathir (slug: en-tafisr-ibn-kathir)

### 3. Build Script Command
```bash
# Basic command
python3 scripts/fetch_tafsir.py --verse "2:16" --slug "en-tafisr-ibn-kathir"

# With menhec
python3 scripts/fetch_tafsir.py --verse "Bakara 255" --menhec "ishari"

# Verbose output
python3 scripts/fetch_tafsir.py --verse "1:1" --slug "en-tafisr-ibn-kathir" --verbose

# Disable cache (for fresh data)
python3 scripts/fetch_tafsir.py --verse "2:16" --slug "en-tafisr-ibn-kathir" --no-cache
```

## Example Prompts for LLM

### Prompt Template 1: Direct Request
```
User: "2:16, ibn kesir tefsiri getir"

LLM should extract:
- verse: "2:16"
- slug: "en-tafisr-ibn-kathir"

Command: python3 scripts/fetch_tafsir.py --verse "2:16" --slug "en-tafisr-ibn-kathir"
```

### Prompt Template 2: Menhec-based Request
```
User: "Bakara 255 için işari tefsir bul"

LLM should extract:
- verse: "Bakara 255"
- menhec: "ishari"

Command: python3 scripts/fetch_tafsir.py --verse "Bakara 255" --menhec "ishari"
```

### Prompt Template 3: Turkish Input
```
User: "fatiha 1, rivayet tefsiri oku"

LLM should extract:
- verse: "fatiha 1"
- menhec: "rivayet" (script will normalize to "riwayah")

Command: python3 scripts/fetch_tafsir.py --verse "fatiha 1" --menhec "rivayet"
```

### Prompt Template 4: Detailed Request
```
User: "2:16 ayetinin İbn Kesir tefsirini detaylı şekilde getir"

LLM should extract:
- verse: "2:16"
- slug: "en-tafisr-ibn-kathir"
- verbose: True

Command: python3 scripts/fetch_tafsir.py --verse "2:16" --slug "en-tafisr-ibn-kathir" --verbose
```

## Error Handling Guidance

### LLM Should Handle These Cases:

1. **Ambiguous Verse Reference**
   ```
   User: "255" (missing surah)
   LLM Response: "Hangi surenin 255. ayetini istiyorsunuz? Örneğin: 'Bakara 255' veya '2:255'"
   ```

2. **Unknown Tafsir Edition**
   ```
   User: "2:16, unknown-tefsir"
   LLM Response: "Bilinmeyen tefsir ismi. Desteklenen tefsirler: İbn Kesir, Al-Jalalayn, Maarif-ul-Quran, vs."
   ```

3. **Invalid Menhec**
   ```
   User: "2:16, bilinmeyen-menhec"
   LLM Response: "Desteklenen tefsir metodolojileri: rivayet, işari, diraye"
   ```

### Let Script Handle These:
- Invalid surah/ayah numbers (script validates 1-114, reasonable ayah ranges)
- API errors (404, network issues - script provides user-friendly messages)
- Fallback logic (if tafsir not found, script tries alternatives)
- Rate limiting and caching

## Advanced Features

### 1. Cache Control
LLM can add flags based on user intent:
- `--no-cache`: For fresh data
- Default: Uses 24-hour cache

### 2. Fallback Control
- `--no-fallback`: Disable automatic fallback to alternative tafsirs
- Default: Enabled (tries similar menhec tafsirs if primary fails)

### 3. Listing Options
LLM can call these for help:
```bash
# List all tafsir editions
python3 scripts/fetch_tafsir.py --list-tafsirs

# List all menhec types
python3 scripts/fetch_tafsir.py --list-menhec
```

## Best Practices

### Do:
- Extract verse reference in any format (script will parse)
- Use menhec synonyms (rivayet, işari, diraye) - script normalizes
- Add `--verbose` when user asks for details
- Let script handle complex validation and API logic

### Don't:
- Don't validate surah/ayah ranges manually (script does it)
- Don't handle API errors (script provides user-friendly messages)
- Don't implement fallback logic (script has built-in fallback)
- Don't parse surah names extensively (script has 100+ name mapping)

## Integration Example

```python
# Pseudo-code for LLM integration
def handle_tafsir_request(user_input: str):
    # Extract parameters
    params = extract_params(user_input)  # verse, slug/menhec, flags
    
    # Build command
    cmd = ["python3", "scripts/fetch_tafsir.py"]
    
    if params.get("verse"):
        cmd.extend(["--verse", params["verse"]])
    
    if params.get("slug"):
        cmd.extend(["--slug", params["slug"]])
    elif params.get("menhec"):
        cmd.extend(["--menhec", params["menhec"]])
    
    if params.get("verbose"):
        cmd.append("--verbose")
    
    # Execute and return result
    result = execute_command(cmd)
    return format_result(result)
```

## Quick Reference Card

```
Verse Formats:   2:16, Bakara 255, fatiha 1, surah 2 ayah 16
Slugs:           en-tafisr-ibn-kathir, en-al-jalalayn, en-tafsir-maarif-ul-quran
Menhec Synonyms: rivayet→riwayah, işari→ishari, diraye→dirayah, mystical→ishari
Flags:           --verbose (details), --no-cache (fresh), --no-fallback (no alternatives)
Defaults:        Ibn Kathir, cache enabled, fallback enabled
```

This approach keeps LLM logic simple while leveraging the script's robust parsing, validation, and error handling capabilities.

## Enhanced Context Analysis with Comprehensive Menhec Categories

Now with the rich metadata in `references/tafsir_metadata.json`, LLM can perform sophisticated context analysis:

### Available Menhec Categories (60+ categories)

#### 1. Historical Periods
- **Classical (9th-14th century):** `10th-century`, `12th-century`, `13th-century`, `14th-century`, `classical`
- **Modern (20th-21st century):** `20th-century`, `21st-century`, `modern`

#### 2. Schools of Thought
- **Sunni:** `sunni`, `salafi`, `hanafi`, `shafi`, `maliki`, `deobandi`
- **Shia:** `shia`, `isna-asher`, `ithna-ashari`

#### 3. Methodology Types
- **Core:** `riwayah`, `dirayah`, `ishari`, `athari`
- **Specialized:** `tasawwuf`, `sufism`, `hadith-based`, `jurisprudential`, `linguistic`

#### 4. Language Preferences
- `english` (English translations)
- `arabic` (Original Arabic works)

#### 5. Style & Approach
- `simplified`, `brief-explanation`, `concise-literal`, `reflective`, `contemplative-dirayah`

### Context Analysis Examples

#### Example 1: Modern Turkish Reader
```
User: "Türkçe okuyacağım, modern ve sade bir tefsir istiyorum"

LLM Analysis:
- Language: Turkish user → prefers Arabic or English? (Context: Turkish readers often use Arabic tafsirs with translations)
- Style: "modern ve sade" → `modern`, `simplified`, `brief-explanation`
- Possible menhec: `modern`, `simplified`, `arabic` (or `english` if prefers translation)

Command: python3 scripts/fetch_tafsir.py --verse "{verse}" --menhec "modern simplified"
# Would select: ar-tafsir-muyassar (21st-century, simplified, brief-explanation)
```

#### Example 2: Hanefi Fiqh Student
```
User: "Hanefi mezhebine uygun fıkhi tefsir"

LLM Analysis:
- School: `hanafi`
- Focus: `jurisprudential`, `legal-focus`
- Possible menhec: `hanafi`, `jurisprudential`

Command: python3 scripts/fetch_tafsir.py --verse "{verse}" --menhec "hanafi jurisprudential"
# Would select: en-tafsir-maarif-ul-quran (hanafi, deobandi, jurisprudential)
```

#### Example 3: Academic Researcher
```
User: "Akademik araştırma için klasik dönem rivayet tefsiri"

LLM Analysis:
- Purpose: Academic research → needs authoritative, comprehensive
- Period: `classical`, `14th-century` (or specific century)
- Methodology: `riwayah`, `hadith-comprehensive`
- Possible menhec: `classical`, `riwayah`, `hadith-comprehensive`

Command: python3 scripts/fetch_tafsir.py --verse "{verse}" --menhec "classical riwayah hadith-comprehensive"
# Would select: ar-tafsir-ibn-kathir (14th-century, riwayah, hadith-comprehensive)
```

#### Example 4: Spiritual Seeker
```
User: "Manevi anlamlar için tasavvufi tefsir"

LLM Analysis:
- Focus: Spiritual meanings → `ishari`, `tasawwuf`, `sufism`
- Possible menhec: `ishari`, `tasawwuf`

Command: python3 scripts/fetch_tafsir.py --verse "{verse}" --menhec "ishari tasawwuf"
# Would select: en-kashf-al-asrar-tafsir (ishari, tasawwuf, mystical-linguistic)
```

### Intelligent Menhec Combination

LLM can combine multiple menhec categories based on user context:

```python
def analyze_user_context(user_input: str) -> list:
    """
    Analyze user context and return relevant menhec categories.
    """
    menhec_categories = []
    
    # Language preferences
    if any(word in user_input for word in ["türkçe", "ingilizce", "arapça"]):
        if "türkçe" in user_input or "ingilizce" in user_input:
            menhec_categories.append("english")
        elif "arapça" in user_input:
            menhec_categories.append("arabic")
    
    # Time period
    if any(word in user_input for word in ["modern", "çağdaş", "güncel"]):
        menhec_categories.append("modern")
    elif any(word in user_input for word in ["klasik", "kadim", "eski"]):
        menhec_categories.append("classical")
    
    # School of thought
    if "hanefi" in user_input:
        menhec_categories.append("hanafi")
    elif "şafii" in user_input:
        menhec_categories.append("shafi")
    elif "şia" in user_input or "şii" in user_input:
        menhec_categories.append("shia")
    
    # Style preferences
    if any(word in user_input for word in ["sade", "basit", "anlaşılır"]):
        menhec_categories.append("simplified")
    elif any(word in user_input for word in ["detaylı", "kapsamlı", "akademik"]):
        menhec_categories.append("encyclopedic")
    
    return menhec_categories
```

### Metadata Reference

The complete tafsir metadata is available in `references/tafsir_metadata.json`:
- **18 tafsir editions** with rich menhec categorization
- Each tafsir has 5-8 menhec categories describing its approach
- Historical period, school of thought, methodology, language, style

LLM can reference this metadata to make informed selections based on user context, preferences, and needs.