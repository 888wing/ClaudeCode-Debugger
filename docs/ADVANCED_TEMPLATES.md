# Advanced Template System Documentation

## Overview

The ClaudeCode-Debugger now features an advanced template system with the following capabilities:

1. **Template Inheritance**: Templates can extend base templates and override specific blocks
2. **Template Composition**: Include multiple template fragments
3. **Conditional Logic**: Dynamic content based on error context
4. **Hot Reload**: Templates automatically reload when modified
5. **Multi-language Support**: Templates can specify language preferences
6. **Custom Filters & Functions**: Extended Jinja2 functionality
7. **Template Validation**: Syntax and structure validation
8. **Version Control**: Template versioning and upgrades

## Template Structure

### YAML Format

```yaml
name: Display name for the template
extends: base_template_name  # Optional: inherit from another template
version: "2.0.0"
description: Template description
category: error_category
agent: recommended_agent
tags: [tag1, tag2, tag3]
language: typescript  # Optional: primary language

# Variables that can be used in the template
variables:
  key1: value1
  key2:
    nested: value

# Templates to include
includes:
  - "conditional_include_1"
  - "conditional_include_2"

# Macros for reusable components
macros:
  macro_name: |
    {% macro macro_name(param1, param2) -%}
    Macro content here
    {%- endmacro %}

# Main template content
template: |
  Template content with Jinja2 syntax
```

## Template Inheritance

### Base Template (`base.yaml`)

```yaml
name: Base Debug Template
version: "2.0.0"

template: |
  {% block header %}
  Default header content
  {% endblock %}
  
  {% block content %}
  Default content
  {% endblock %}
  
  {% block footer %}
  Default footer
  {% endblock %}
```

### Child Template

```yaml
name: TypeScript Advanced Template
extends: base
version: "2.0.0"

template: |
  {% extends "base" %}
  
  {% block header %}
  {{ super() }}  {# Include parent content #}
  Additional TypeScript-specific header
  {% endblock %}
  
  {% block content %}
  TypeScript-specific content
  {% endblock %}
```

## Available Filters

### Built-in Custom Filters

- `capitalize_first`: Capitalize first letter
- `format_list`: Format list as bullet points
- `format_code`: Wrap code in markdown code blocks
- `truncate_middle`: Truncate string in the middle
- `to_camel_case`: Convert to camelCase
- `to_snake_case`: Convert to snake_case
- `format_error_code`: Format error code with description
- `severity_color`: Get emoji for severity level
- `format_timestamp`: Format timestamp to readable date
- `pluralize`: Pluralize words based on count
- `file_icon`: Get icon for file type
- `language_name`: Get display name for language

### Usage Examples

```jinja2
{{ error_type|capitalize_first }}
{{ files|format_list }}
{{ code|format_code('typescript') }}
{{ long_path|truncate_middle(50) }}
{{ 'my_variable'|to_camel_case }}  {# myVariable #}
{{ error_code|format_error_code }}  {# TS2322: Type mismatch #}
{{ severity|severity_color }}  {# 🔴 #}
{{ timestamp|format_timestamp }}  {# 2024-01-20 15:30:45 #}
{{ count|pluralize('error', 'errors') }}
{{ 'main.ts'|file_icon }}  {# 📘 #}
{{ 'ts'|language_name }}  {# TypeScript #}
```

## Available Functions

### Custom Functions

- `include_template(name, **kwargs)`: Include another template
- `has_template(name)`: Check if template exists
- `get_template_var(template_name, var_name, default)`: Get variable from template
- `format_stack_trace(trace, max_frames)`: Format stack trace
- `suggest_fix(error_type, error_code)`: Get fix suggestions
- `get_related_errors(error_type, error_code)`: Get related error codes

### Usage Examples

```jinja2
{{ include_template('error_hints', error_type=error_type) }}

{% if has_template('typescript_helpers') %}
  {{ include_template('typescript_helpers') }}
{% endif %}

{{ format_stack_trace(stack_trace, 15) }}

{% for suggestion in suggest_fix('typescript', 'TS2322') %}
- {{ suggestion }}
{% endfor %}
```

## Conditional Logic

### Basic Conditionals

```jinja2
{% if error_type == 'typescript' %}
  TypeScript-specific content
{% elif error_type == 'python' %}
  Python-specific content
{% else %}
  Generic content
{% endif %}
```

### Advanced Conditionals

```jinja2
{% if 'react' in error_text.lower() and error_type == 'typescript' %}
  React + TypeScript specific help
{% endif %}

{% if error_count > 10 %}
  ⚠️ Large number of errors detected!
{% endif %}

{% if severity == 'critical' %}
  🚨 CRITICAL ERROR - Immediate action required!
{% endif %}
```

## Template Management CLI

### List Templates

```bash
# List all templates
ccdebug template list

# List with details
ccdebug template list --details

# Filter by category
ccdebug template list --category typescript
```

