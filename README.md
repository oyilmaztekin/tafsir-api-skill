# Tafsir API Skill for OpenClaw

<div align="center">

![Quran](https://img.shields.io/badge/Quran-Exegesis-green)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)
![License](https://img.shields.io/badge/License-MIT-orange)

**Intelligent Quranic Tafsir (Exegesis) Retrieval with Context-Aware Selection**

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [Usage](#usage) • [API Reference](#api-reference) • [Contributing](#contributing)

</div>

## 📖 Overview

The **Tafsir API Skill** is an OpenClaw skill that provides intelligent access to Quranic exegesis (tafsir) texts through a REST API. It features sophisticated context analysis, rich metadata categorization, and intelligent tafsir selection based on user preferences, historical period, methodology, language, and school of thought.

This skill enables LLMs to fetch appropriate tafsir texts for any Quranic verse while considering the user's context, preferences, and requirements.

## ✨ Features

### 🎯 **Intelligent Context Analysis**
- **60+ Menhec Categories**: Historical periods, methodologies, schools of thought, languages, styles
- **User Preference Mapping**: Analyzes user context (language, school, style preferences)
- **Optimal Tafsir Selection**: Automatically selects the most appropriate tafsir based on multiple criteria

### 🔧 **Robust Technical Foundation**
- **100+ Verse Format Support**: Parses "2:16", "Bakara 255", "surah 1 verse 1", "fatiha 1", etc.
- **Multi-language Synonym Support**: Turkish/English/Arabic menhec term normalization
- **Production-Ready Features**: Caching (24h), rate limiting (1s), fallback mechanisms
- **Comprehensive Error Handling**: User-friendly messages and automatic recovery

### 📚 **Rich Metadata Integration**
- **18 Tafsir Editions**: 17 English, 1 Arabic with comprehensive metadata
- **Detailed Categorization**: Each tafsir categorized by 5-8 menhec attributes
- **Historical Context**: Period-based selection (10th-21st century works)

### 🤖 **LLM-Optimized Design**
- **Two-Layer Synonym Handling**: LLM handles normalization, script provides fallback
- **Context-Aware Prompts**: LLM can analyze user intent and select optimal parameters
- **Semantic Understanding**: Natural language parsing for verse references and preferences

## 🏗️ Architecture

```mermaid
graph TB
    A[User Request] --> B[LLM Context Analysis]
    B --> C[Parameter Extraction]
    C --> D[Script Execution]
    D --> E{API Call}
    E -->|Success| F[Formatted Output]
    E -->|Failure| G[Fallback Strategy]
    G --> H[Alternative Tafsir]
    H --> F
    
    subgraph "Metadata Database"
        I[18 Tafsir Editions]
        J[60+ Menhec Categories]
        K[Rich Categorization]
    end
    
    D --> I
    B --> J
```

### Core Components

1. **`fetch_tafsir.py`** - Main script with caching, rate limiting, and fallback
2. **`methodology_matcher.py`** - Intelligent menhec matching with 60+ categories
3. **`tafsir_metadata.json`** - Comprehensive metadata for 18 tafsir editions
4. **`llm_prompts.md`** - Context analysis guide for LLMs

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/oyilmaztekin/tafsir-api-skill.git
cd tafsir-api-skill

# Install as OpenClaw skill
openclaw skills install .
```

### Basic Usage

```bash
# Fetch tafsir for a specific verse
python3 scripts/fetch_tafsir.py --verse "2:16"

# Specify methodology (menhec)
python3 scripts/fetch_tafsir.py --verse "Bakara 255" --menhec "ishari"

# Use specific tafsir edition
python3 scripts/fetch_tafsir.py --verse "1:1" --slug "en-tafisr-ibn-kathir"

# Get verbose output with details
python3 scripts/fetch_tafsir.py --verse "2:16" --slug "en-tafisr-ibn-kathir" --verbose
```

### LLM Integration Example

```python
# Pseudo-code for LLM integration
def handle_tafsir_request(user_input):
    # Analyze user context
    context = analyze_user_context(user_input)
    # Extract parameters
    params = extract_parameters(user_input, context)
    # Build and execute command
    result = execute_tafsir_command(params)
    return format_result(result)
```

## 📊 Tafsir Editions

The skill supports 18 tafsir editions across various categories:

| Category | Tafsir Examples | Key Characteristics |
|----------|----------------|---------------------|
| **Classical Riwayah** | Ibn Kathir, Al-Baghawi, Al-Tabari | Hadith-based, narrative-focused, 10th-14th century |
| **Modern Dirayah** | Maarif-ul-Quran, Tazkirul Quran | Rational analysis, contemporary issues, 20th century |
| **Sufi/Ishari** | Kashf al-Asrar, Al-Qushairi, Kashani | Mystical interpretation, spiritual insights |
| **Jurisprudential** | Al-Qurtubi, Maarif-ul-Quran | Legal focus, fiqh-oriented analysis |
| **Simplified** | Al-Muyassar, Al-Saddi | Brief explanations, easy understanding |

**Complete List**: See [`references/tafsir_editions.md`](references/tafsir_editions.md)

## 🎯 Menhec Categories

### Historical Periods
- `10th-century`, `12th-century`, `13th-century`, `14th-century`
- `15th-16th-century`, `20th-century`, `21st-century`
- `classical`, `modern`

### Schools of Thought
- `sunni`, `salafi`, `hanafi`, `shafi`, `maliki`, `deobandi`, `shia`

### Methodology Types
- `riwayah` (narrative), `dirayah` (rational), `ishari` (mystical), `athari` (textual)
- `tasawwuf` (Sufi), `sufism`, `hadith-based`, `jurisprudential`, `linguistic`

### Language Preferences
- `english` (English translations)
- `arabic` (Original Arabic works)

### Style & Approach
- `simplified`, `brief-explanation`, `concise-literal`
- `reflective`, `contemplative-dirayah`, `encyclopedic`

## 🔍 Usage Examples

### Example 1: Simple Verse Request (Default Methodology)
```
User: "Get tafsir for 2:255"

LLM Analysis:
- Verse: "2:255" → surah=2, ayah=255
- No methodology specified → default to riwayah (narrative-based)
- Menhec: riwayah (default)

Command: python3 scripts/fetch_tafsir.py --verse "2:255" --menhec "riwayah"
Result: en-tafisr-ibn-kathir (riwayah, athari, hadith-based)
```

### Example 2: Verse with Mystical Interpretation
```
User: "Find mystical tafsir for 1:1"

LLM Analysis:
- Verse: "1:1" → surah=1, ayah=1
- Methodology: "mystical" → ishari (mystical/allegorical)
- Menhec: ishari

Command: python3 scripts/fetch_tafsir.py --verse "1:1" --menhec "ishari"
Result: en-kashf-al-asrar-tafsir (ishari, sufi-mystical, mystical-linguistic)
```

### Example 3: Specific Tafsir Edition Request
```
User: "Ibn Kathir tafsir for Al-Baqarah 255"

LLM Analysis:
- Verse: "Al-Baqarah 255" → surah=2, ayah=255
- Specific edition: "Ibn Kathir" → slug: en-tafisr-ibn-kathir
- Command uses slug instead of menhec

Command: python3 scripts/fetch_tafsir.py --verse "Al-Baqarah 255" --slug "en-tafisr-ibn-kathir"
Result: en-tafisr-ibn-kathir (direct slug selection)
```

### Example 4: Narrative and Hadith-Based Tafsir
```
User: "Narrative and hadith-based tafsir for 2:16"

LLM Analysis:
- Verse: "2:16" → surah=2, ayah=16
- Methodology: "narrative and hadith-based" → riwayah, hadith-based
- Menhec: riwayah, hadith-based

Command: python3 scripts/fetch_tafsir.py --verse "2:16" --menhec "riwayah hadith-based"
Result: en-tafisr-ibn-kathir (riwayah, hadith-based, athari)
```

### Example 5: Modern Simplified Tafsir
```
User: "Modern simple tafsir for 36:1"

LLM Analysis:
- Verse: "36:1" → surah=36, ayah=1
- Style: "modern simple" → modern, simplified
- Menhec: modern, simplified

Command: python3 scripts/fetch_tafsir.py --verse "36:1" --menhec "modern simplified"
Result: ar-tafsir-muyassar (21st-century, simplified, brief-explanation)
```

### Example 6: Hanafi Jurisprudential Tafsir
```
User: "Hanafi jurisprudential tafsir for 4:34"

LLM Analysis:
- Verse: "4:34" → surah=4, ayah=34
- School: "Hanafi" → hanafi
- Focus: "jurisprudential" → jurisprudential
- Menhec: hanafi, jurisprudential

Command: python3 scripts/fetch_tafsir.py --verse "4:34" --menhec "hanafi jurisprudential"
Result: en-tafsir-maarif-ul-quran (hanafi, jurisprudential, socio-moral)
```

### Example 7: Classical Narrative Tafsir for Academic Use
```
User: "Classical narrative tafsir for 18:18 for academic research"

LLM Analysis:
- Verse: "18:18" → surah=18, ayah=18
- Period: "classical" → classical
- Methodology: "narrative" → riwayah
- Purpose: "academic research" → comprehensive, authoritative
- Menhec: classical, riwayah, encyclopedic

Command: python3 scripts/fetch_tafsir.py --verse "18:18" --menhec "classical riwayah encyclopedic"
Result: ar-tafsir-al-tabari (10th-century, riwayah-foundational, encyclopedic)
```

### Example 8: Sufi Tafsir for Spiritual Meaning
```
User: "Sufi tafsir for 55:1-3 with spiritual meanings"

LLM Analysis:
- Verse: "55:1-3" → surah=55, ayah=1-3 (script handles range)
- Methodology: "Sufi" → tasawwuf, ishari
- Focus: "spiritual meanings" → spiritual-allusions
- Menhec: ishari, tasawwuf, spiritual-allusions

Command: python3 scripts/fetch_tafsir.py --verse "55:1-3" --menhec "ishari tasawwuf spiritual-allusions"
Result: en-al-qushairi-tafsir (ishari, tasawwuf, spiritual-allusions)
```

### Example 9: Arabic Language Tafsir
```
User: "Arabic tafsir for Ayat al-Kursi (2:255)"

LLM Analysis:
- Verse: "2:255" → surah=2, ayah=255
- Language: "Arabic" → arabic
- Menhec: arabic, riwayah (default for Arabic)

Command: python3 scripts/fetch_tafsir.py --verse "2:255" --menhec "arabic riwayah"
Result: ar-tafsir-ibn-kathir (arabic, riwayah, hadith-comprehensive)
```

### Example 10: Salafi-Oriented Simple Tafsir
```
User: "Simple Salafi-oriented tafsir for 23:1-11"

LLM Analysis:
- Verse: "23:1-11" → surah=23, ayah=1-11
- School: "Salafi-oriented" → salafi
- Style: "simple" → simplified
- Menhec: salafi, simplified

Command: python3 scripts/fetch_tafsir.py --verse "23:1-11" --menhec "salafi simplified"
Result: ar-tafseer-al-saddi (salafi, simplified, brief-explanation)
```

## 📁 Project Structure

```
tafsir-api-skill/
├── README.md                          # This file
├── SKILL.md                           # OpenClaw skill documentation
├── scripts/
│   ├── fetch_tafsir.py               # Main script (caching, fallback, rate limiting)
│   ├── methodology_matcher.py        # Intelligent menhec matching
│   ├── test_fetch_tafsir.py          # Basic test suite
│   └── test_extended.py              # Extended test suite
└── references/
    ├── tafsir_metadata.json          # 18 tafsir metadata (rich categorization)
    ├── api_reference.md              # API documentation
    ├── tafsir_editions.md            # Tafsir descriptions
    └── llm_prompts.md                # LLM context analysis guide
```

## 🔧 API Reference

### Base URL
```
https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/
```

### Fallback URL
```
https://raw.githubusercontent.com/spa5k/tafsir_api/main/tafsir/
```

### Available Tafsir Slugs
- `en-tafisr-ibn-kathir` - Tafsir Ibn Kathir (abridged)
- `ar-tafsir-ibn-kathir` - Tafsir Ibn Kathir (Arabic)
- `en-tafsir-maarif-ul-quran` - Maarif-ul-Quran
- `ar-tafseer-al-saddi` - Tafseer Al Saddi
- `ar-tafsir-al-baghawi` - Tafseer Al-Baghawi
- ... and 13 more (see references/tafsir_editions.md)

### Response Format
```json
{
  "text": "Tafsir text content...",
  "surah": 2,
  "ayah": 16,
  "tafsir_name": "Tafsir Ibn Kathir (abridged)",
  "author": "Hafiz Ibn Kathir",
  "source": "API endpoint"
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Basic tests
python3 scripts/test_fetch_tafsir.py

# Extended tests (menhec combinations, context analysis)
python3 scripts/test_extended.py

# Individual component tests
python3 -c "from methodology_matcher import normalize_menhec; print(normalize_menhec('rivayet'))"
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Issues**: Found a bug? Open an issue with detailed description
2. **Suggest Features**: Have an idea? Share it in the discussions
3. **Submit PRs**: 
   - Add new tafsir editions to metadata
   - Improve menhec categorization
   - Enhance context analysis algorithms
   - Add tests for edge cases

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/tafsir-api-skill.git
cd tafsir-api-skill

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 scripts/test_fetch_tafsir.py
python3 scripts/test_extended.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tafsir API**: Thanks to [spa5k](https://github.com/spa5k/tafsir_api) for providing the tafsir data
- **OpenClaw Community**: For the amazing platform and support
- **Islamic Scholarship**: To the scholars whose works make this project possible

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/oyilmaztekin/tafsir-api-skill/issues)
- **Discussions**: [GitHub Discussions](https://github.com/oyilmaztekin/tafsir-api-skill/discussions)
- **OpenClaw Community**: [Discord](https://discord.com/invite/clawd)

---

<div align="center">

**Made with ❤️ for the OpenClaw community**

</div>