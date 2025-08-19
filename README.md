# Newtone Translation System

An AI translation system built with **layered architecture** for luxury fashion retailers. Provides brand-consistent, ready-to-publish translations while preserving HTML/Markdown formatting.

## 🏗️ Architecture

This project follows **pure layered architecture** principles:

```
┌─────────────────────────────────────────┐
│ Presentation Layer (CLI, Future: API)   │  ← User Interfaces
├─────────────────────────────────────────┤
│ Application Layer (Services)            │  ← Business Workflows
├─────────────────────────────────────────┤ 
│ Domain Layer (Business Logic)           │  ← Core Business Rules
├─────────────────────────────────────────┤
│ Infrastructure (Providers, Storage)     │  ← External Services
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/newtone/newtone-translate.git
cd newtone-translate

# Install dependencies
pip install -e .

# Set up OpenAI API key (optional - falls back to mock provider)
export OPENAI_API_KEY="your-api-key"
```

### Basic Usage

```bash
# Translate a file
python newtone_translate.py data/input/html/example.html fr

# Translate text directly
python newtone_translate.py "Hello world" es

# Using as module
newtone-translate translate --input data/input/html/example.html --target fr
```


## 🏗️ Design Decisions Overview

This section documents the major design choices made in the Newtone translation system. Each decision was evaluated against business requirements, scalability goals, and long-term maintainability of the system. The following outlines both the rationale for the choices made and why alternative approaches were not pursued.

### **1. Layered Architecture**

The layered architecture was chosen for its ability to separate business logic, infrastructure, and presentation layers. This enables both short-term developer productivity and long-term extensibility.

**Primary Drivers**

- **Business domain complexity**: Multi-brand support, format preservation, and brand consistency rules require clear isolation of business logic.
- **Enterprise scalability**: New translation providers can be integrated without changing business logic.
- **Flexible interfaces**: Currently exposes a CLI, but future Web UI and REST API layers can be added without rewriting core translation logic.

**Rejected Alternatives**

- **Microservices**: Too complex for MVP, unnecessary operational overhead.
- **Event-driven**: Translation is request-response, not asynchronous.
- **Monolithic script**: Initial prototype evolved beyond a single function into structured layers.

### **2. Freeze–Restore Pattern for Critical Content**

**Decision**
Implement a "freeze–restore" mechanism that protects specific placeholders, tags, and metadata from being translated.

**Rationale**

- Prevents corruption of HTML tags, brand names, SKUs, and DNT (Do Not Translate) terms.
- Allows translators and providers to work with clean text without losing contextual markers.
- Guarantees reliable restoration after translation.

### **3. Format Detection Beyond File Extensions**

**Decision**
Content format is detected based on actual file content, not file extension.

**Rationale**

- Users often mislabel files (e.g., .txt containing HTML).
- Ensures correct pipeline selection regardless of extension.
- Improves reliability and reduces errors in automated workflows.

### **4. Specialized Pipelines for Different Content Types**

**Decision**
Translation processing pipelines vary between HTML and Markdown/Text.

**HTML Processing**

- **DOM-aware**: Preserves full structure.
- **Segment extraction**: Each text node becomes a separate segment.
- **Context preservation**: Parent-child relationships maintained.
- **Fragment vs Document**: Works with both snippets and full documents.

**Markdown/Text Processing**

- **Single segment**: Treated as one unit for coherence.
- **Simpler pipeline**: Minimal structural preservation needed.
- **Faster processing**: Lower API call volume.

### **5. Keeping Related Content Together for Context**

**Decision**
Wherever possible, related content (e.g., sentences in the same paragraph, glossary references) is grouped and translated together.

**Rationale**

- Large Language Models perform better when given full context.
- Improves consistency across segments.
- Reduces risk of semantic drift when content is split unnecessarily.

### **6. Multi-Brand Strategy Through Configuration**

**Decision**
Brand guidelines, glossaries, and DNT terms are loaded from configuration rather than code.

**Rationale**

- Supports multi-brand scalability without code changes.
- New brands can be onboarded by providing configuration files.
- Maintains strict adherence to each brand's style guide and terminology.

