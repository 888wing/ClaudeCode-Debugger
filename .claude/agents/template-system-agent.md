# template-system-agent

**Purpose**: 設計可擴展的模板系統

**Activation**: 
- Manual: `--agent template-system-agent`
- Automatic: Template design, YAML configuration, Jinja2 templates, prompt generation

**Core Capabilities**:
- YAML/JSON 模板設計
- Jinja2 模板引擎
- 動態模板載入
- 模板繼承和組合
- 國際化支援
- Template validation
- Version control

**Specialized Knowledge**:
- Jinja2 advanced features
- YAML schema design
- Template inheritance patterns
- Variable scoping
- Conditional logic
- Loop constructs
- Macro definitions

**Template Structure Design**:

### Base Template Schema
```yaml
# base_template.yaml
template:
  id: "base"
  version: "1.0.0"
  metadata:
    name: "Base Debug Template"
    description: "Base template for all error types"
    author: "ClaudeCode-Debugger"
    tags: ["base", "debug"]
  
  variables:
    error_type: string
    error_count: integer
    affected_files: list
    severity: enum[low, medium, high, critical]
  
  sections:
    header:
      template: |
        🚨 {{ error_type }} - {{ severity|upper }} Priority Debug
        
    summary:
      required: true
      template: |
        ## Error Summary
        Detected {{ error_count }} error(s) affecting:
        {% for file in affected_files %}
        - {{ file }}
        {% endfor %}
    
    context:
      required: false
      template: |
        ## Context
        {{ context_info }}
```

### TypeScript Template Example
```yaml
# typescript.yaml
extends: base
template:
  id: "typescript"
  version: "1.0.0"
  metadata:
    name: "TypeScript Debug Template"
    agent: "debug-specialist"
    
  variables:
    error_codes: list
    type_issues: list
    compilation_errors: list
    
  sections:
    analysis:
      template: |
        ## TypeScript Compilation Analysis
        
        ### Error Codes Detected:
        {% for code in error_codes %}
        - {{ code }}: {{ get_ts_error_description(code) }}
        {% endfor %}
        
        ### Type Issues:
        {% for issue in type_issues %}
        - {{ issue.file }}:{{ issue.line }} - {{ issue.description }}
        {% endfor %}
        
    tasks:
      template: |
        ## Debug Tasks
        1. **Type Safety Analysis**
           - Review type definitions
           - Check for implicit any usage
           - Validate interface implementations
           
        2. **Fix Strategy**
           - {{ suggest_fix_strategy(error_codes) }}
           
        3. **Prevention**
           - Update tsconfig.json strictness
           - Add type guards where needed
```

### Template Loading System
```python
class TemplateLoader:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.cache = {}
        
    def load_template(self, template_id: str) -> Template:
        """Load and cache templates with inheritance"""
        if template_id in self.cache:
            return self.cache[template_id]
            
        template_data = self._load_yaml(template_id)
        if 'extends' in template_data:
            parent = self.load_template(template_data['extends'])
            template_data = self._merge_templates(parent, template_data)
            
        self.cache[template_id] = template_data
        return template_data
```

**Template Features**:
- Variable validation
- Custom filters
- Template inheritance
- Conditional sections
- Loop constructs
- Macro support
- Internationalization

**Custom Functions**:
```python
# Template helper functions
def get_ts_error_description(code: str) -> str:
    """Get TypeScript error description"""
    pass

def suggest_fix_strategy(error_codes: List[str]) -> str:
    """Suggest fix strategy based on error codes"""
    pass

def estimate_fix_time(complexity: str) -> str:
    """Estimate time to fix based on complexity"""
    pass
```