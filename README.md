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

## 🏗️ Major Design Decisions

### **1. Multi-Brand Scalability with Brand Guidelines**

**Decision**: Create brand guideline templates that are scalable for multiple brands.

**Rationale**:
- **Client Scalability**: System needs to handle multiple luxury fashion brands
- **Brand Consistency**: Each brand has unique tone, voice, and terminology requirements
- **Business Growth**: Easy onboarding of new brands without code changes
- **Template-Based**: Standardized structure that works across different brand types

**Implementation**:
```
config/brand/
├── default/               # Default brand template
├── Newtone/                # Newtone brand specific
├── luxury-brand-x/       # Another brand
└── template/             # Template for new brands
```

**Implementation**:
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

### **2. Brand Glossary System**

**Decision**: Include comprehensive Brand Glossary for consistent terminology translation.

**Rationale**:
- **Brand Voice Consistency**: Each luxury brand has specific terminology that must be translated consistently
- **Quality Control**: Prevent AI from making inconsistent translation choices for key brand terms
- **Business Requirements**: Luxury fashion has specialized vocabulary that requires precise translation
- **Scalable Management**: Glossaries can be updated by business users without code changes

**Implementation**:
```json
{
  "luxury": "luxe",
  "handbag": "sac à main", 
  "craftsmanship": "savoir-faire",
  "premium": "haut de gamme",
  "timeless": "intemporel"
}
```

### **6. Smart Content Protection System**

**Decision**: Protect specific content types from translation using placeholder system.

**Rationale**:
- **Technical Element Protection**: Prevent translation of HTML tags, attributes, and technical markup
- **Brand Asset Protection**: Preserve URLs, email addresses, phone numbers, and brand-specific codes
- **Price and SKU Protection**: Keep pricing, model numbers, and product codes in original language
- **Link Functionality**: Ensure links continue to work after translation

**Protected Content Types**:
- HTML tags and attributes (`<div class="product">`)
- URLs and email addresses (`https://...`, `info@brand.com`)
- Prices and currency (`$299.99`, `€250.00`)
- Brand-specific terms (from DNT list)
- Technical codes and SKUs

**Process**:
1. **Freeze**: Replace protected content with placeholders `⟦PH_1⟧`
2. **Translate**: Send only translatable text to AI
3. **Restore**: Put original protected content back exactly as it was

### **3. HTML DOM Parsing Strategy**

**Decision**: Parse HTML into DOM structure rather than treating it as plain text.

**Rationale**:
- **Prevent HTML Translation**: Don't want the translator to translate `<div>`, `<head>`, `<a>` tags, or other HTML elements
- **Structure Preservation**: Maintain exact HTML structure while translating only text content
- **Link Protection**: Preserve URLs and href attributes exactly as they are
- **Context Awareness**: Extract text segments but keep them in logical context for better AI translation
- **Clean Separation**: Clear distinction between markup and translatable content

**Why This Matters**:
- AI translators will try to translate everything, including HTML tags and attributes
- Links and technical elements must remain functional across languages
- DOM parsing ensures only human-readable text gets translated

**Process**:
1. **Parse**: Convert HTML to DOM structure using BeautifulSoup
2. **Extract**: Pull out text segments while preserving DOM relationships
3. **Translate**: Send only text content to AI, maintaining context
4. **Reconstruct**: Put translated text back into original DOM structure

### **4. Context-Aware Translation Strategy**

**Decision**: Maintain context during translation rather than breaking text into isolated fragments.

**Rationale**:
- **AI Context Dependency**: AI translation models rely heavily on context for accurate translation
- **Coherent Translation**: Breaking text into too-small pieces loses semantic meaning
- **Natural Flow**: Sentences and paragraphs should flow naturally in the target language
- **Quality Priority**: Better to translate larger chunks with context than perfect technical isolation

**Implementation Approach**:
- **Logical Segmentation**: Break content at natural boundaries (paragraphs, sections)
- **Context Preservation**: Keep related text together during translation
- **Smart Reconstruction**: Put translated context back into original structure
- **Format-Specific Logic**: Different strategies for HTML vs Markdown vs plain text

**Why Context Matters**:
```html
<!-- Bad: Fragmented translation -->
<p>Experience the finest</p> → "Vivez le plus fin"
<strong>craftsmanship</strong> → "savoir-faire"

<!-- Good: Contextual translation -->
<p>Experience the finest <strong>craftsmanship</strong></p> 
→ <p>Découvrez le plus fin <strong>savoir-faire</strong></p>
```