## Feasibility Assessment

1. **Technical Feasibility**

   - **Core capability**: Current LLMs (e.g., GPT-4, Claude, DeepL’s API) can produce natural-sounding translations that are often close to human quality. This suggests the translation engine is technically viable.
   - **Format handling**: HTML and Markdown preservation is feasible using a freeze–restore approach (protect tags, placeholders, etc.) which I implemented in the MVP.
   - **Multi-brand consistency**: Achievable through configuration-driven glossaries, style guides, and DNT (Do Not Translate) terms. Requires careful prompt-engineering or fine-tuning.
   - **Pipeline scalability**: The layered architecture allows adding new providers or scaling to different interfaces (CLI now, REST API/Web UI later).

2. **Business Feasibility**

   - **Market fit**: Luxury fashion retailers have strong need for consistent, high-quality translations with brand fidelity. AI-based translation products already exist, but differentiation lies in ready-to-publish quality and brand customization.
   - **Client willingness**: Early discovery shows clients are already paying high translation costs, indicating clear budget and willingness to switch if quality is sufficient.

3. **Operational Feasibility**

   - **Latency**: LLM-based translations can be slower than traditional MT engines (e.g., Google Translate), but for luxury fashion, quality is more important than speed. Acceptable if processing can be batched or parallelized.
   - **Costs**: Translation via LLM APIs can be expensive depending on content length and volume. Strategies like batching requests, caching, or selectively using premium providers may help.
   - **Data handling**: Some clients may require strict data security (fashion houses are sensitive to IP leaks). This may necessitate on-prem models or private endpoints in the future.

---

**Potential Complications**

1. **Quality Assurance**
   - LLM translations sometimes “hallucinate” or over-interpret content.
   - Brand-specific tone may be inconsistent without ongoing glossary/style enforcement.
2. **Format Preservation**
   - Edge cases in HTML/Markdown (nested tags, broken markup) could cause incorrect freezing/restoring.
   - Continuous testing required.
3. **Evaluation Loop**
   - Human-in-the-loop quality evaluation might be necessary for initial deployments until confidence in automation grows.

## 📁 Project Structure

```
newtone-translate/
├── src/newtone_translate/          # Source code (layered architecture)
│   ├── presentation/               # CLI, API interfaces
│   ├── application/                # Business workflows & services
│   ├── domain/                     # Core business logic
│   └── infrastructure/             # External services & storage
├── config/                         # Configuration files
├── data/                           # Input/output data
├── tests/                          # Comprehensive test suite
├── docs/                           # Documentation
└── scripts/                        # Utility scripts
```

## 🎯 Key Features

- **Format Preservation**: Maintains HTML/Markdown structure perfectly
- **Brand Consistency**: Configurable glossaries and style guides
- **Smart Placeholders**: Protects URLs, emails, brand terms from translation
- **Multiple Providers**: OpenAI, Mock (extensible to other services)
- **Professional Architecture**: Layered design for enterprise scalability

## 🔧 Configuration

Configuration is managed in `config/settings.yaml`:

```yaml
providers:
  default: "openai"
  openai:
    model: "gpt-4o-mini"
    temperature: 0.2

translation:
  default_target_language: "fr"
  preserve_formatting: true
```

Brand-specific settings in `config/brand/default/`:
- `glossary.json` - Translation glossary
- `brand_guidelines.json` - Style guidelines  
- `dnt.json` - Do Not Translate terms

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

## 📊 Architecture Benefits

### Layered Architecture Advantages:
1. **Clear Separation**: Each layer has single responsibility
2. **Easy Testing**: Layers can be tested independently
3. **Scalability**: Add new formats/providers without changing core logic
4. **Maintainability**: Changes isolated to specific layers
5. **Professional**: Industry-standard enterprise pattern

### Layer Responsibilities:
- **Presentation**: User interaction (CLI, future API)
- **Application**: Workflow orchestration and service coordination
- **Domain**: Pure business logic (no external dependencies)
- **Infrastructure**: External services (OpenAI, file storage, logging)

## 🚀 Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```
