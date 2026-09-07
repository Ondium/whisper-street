# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Entries are derived from [Conventional Commit](https://www.conventionalcommits.org/)
messages — see [CONTRIBUTING.md](CONTRIBUTING.md#commit-and-pr-conventions).

## [Unreleased]

### Added

- Public repository foundation: contribution process, code of conduct, security
  policy, governance, issue and pull request templates.
- Agent- and LLM-facing documentation: `AGENTS.md`, `CLAUDE.md`, and a
  machine-readable documentation index at `llms.txt`.
- Interface design documents for the [MCP server](docs/mcp/README.md) and the
  [HTTP API](docs/api/README.md).
- Continuous integration scaffolding.
- Typed stub scaffold: Python core contracts (`src/whisper_street/core`) with
  canonical JSON/SRT/VTT rendering, per-stage stub implementations
  (`src/whisper_street/stages`), a FastAPI `/v1` surface with an in-memory job
  store (`src/whisper_street/api`), and a CLI (`src/whisper_street/cli`). No
  transcription engine is wired in yet — see
  [docs/ROADMAP.md](docs/ROADMAP.md#phase-1-import-the-prototype-engine).
- TypeScript MCP server (`packages/mcp-server`) exposing the seven tools from
  [docs/mcp/README.md](docs/mcp/README.md#proposed-tool-surface) as a thin
  client over the HTTP API; three of them (`inspect_audio`, `isolate_voice`,
  `search_transcript`) currently return `NO_BACKEND_ENDPOINT` pending a
  backend decision (see [docs/ROADMAP.md](docs/ROADMAP.md#phase-3-v1-contract-freeze)).
- A manual (`workflow_dispatch`-only) release workflow and a `Dockerfile`
  packaging the HTTP API service, plus [docs/ROADMAP.md](docs/ROADMAP.md)
  describing the phased path to v1.

[Unreleased]: https://github.com/Ondium/whisper-street/commits/main