### Show Template

```bash
# Show rendered preview
ccdebug template show typescript_advanced

# Show raw YAML
ccdebug template show typescript_advanced --raw
```

### Create Template

```bash
# Create new template
ccdebug template create my_template

# Create extending existing template
ccdebug template create my_template --base typescript_advanced
```

### Edit Template

```bash
# Edit template (opens in $EDITOR)
ccdebug template edit my_template
```

### Test Template

```bash
# Test with sample data
ccdebug template test typescript_advanced

# Test with custom data file
ccdebug template test typescript_advanced --sample data.json
```

### Import/Export Templates

```bash
# Export template
ccdebug template export typescript_advanced output.yaml

# Import template
ccdebug template import custom_template.yaml

# Share template (creates package)
ccdebug template share typescript_advanced
```

## Creating Custom Templates

### Step 1: Create Template File

Create a file in `~/.ccdebug/templates/my_template.yaml`:

```yaml
name: My Custom Template
version: "1.0.0"
description: Custom template for specific errors
category: custom
agent: debug-specialist
tags: [custom, specific]

variables:
  my_var: "default value"
  
template: |
  # 🚨 {{ error_type_display }} Debug
  
  ## Custom Analysis
  This is my custom template for {{ error_type }} errors.
  
  {% if files %}
  ### Affected Files:
  {% for file in files %}
  - {{ file_icon(file) }} `{{ file }}`
  {% endfor %}
  {% endif %}
  
  ## My Custom Sections
  Add your custom content here...
```

### Step 2: Test Template

```bash
ccdebug template test my_template
```

### Step 3: Use Template

The template will be automatically picked up based on error type matching.

## Advanced Features

### Hot Reload

Templates are automatically reloaded when modified. Set `CCDEBUG_NO_WATCH=true` to disable.

### Template Validation

Templates are validated for:
- Required fields (name, template)
- Jinja2 syntax errors
- Undefined variables
- Circular dependencies
- Invalid inheritance

### Multi-language Support

Templates can specify language and use language-specific content:

```yaml
language: zh  # Chinese

template: |
  {% if _template.language == 'zh' %}
  ## 错误分析
  {% else %}
  ## Error Analysis
  {% endif %}
```

### Template Caching

Templates are cached in memory with TTL. Cache is invalidated on:
- File modification
- Dependency changes
- Manual reload

### Version Control

Templates include version information for upgrades:

```yaml
version: "2.0.0"
# Version format: MAJOR.MINOR.PATCH
```

## Best Practices

1. **Use Inheritance**: Extend base templates for consistency
2. **Modular Design**: Create small, reusable template fragments
3. **Clear Naming**: Use descriptive template names
4. **Document Variables**: List all expected variables
5. **Test Thoroughly**: Test with various error scenarios
6. **Version Properly**: Update version on changes
7. **Use Categories**: Organize templates by error type
8. **Leverage Filters**: Use custom filters for formatting
9. **Handle Edge Cases**: Add conditionals for edge cases
10. **Provide Examples**: Include fix examples in templates

## Examples

### Framework-Specific Template

```yaml
name: React TypeScript Error Template
extends: typescript_advanced
version: "2.0.0"
category: typescript
subcategory: react
tags: [react, typescript, jsx, hooks]

template: |
  {% extends "typescript_advanced" %}
  
  {% block analysis_content %}
  {{ super() }}
  
  ## React-Specific Analysis
  
  {% if 'hook' in error_text.lower() %}
  ### Hook Rules Violation Check:
  - Ensure hooks are called at the top level
  - Verify hooks are not called conditionally
  - Check hook dependencies array
  {% endif %}
  
  {% if 'props' in error_text.lower() %}
  ### Props Type Check:
  - Verify prop types match component definition
  - Check for missing required props
  - Validate prop spreading
  {% endif %}
  {% endblock %}
```

### Multi-Stage Debug Template

```yaml
name: Progressive Debug Template
version: "2.0.0"

template: |
  # Debug Plan
  
  ## Stage 1: Quick Checks
  {% include 'quick_checks' %}
  
  ## Stage 2: Deep Analysis
  {% if error_count > 5 or severity == 'critical' %}
  {% include 'deep_analysis' %}
  {% endif %}
  
  ## Stage 3: Resolution
  {% include 'resolution_steps' %}
  
  ## Stage 4: Prevention
  {% if include_prevention|default(true) %}
  {% include 'prevention_measures' %}
  {% endif %}
```

## Troubleshooting

### Template Not Loading

1. Check file location: `~/.ccdebug/templates/`
2. Verify YAML syntax: `yamllint template.yaml`
3. Check template name conflicts
4. Review error logs

### Template Syntax Errors

1. Validate Jinja2 syntax
2. Check variable names
3. Verify block names match parent
4. Test with minimal template

### Performance Issues

1. Reduce template complexity
2. Minimize includes
3. Enable caching
4. Optimize conditionals