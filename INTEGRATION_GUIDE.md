# ClaudeCode-Debugger Integration Guide

This guide explains how all the advanced components work together in ClaudeCode-Debugger v0.2.0.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐         │
│  │   Legacy    │  │   Enhanced   │  │    Template    │         │
│  │    CLI      │  │     CLI      │  │    Manager     │         │
│  └─────────────┘  └──────────────┘  └────────────────┘         │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────┴───────────────────────────────┐
│                         Core Components                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐         │
│  │  Advanced   │  │   Advanced   │  │    Plugin      │         │
│  │  Detector   │  │  Generator   │  │    System      │         │
│  └─────────────┘  └──────────────┘  └────────────────┘         │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────┴───────────────────────────────┐
│                        Support Systems                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐         │
│  │   History   │  │    Config    │  │       ML       │         │
│  │   Manager   │  │   Manager    │  │   Classifier   │         │
│  └─────────────┘  └──────────────┘  └────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Integration

### 1. Main Entry Point (`main.py`)

The main entry point orchestrates all components:

```python
# Initialize all components
components = {
    'config': Config(),
    'history': HistoryManager(),
    'plugins': PluginManager(),
    'detector': AdvancedErrorDetector(),
    'generator': AdvancedPromptGenerator()
}

# Route to appropriate CLI
if use_legacy:
    legacy_cli()
else:
    enhanced_cli(**components)
```

### 2. Enhanced CLI Flow

```python
# 1. Parse command and options
@click.command()
def analyze(error_text, **options):
    # 2. Load configuration
    config = ctx.obj['config']
    
    # 3. Apply plugins pre-processing
    error_text = plugins.pre_process(error_text)
    
    # 4. Detect error type
    detection = detector.detect_multi_label(error_text)
    
    # 5. Generate prompt
    prompt = generator.generate(
        error_text,
        detection,
        template=select_best_template(detection)
    )
    
    # 6. Apply plugins post-processing
    prompt = plugins.post_process(prompt)
    
    # 7. Save to history
    history.add_entry(error_text, detection, prompt)
    
    # 8. Display results
    display_results(prompt, format=options['format'])
```

### 3. Advanced Error Detection Flow

```python
# Multi-stage detection process
def detect_advanced(error_text):
    # Stage 1: Pattern matching
    pattern_results = pattern_matcher.match(error_text)
    
    # Stage 2: ML classification (if enabled)
    if config.ml_enabled:
        ml_results = ml_classifier.predict(error_text)
        
    # Stage 3: Combine results
    combined = combine_results(pattern_results, ml_results)
    
    # Stage 4: Extract metadata
    metadata = extract_metadata(error_text)
    
    return {
        'categories': combined,
        'metadata': metadata,
        'confidence': calculate_confidence(combined)
    }
```

### 4. Template System Integration

```python
# Template selection and rendering
def generate_prompt(error_data):
    # 1. Select best template
    template = template_selector.select(
        error_data['categories'],
        error_data['metadata']
    )
    
    # 2. Load template with inheritance
    template_data = template_loader.load(template)
    
    # 3. Prepare context
    context = {
        **error_data,
        'config': config.get_template_config(),
        'history': history.get_similar_errors(error_data)
    }
    
    # 4. Render template
    prompt = template_engine.render(template_data, context)
    
    return prompt
```

### 5. Plugin System Integration

```python
# Plugin lifecycle
class PluginManager:
    def load_plugins(self):
        # Load built-in plugins
        self.load_builtin_plugins()
        
        # Load user plugins
        self.load_user_plugins()
        
        # Initialize plugins
        for plugin in self.plugins:
            plugin.initialize(self.context)
    
    def process_error(self, error_data):
        # Run plugins in order
        for plugin in self.enabled_plugins:
            error_data = plugin.process_error(error_data)
        
        return error_data
```

## Data Flow Example

Here's how data flows through the system for a typical error analysis:

```
User Input: "TypeError: Cannot read property 'name' of undefined"
    ↓
CLI Parser
    ├─→ Configuration Load
    ├─→ Plugin Pre-processing
    │     └─→ Clean and normalize input
    ↓
Advanced Detector
    ├─→ Pattern Matching
    │     └─→ Categories: ['javascript', 'runtime']
    ├─→ ML Classification
    │     └─→ Confidence: 0.92
    ├─→ Metadata Extraction
    │     └─→ Files: [], Lines: [], Type: 'TypeError'
    ↓
Template Selector
    ├─→ Find Best Match
    │     └─→ Selected: 'javascript_advanced.yaml'
    ├─→ Load with Inheritance
    │     └─→ Base → JavaScript → JavaScript Advanced
    ↓
Prompt Generator
    ├─→ Context Preparation
    ├─→ Template Rendering
    ├─→ Macro Expansion
    ↓
Plugin Post-processing
    ├─→ Stack Trace Enhancement
    ├─→ Git Context Addition
    ├─→ Similar Error Suggestions
    ↓
Output Formatter
    ├─→ Rich Console Display
    ├─→ History Save
    └─→ Clipboard Copy
```

