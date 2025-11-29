# Changelog

All notable changes to Groqqy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-28

### Added
- **Strategy Pattern**: ToolExecutionStrategy abstraction for extensible tool execution
  - `LocalToolStrategy`: Function-based tools (read_file, run_command) execute locally
  - `PlatformToolStrategy`: Server-executed tools (browser_search, web_search) run on Groq's servers
  - `HybridToolStrategy`: Mix local + platform tools in same agent
  - `detect_strategy()`: Auto-detection selects appropriate strategy based on tool types
- **Platform Tool Support**: Integration with Groq Compound AI System
  - `registry.register_platform_tool("browser_search")` API
  - Server-side execution (no local tool_calls, results appear directly in response)
  - Compatible models: openai/gpt-oss-20b, Llama 4 Scout, Llama 3.3 70B
- **Web Search Capabilities**: browser_search powered by Tavily API
- **New Example**: `examples/example_web_search.py` demonstrating platform tools and hybrid usage

### Changed
- **Agent**: Added optional `strategy` parameter (auto-detected if not provided)
- **ToolRegistry**: Enhanced `to_schemas()` to merge function and platform tools
- **Agent Loop**: Delegates response handling to strategy pattern instead of hardcoded logic
- **Architecture**: Extended via Strategy Pattern (Open/Closed Principle)

### Technical Details
- `strategy.py`: 209 lines with extensive documentation and teaching focus
- Backward compatible: Existing code works unchanged without modifications
- Follows SOLID principles: Open/Closed (extend via new strategies without modifying Agent)
- Teaching microkernel: Each strategy includes "WHY THIS EXISTS" documentation
- Auto-detection prevents API complexity for beginners while allowing advanced control

## [1.0.0] - 2025-11-28

### Added - v0.3.0 Architecture Refactor
- **Agentic Loop**: Multi-step reasoning (THINK → ACT → OBSERVE pattern)
- **Agent Component** (175 lines): Orchestrates agentic loop with max_iterations safeguard
- **Tool Registry** (199 lines): Dynamic tool registration system
- **Composable Components**: ConversationManager, ToolExecutor, CostTracker
- **Provider Interface**: Abstract LLM provider for extensibility
- **Configuration System**: ~/.groqqy/ directory for boot.md and knowledge files
- **Comprehensive Documentation**:
  - README.md (477 lines): Complete user guide with diagrams
  - ARCHITECTURE.md (864 lines): Deep technical guide
  - TEACHING_GUIDE.md (789 lines): Educational resource with 3-phase learning path
  - 4 hands-on exercises, 12 discussion questions, 10 project ideas, 4-week syllabus

### Changed
- **Bot.py**: Refactored from 277 → 140 lines (49% reduction), now facade over Agent
- **Architecture**: Transformed from monolithic to composable (5 layers, 14 files)
- **CLI**: Enhanced with --context, --prompt, --no-boot options
- **Security**: Fixed shell injection vulnerabilities (shlex.quote in search tools)

### Added - v0.2.0 Features
- Configuration system (~/.groqqy/boot.md for apriori knowledge)
- System instruction customization
- Multiple context file support
- Single-shot mode (--prompt flag)

### Technical Details
- Python 3.8+ support
- Standalone implementation using requests (no external AI frameworks)
- Clean separation of concerns across 14 files (all <200 lines)
- Production-ready patterns: logging (loguru + JSONL), cost tracking, error handling
- Follows SOLID principles and design patterns (Facade, Strategy, Registry, Composition)
- Implements ReAct pattern (Yao et al., 2022)

### Testing
- Architecture validation tests (6/6 passing)
- Configuration system tests (all passing)
- Example scripts verified working

## [0.1.0] - 2025-11-27

### Added
- Initial MVP release
- Clean tool-calling bot kernel
- Exemplary Python architecture for AI agent development
- Production-ready patterns (error handling, cost tracking, composability)

---

## Release Notes Template

### [X.Y.Z] - YYYY-MM-DD

#### Added
- New features

#### Changed
- Changes to existing functionality

#### Deprecated
- Soon-to-be removed features

#### Removed
- Removed features

#### Fixed
- Bug fixes

#### Security
- Security improvements
