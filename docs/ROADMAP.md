# Roadmap

> Strategic phasing for whisper-street from the current stub scaffold to a
> released v1. This is a plan, not a schedule — dates aren't promised. See
> [GOVERNANCE.md](../GOVERNANCE.md#releases) for how releases are actually cut.

## Phase 0 — typed stub scaffold (this build)

A green, buildable, publicly readable repository with zero transcription
engine: Python core contracts and canonical JSON/SRT/VTT rendering, a FastAPI
`/v1` surface with an in-memory job store, a CLI, a TypeScript MCP server
exposing seven tools, CI, a manual release workflow, and this roadmap. Every
pipeline stage (ingest, isolate, segment, transcribe, emit) is a typed stub —
it satisfies its contract without doing real audio work.

## Phase 1 — import the prototype engine

Bring in the working local prototype (`wav_pipeline`: faster-whisper /
openai-whisper for ASR, an onnxruntime-based gate for isolation) and map it
onto the existing Ingester / Isolator / Segmenter / Transcriber contracts
(`src/whisper_street/core/stages.py`, `docs/architecture.md`). Concretely:

- Resolve every `_TBD_` in [Architecture](architecture.md): stage contract
  details, schema, and configuration format.
- Fill in the model-licensing table in Architecture — each model whisper-street
  can drive is licensed separately by its author (see
  [LICENSE](../LICENSE)) and that table is currently empty.
- Real multipart file upload for `POST /v1/jobs` and `POST /v1/transcribe`
  lands here. The v0 scaffold accepts a JSON submission — an opaque `audio`
  field or `source_url` — because `python-multipart` is intentionally not a
  dependency while the audio path is fully stubbed (see
  [HTTP API — Submitting a job](api/README.md#submitting-a-job)).

## Phase 2 — benchmarks and evidence

Establish the measurement discipline [AGENTS.md#measuring-quality](../AGENTS.md#measuring-quality)
requires before any isolation, segmentation, or transcription change can claim
an improvement: WER, CER, SI-SDR, DER, and RTF on stated datasets and
hardware. Define the test fixtures policy — what small, license-clear clips
live under `tests/fixtures/`, and how larger evaluation sets are obtained
without being committed (`.gitignore`, `CONTRIBUTING.md#audio-models-and-test-fixtures`).

## Phase 3 — v1 contract freeze

- Publish the OpenAPI 3.1 document promised in
  [HTTP API — Machine-readable specification](api/README.md#machine-readable-specification).
- Resolve API authentication — currently `_TBD_` in
  [HTTP API — Authentication](api/README.md#authentication) — covering both
  interactive users and machine-to-machine platform callers.
- Open a governance issue to reconcile the MCP↔HTTP gap: the MCP tools
  `inspect_audio`, `isolate_voice`, and `search_transcript`
  (`packages/mcp-server/src/tools/`) have no backing HTTP endpoint yet and
  currently return `NO_BACKEND_ENDPOINT`. Before v1 this needs either new
  additive HTTP endpoints, or a documented decision to drop or change those
  tools — the latter is a breaking MCP change under
  [MCP server — Compatibility](mcp/README.md#compatibility) and needs
  maintainer sign-off.
- Flip [release.yml](../.github/workflows/release.yml) from manual-only
  toward real triggers, and cut `1.0.0`.

## Collaboration and governance

Contract documents (`docs/api/`, `docs/mcp/`) stay issue-gated — proposed
changes are discussed before implementation, per
[GOVERNANCE.md#proposing-significant-changes](../GOVERNANCE.md#proposing-significant-changes).
[AGENTS.md](../AGENTS.md) is the on-ramp for coding agents working in this
repository; the MCP server is the on-ramp for enterprise and agent
*consumers* of the pipeline once its tools stop being stubs, at which point it
is published to npm. Its schemas are kept stable once published — agents
cache tool schemas, so churn there is more disruptive than an equivalent REST
change (see [MCP server — Compatibility](mcp/README.md#compatibility)).
