# Changelog

All notable changes to Groqqy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release
- Core Groqqy bot with clean, composable architecture
- 4 built-in tools: read_file, run_command, search_files, search_content
- Interactive CLI interface
- Custom tool support
- Cost tracking per interaction and total
- Complete documentation (README, ARCHITECTURE, DEVELOPMENT)
- 3 working examples (basic chat, tool usage, custom tools)
- Type annotations throughout
- Organized into 6 logical sections (19 functions, all 3-7 lines)

### Fixed
- Fixed Groq tool calling by adding required parameter validation
- TIA's GroqProvider now properly marks parameters as required in function schemas

### Technical Details
- Python 3.8+ support
- Uses TIA's GroqProvider for LLM integration
- Follows TIA Python Development Guide principles
- Clean separation of concerns: conversation management, LLM interaction, tool execution
- Extensible architecture with clear hook points

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