## Configuration Integration

All components share a unified configuration:

```yaml
# ~/.ccdebug/config.yaml
general:
  theme: dark
  auto_copy: true
  default_format: rich

detector:
  ml_enabled: true
  confidence_threshold: 0.7
  custom_patterns_dir: ~/.ccdebug/patterns

templates:
  custom_dir: ~/.ccdebug/templates
  cache_enabled: true
  hot_reload: true

plugins:
  enabled:
    - stack_trace_analyzer
    - git_context
  custom_dir: ~/.ccdebug/plugins

history:
  max_entries: 10000
  retention_days: 90
```

## Performance Optimization

### 1. Lazy Loading
```python
# Components are loaded only when needed
@property
def ml_classifier(self):
    if not self._ml_classifier:
        self._ml_classifier = MLClassifier()
    return self._ml_classifier
```

### 2. Caching
```python
# Template cache
@lru_cache(maxsize=100)
def load_template(template_name):
    return template_loader.load(template_name)

# Pattern cache
compiled_patterns = {}
```

### 3. Parallel Processing
```python
# Batch processing with multiprocessing
def process_batch(files):
    with Pool() as pool:
        results = pool.map(analyze_file, files)
    return results
```

## Testing Integration

### Unit Tests
Each component has its own test suite:
- `test_advanced_detector.py`
- `test_advanced_generator.py`
- `test_cli_enhanced.py`
- `test_plugins.py`

### Integration Tests
```python
def test_full_flow():
    # Test complete error analysis flow
    error = "TS2322: Type error"
    result = analyze_error(error)
    
    assert result.detection.categories == ['typescript']
    assert result.prompt.contains("TypeScript")
    assert result.history_saved
```

### End-to-End Tests
```bash
# Test CLI commands
def test_cli_e2e():
    result = runner.invoke(cli, ['analyze', 'error'])
    assert result.exit_code == 0
    assert 'Debug' in result.output
```

## Debugging Integration Issues

### Enable Debug Mode
```bash
export CCDEBUG_DEBUG=1
ccdebug analyze "error"
```

### Check Component Status
```bash
ccdebug status
# Shows:
# - Loaded plugins
# - Active templates
# - ML model status
# - Configuration
```

### Trace Execution
```bash
ccdebug analyze "error" --trace
# Shows step-by-step execution
```

## Best Practices

### 1. Component Independence
Each component should work independently:
```python
# Good
detector = AdvancedErrorDetector()
result = detector.detect(error)  # Works standalone

# Bad
detector = AdvancedErrorDetector(generator, plugins)  # Too coupled
```

### 2. Configuration Validation
Always validate configuration:
```python
def load_config():
    config = Config()
    config.validate()  # Throws if invalid
    return config
```

### 3. Error Handling
Handle errors gracefully:
```python
try:
    result = detector.detect(error)
except DetectionError:
    # Fallback to basic detection
    result = basic_detect(error)
```

### 4. Plugin Isolation
Plugins shouldn't break the system:
```python
def run_plugin(plugin, data):
    try:
        return plugin.process(data)
    except Exception as e:
        logger.error(f"Plugin {plugin.name} failed: {e}")
        return data  # Return unmodified
```

## Extending the System

### Adding New Error Types
1. Add patterns to `AdvancedErrorDetector`
2. Create template in `templates/advanced/`
3. Add tests
4. Update documentation

### Creating Plugins
1. Inherit from `PluginBase`
2. Implement required methods
3. Place in `~/.ccdebug/plugins/`
4. Enable in configuration

### Custom Templates
1. Create YAML template
2. Use inheritance for consistency
3. Test with `ccdebug template test`
4. Share with community

## Conclusion

The integrated system provides:
- 🚀 High performance through optimization
- 🔧 Extensibility through plugins
- 🎨 Customization through templates
- 📊 Intelligence through ML
- 🏗️ Maintainability through modular design

All components work together seamlessly while remaining independent and testable.