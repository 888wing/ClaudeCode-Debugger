# AGENTS.md - ClaudeCode-Debugger Sub-Agent Registry

Registry of specialized sub-agents for the ClaudeCode-Debugger project.

## Overview

These sub-agents are specialized AI configurations designed for specific aspects of building and maintaining the ClaudeCode-Debugger tool. They can be activated manually or automatically based on context and requirements.

## Available Sub-Agents

### project-setup-agent

**Purpose**: Initialize and structure open-source Python CLI projects with best practices.

**Activation**: 
- Manual: `--agent project-setup-agent`
- Automatic: Project initialization, setup.py creation, CI/CD configuration

**Core Capabilities**:
- Standard Python project structure creation
- CI/CD pipeline configuration (GitHub Actions)
- Testing framework setup (pytest)
- Documentation templates generation
- Release process automation

**Integration Points**:
- Works with test-documentation-agent for comprehensive docs
- Coordinates with cli-developer-agent for entry points
- Integrates with DevOps persona for CI/CD

### cli-developer-agent

**Purpose**: Expert in developing command-line interface tools with excellent UX.

**Activation**: 
- Manual: `--agent cli-developer-agent`
- Automatic: CLI development, Click framework usage, interactive CLI features

**Core Capabilities**:
- Click framework expertise
- Rich library for beautiful output
- Command-line argument design
- Interactive CLI development
- Error handling and user experience
- Progress indicators and spinners

**Integration Points**:
- Works with error-pattern-agent for error handling
- Coordinates with template-system-agent for output formatting
- Integrates with Frontend persona for UX design

### error-pattern-agent

**Purpose**: Design and implement sophisticated error detection systems.

**Activation**: 
- Manual: `--agent error-pattern-agent`
- Automatic: Error detection, pattern matching, regex design, log analysis

**Core Capabilities**:
- Regular expression expertise
- Multi-language error pattern recognition
- Machine learning classifier design
- Error feature extraction
- Pattern matching optimization
- Large log file processing

**Specialized Knowledge**:
- TypeScript/JavaScript error patterns
- Python exception patterns
- Memory and performance error patterns
- Network and API error patterns
- Framework-specific error signatures

### template-system-agent

**Purpose**: Design extensible template systems for prompt generation.

**Activation**: 
- Manual: `--agent template-system-agent`
- Automatic: Template design, YAML configuration, Jinja2 templates

**Core Capabilities**:
- YAML/JSON template design
- Jinja2 template engine expertise
- Dynamic template loading
- Template inheritance and composition
- Internationalization support
- Template validation

**Integration Points**:
- Works with ai-integration-agent for dynamic content
- Coordinates with plugin-system-agent for extensibility
- Leverages Scribe persona for content quality

### ai-integration-agent

**Purpose**: Implement intelligent analysis and recommendation features.

**Activation**: 
- Manual: `--agent ai-integration-agent`
- Automatic: AI analysis, similarity matching, recommendation systems

**Core Capabilities**:
- Error similarity calculation
- Historical data analysis
- Solution recommendation systems
- Context enhancement
- Learning system design
- Success rate tracking

**Specialized Knowledge**:
- Text similarity algorithms
- Machine learning for classification
- Recommendation algorithms
- Performance metrics
- Continuous learning systems

### test-documentation-agent

**Purpose**: Ensure code quality and comprehensive documentation.

**Activation**: 
- Manual: `--agent test-documentation-agent`
- Automatic: Test creation, documentation writing, coverage analysis

**Core Capabilities**:
- Unit test design (pytest)
- Integration testing
- Documentation generation
- Usage examples creation
- CI/CD configuration
- Coverage reporting

**Integration Points**:
- Works with project-setup-agent for initial structure
- Coordinates with QA persona for test strategies
- Integrates with Scribe persona for documentation

### plugin-system-agent

**Purpose**: Design extensible plugin architecture for the debugger.

**Activation**: 
- Manual: `--agent plugin-system-agent`
- Automatic: Plugin architecture, extension system, hook implementation

**Core Capabilities**:
- Plugin architecture design
- Hook system implementation
- Dynamic loading mechanisms
- API design
- Security sandboxing
- Lifecycle management

**Specialized Knowledge**:
- Plugin patterns (hooks, filters, actions)
- Dynamic module loading in Python
- Security considerations
- API versioning
- Dependency resolution

## Sub-Agent Coordination

### Typical Workflows

**Project Initialization**:
1. project-setup-agent creates structure
2. cli-developer-agent implements CLI
3. test-documentation-agent adds tests and docs

**Feature Development**:
1. error-pattern-agent designs detection logic
2. template-system-agent creates output templates
3. ai-integration-agent adds intelligence

**Extension Development**:
1. plugin-system-agent designs architecture
2. template-system-agent enables custom templates
3. test-documentation-agent ensures quality

### Best Practices

1. **Focused Expertise**: Each agent handles specific domain
2. **Clear Handoffs**: Define integration points clearly
3. **Parallel Work**: Use multiple agents concurrently when possible
4. **Quality Gates**: Each agent validates its output
5. **Documentation**: Agents document their decisions