### **5. Format Detection and Validation**

**Decision**: Check and validate format in `.txt` and other file types for proper handling.

**Rationale**:
- **Content Classification**: Automatically detect whether content is HTML, Markdown, or plain text
- **Processing Pipeline**: Route content to appropriate parsing strategy based on actual format
- **Error Prevention**: Avoid treating HTML as plain text or vice versa
- **User Experience**: Handle mixed or ambiguous content gracefully

**Detection Logic**:
```python
def detect_format(self, text: str) -> str:
    """Detect format with priority: Markdown > HTML > Text."""
    if self._is_markdown_text(text):
        return "markdown"
    elif self._is_html_text(text):
        return "html" 
    else:
        return "text"
```

**Why This Matters**:
- Files might have wrong extensions (`.txt` file containing HTML)
- Content might be mixed format
- Different formats need completely different processing approaches

### **7. Layered Architecture for Enterprise Scalability**

**Decision**: Implement clean layered architecture with strict dependency rules.

**Rationale**:
- **Multiple Brand Support**: Architecture needs to scale for multiple luxury fashion brands
- **Business Logic Isolation**: Translation rules and brand guidelines are business logic, separate from technical concerns
- **Testing and Quality**: Each layer can be tested independently
- **Future Growth**: Easy to add new interfaces (Web UI, API) without changing core logic

**Architecture Layers**:
```
┌─────────────────────────────────────────┐
│ Presentation (CLI, Future: Web UI)      │  ← User Interfaces
├─────────────────────────────────────────┤
│ Application (Translation Workflows)     │  ← Business Workflows  
├─────────────────────────────────────────┤
│ Domain (Brand Rules, Content Logic)     │  ← Core Business Rules
├─────────────────────────────────────────┤
│ Infrastructure (AI Providers, Storage)  │  ← External Services
└─────────────────────────────────────────┘
```

### **8. Comprehensive Testing Strategy**

**Decision**: Multi-layer testing with realistic fixtures and scenarios.

**Rationale**:
- **Quality Assurance**: Catch issues early in development
- **Regression Prevention**: Ensure changes don't break existing functionality
- **Documentation**: Tests serve as living documentation of expected behavior
- **Confidence**: Enable safe refactoring and feature additions

**Testing Layers**:
- **Unit Tests**: Individual component testing with mocks
- **Integration Tests**: Cross-layer workflow testing
- **Fixture-Based**: Realistic luxury fashion content for testing
- **Mock Providers**: Testing without external API dependencies

### **8. Error Handling and Observability**

**Decision**: Comprehensive logging and graceful error handling.

**Rationale**:
- **Production Readiness**: Handle real-world failure scenarios
- **Debugging Support**: Detailed logs for troubleshooting
- **User Experience**: Graceful degradation when services unavailable
- **Monitoring**: Observable system behavior in production

**Implementation**:
- Structured logging with business context
- Fallback to mock provider when OpenAI unavailable
- Detailed error messages with actionable guidance
- Usage tracking and performance metrics

### **9. Modern Python Development Practices**

**Decision**: Use modern Python tooling and type safety.

**Rationale**:
- **Developer Experience**: Better IDE support and error catching
- **Code Quality**: Type hints improve code documentation and reliability
- **Maintainability**: Modern packaging and dependency management
- **Professional Standards**: Industry best practices for Python development

**Tools & Practices**:
- `pyproject.toml` for modern Python packaging
- Type hints throughout codebase (`py.typed` marker)
- Dataclasses for clean, immutable data models
- Context managers for resource management
- Dependency injection for testability

### **10. Extensibility and Future-Proofing**

**Decision**: Design for easy extension and modification.

**Rationale**:
- **Business Growth**: System can evolve with business needs
- **Technology Changes**: Easy to adopt new translation technologies
- **Feature Additions**: New capabilities can be added without major refactoring
- **Integration Readiness**: Architecture supports future API, web UI, or microservice deployment

**Extension Points**:
- New translation providers
- Additional content formats (PDF, DOCX, etc.)
- Different user interfaces (Web UI, API)
- Additional languages and locales
- Custom business rules and workflows

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
