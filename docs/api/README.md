# HTTP API

> **Status: design.** This document proposes the API surface and its
> compatibility rules. It is not yet implemented, and it is the right place to
> argue with the design — open an issue. Nothing here is a promise until it
> ships in a release.

The HTTP API exists so that platforms, enterprise systems, and services can use
whisper-street without embedding it. It is a **public contract**: once released,
it changes only under the rules in [Compatibility](#compatibility).

## Design principles

1. **Transcription is slow, so the API is asynchronous.** Submitting audio
   returns a job; the result is fetched or pushed when ready. A synchronous mode
   exists only for short audio under a documented duration limit.
2. **The structured result is canonical.** SRT, VTT, and plain text are
   renderings of the same JSON. Adding a rendering never breaks a consumer.
3. **Configuration is explicit and echoed back.** Every result states the
   configuration that produced it, because a transcript without its
   configuration can't be reproduced or compared.
4. **Errors are actionable.** An error says what was wrong with the request, not
   merely that something was.
5. **Nothing is retained by default.** Audio and transcripts are personal data.
   Retention is opt-in, bounded, and stated in the response.

## Compatibility

The version is in the path: `/v1/...`. Within a major version:

- New endpoints, new optional request fields, and new response fields may be
  added at any time. **Clients must ignore unknown response fields.**
- Existing fields do not change meaning, type, or nullability.
- Enum values may be added. Clients should handle unknown values gracefully.

Breaking changes mean `/v2`, announced with a deprecation window during which
both versions run. See [GOVERNANCE.md](../../GOVERNANCE.md#compatibility-promises).

## Proposed surface

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/v1/jobs` | Submit audio for processing; returns a job |
| `GET` | `/v1/jobs/{id}` | Job status and, when complete, the result |
| `GET` | `/v1/jobs/{id}/result` | The result in a requested format |
| `DELETE` | `/v1/jobs/{id}` | Cancel a running job, or delete a retained result |
| `POST` | `/v1/transcribe` | Synchronous processing, short audio only |
| `GET` | `/v1/capabilities` | Available models, formats, languages, and limits |
| `GET` | `/v1/health` | Liveness and readiness |

`/v1/capabilities` is deliberately part of the contract rather than
documentation-only: it lets a client — or an agent — discover what a given
deployment can actually do, instead of assuming, since deployments differ in
which models they have available.

### Submitting a job

Audio arrives either as a multipart upload or as a URL the server fetches.

> **If URL fetching is enabled, it is an SSRF surface.** The design assumption is
> that it is *disabled by default*, and that when enabled the operator supplies
> an allowlist. This must be documented prominently in deployment docs.

> **Current implementation note.** The v0 scaffold accepts a JSON submission —
> an opaque `audio` field or a `source_url` — rather than a real multipart
> upload, because `python-multipart` is intentionally not a dependency while
> the audio path is fully stubbed. Real multipart upload lands in
> [Phase 1 of the roadmap](../ROADMAP.md#phase-1-import-the-prototype-engine).

A submission carries: the audio, the pipeline configuration (models, isolation
settings, whether diarization runs, timestamp granularity, expected language),
the desired output formats, and an optional webhook for completion.

### Job lifecycle

```
queued ──▶ running ──▶ succeeded
   │          │
   │          ├──▶ partial     (some segments failed; result usable, failures listed)
   │          └──▶ failed
   └──▶ cancelled
```

`partial` exists because one unintelligible segment should not discard an hour of
good transcript — but it must never be silently presented as a complete result.
A partial result names exactly which spans failed and why.

## Limits

Every deployment must set and publish these via `/v1/capabilities`:

| Limit | Why |
| --- | --- |
| Max file size | Upload exhaustion |
| Max audio duration | Compute exhaustion — the real cost driver |
| Max concurrent jobs per caller | Fair sharing under load |
| Request rate limit | Basic abuse control |
| Result retention period | Privacy — and it should be short by default |

A deployment without these configured is a denial-of-service target; see
[SECURITY.md](../../SECURITY.md#scope).

## Errors

Errors use standard HTTP status codes with a structured body carrying: a stable
machine-readable error code, a human-readable message, the field or parameter at
fault where applicable, and whether the request is worth retrying.

The stable error code is what clients branch on — messages are for humans and may
be reworded; codes are part of the contract and are not.

## Authentication

_TBD._ The choice depends on how the existing public infrastructure authenticates
today. It needs to be decided before `v1` ships, and needs to cover both
interactive users and machine-to-machine platform callers.

## Machine-readable specification

An OpenAPI 3.1 document will be published alongside the implementation and
treated as the source of truth for the contract — with client generation and
schema-based contract tests derived from it, so the document cannot drift from
the implementation without CI noticing.

_Not yet written. Contributions to the design are welcome via issue first._
