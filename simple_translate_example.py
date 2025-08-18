#!/usr/bin/env python3
import json
import os
import re
from typing import Dict, List, Tuple
import openai
from bs4 import BeautifulSoup


def translate_content(text: str, target_lang: str, openai_api_key: str = None) -> str:
    """
    Core translation workflow - the main function everything else builds around.
    
    This is the essence of what the system does:
    1. Detect if it's HTML, Markdown, or plain text
    2. If HTML: parse DOM, extract text segments, preserve structure  
    3. Protect important content (URLs, prices, etc.) with placeholders
    4. Send to OpenAI with proper context
    5. Put translated text back into original structure
    6. Restore protected content
    
    Args:
        text: Content to translate
        target_lang: Target language (fr, es, de, etc.)
        openai_api_key: OpenAI API key (optional, uses env var if not provided)
        
    Returns:
        Translated content with original structure preserved
    """
    
    # Step 1: Set up OpenAI client
    api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        # Fallback to mock translation for testing
        return f"[MOCK {target_lang.upper()}] {text}"
    
    client = openai.OpenAI(api_key=api_key)
    
    # Step 2: Detect content format
    content_format = detect_format(text)
    print(f"Detected format: {content_format}")
    
    # Step 3: Process based on format
    if content_format == "html":
        return translate_html(text, target_lang, client)
    elif content_format == "markdown":
        return translate_markdown(text, target_lang, client)
    else:
        return translate_text(text, target_lang, client)


def detect_format(text: str) -> str:
    """Detect if content is HTML, Markdown, or plain text."""
    # Check for HTML tags
    if re.search(r'<[^>]+>', text):
        return "html"
    
    # Check for Markdown patterns
    markdown_patterns = [
        r'^#+\s+',           # Headers
        r'\*\*[^*]+\*\*',    # Bold
        r'\*[^*]+\*',        # Italic  
        r'\[([^\]]+)\]\(([^)]+)\)',  # Links
    ]
    if any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns):
        return "markdown"
    
    return "text"


def translate_html(html_text: str, target_lang: str, client) -> str:
    """
    Translate HTML while preserving structure.
    
    Key insight: Parse as DOM, extract only text content for translation,
    keep HTML tags and attributes untouched.
    """
    # Parse HTML into DOM
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Extract text segments while preserving DOM structure
    text_segments = []
    segment_id = 1
    
    # Find all text nodes that aren't just whitespace
    for element in soup.find_all(text=True):
        text_content = element.strip()
        if text_content and text_content not in ['', '\n', '\t']:
            # Protect important content before translation
            protected_text, placeholders = protect_content(text_content)
            text_segments.append({
                'id': f'seg_{segment_id}',
                'original': text_content,
                'protected': protected_text,
                'placeholders': placeholders,
                'element': element
            })
            segment_id += 1
    
    # Translate all segments with context
    if text_segments:
        # Combine segments for context but track individually
        segments_for_translation = [seg['protected'] for seg in text_segments]
        translations = translate_segments_with_context(segments_for_translation, target_lang, client)
        
        # Replace text in DOM with translations
        for i, segment in enumerate(text_segments):
            if i < len(translations):
                # Restore protected content
                translated_text = restore_protected_content(
                    translations[i], 
                    segment['placeholders']
                )
                segment['element'].replace_with(translated_text)
    
    return str(soup)


def translate_markdown(md_text: str, target_lang: str, client) -> str:
    """Translate Markdown while preserving formatting."""
    # For MVP: treat as single chunk to preserve context
    protected_text, placeholders = protect_content(md_text)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Translate the following Markdown to {target_lang}. Preserve all Markdown formatting exactly."},
            {"role": "user", "content": protected_text}
        ],
        temperature=0.2
    )
    
    translated = response.choices[0].message.content
    return restore_protected_content(translated, placeholders)


def translate_text(plain_text: str, target_lang: str, client) -> str:
    """Translate plain text."""
    protected_text, placeholders = protect_content(plain_text)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": f"Translate to {target_lang}. Keep the same tone and style."},
            {"role": "user", "content": protected_text}
        ],
        temperature=0.2
    )
    
    translated = response.choices[0].message.content
    return restore_protected_content(translated, placeholders)


def protect_content(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Protect URLs, emails, prices, etc. from translation.
    
    This is crucial - AI will try to translate everything including
    technical elements that should stay exactly as they are.
    """
    placeholders = {}
    protected_text = text
    placeholder_counter = 1
    
    # Protect URLs
    url_pattern = r'https?://[^\s\'"<>]+'
    for match in re.finditer(url_pattern, text):
        placeholder = f"⟦URL_{placeholder_counter}⟧"
        placeholders[placeholder] = match.group()
        protected_text = protected_text.replace(match.group(), placeholder)
        placeholder_counter += 1
    
    # Protect email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    for match in re.finditer(email_pattern, protected_text):
        placeholder = f"⟦EMAIL_{placeholder_counter}⟧"
        placeholders[placeholder] = match.group()
        protected_text = protected_text.replace(match.group(), placeholder)
        placeholder_counter += 1
    
    # Protect prices and currency
    price_pattern = r'[$€£¥]\d+(?:\.\d{2})?'
    for match in re.finditer(price_pattern, protected_text):
        placeholder = f"⟦PRICE_{placeholder_counter}⟧"
        placeholders[placeholder] = match.group()
        protected_text = protected_text.replace(match.group(), placeholder)
        placeholder_counter += 1
    
    return protected_text, placeholders


def restore_protected_content(translated_text: str, placeholders: Dict[str, str]) -> str:
    """Restore protected content in translated text."""
    restored_text = translated_text
    for placeholder, original in placeholders.items():
        restored_text = restored_text.replace(placeholder, original)
    return restored_text


def translate_segments_with_context(segments: List[str], target_lang: str, client) -> List[str]:
    """
    Translate segments while maintaining context.
    
    Key insight: Don't break text into tiny pieces that lose meaning.
    Give AI enough context to make good translation decisions.
    """
    # For small number of segments, translate together for context
    if len(segments) <= 5:
        combined_text = '\n---\n'.join(segments)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate to {target_lang}. Each segment is separated by '---'. Return translations in the same order, separated by '---'."},
                {"role": "user", "content": combined_text}
            ],
            temperature=0.2
        )
        
        translated_combined = response.choices[0].message.content
        return translated_combined.split('---')
    
    # For larger content, translate individually but with more context
    translations = []
    for segment in segments:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate to {target_lang}. Maintain professional tone suitable for luxury fashion."},
                {"role": "user", "content": segment}
            ],
            temperature=0.2
        )
        translations.append(response.choices[0].message.content)
    
    return translations


# Example usage
if __name__ == "__main__":
    # Test with HTML content
    html_content = '''
    <div class="product">
        <h1>Luxury Handbag Collection</h1>
        <p>Experience the finest <strong>craftsmanship</strong> with our exclusive handbags.</p>
        <a href="https://example.com/shop">Shop Now</a>
        <div class="price">Price: $599.99</div>
    </div>
    '''
    
    print("Original HTML:")
    print(html_content)
    print("\nTranslated to French:")
    result = translate_content(html_content, "fr")
    print(result)
    
    # Test with plain text
    text_content = "Welcome to our luxury fashion boutique. We offer premium quality items."
    print(f"\nOriginal text: {text_content}")
    print(f"Translated to Spanish: {translate_content(text_content, 'es')}")
