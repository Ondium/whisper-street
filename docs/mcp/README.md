# MCP server

> **Status: design.** This document proposes the tool surface an MCP server would
> expose. It is not yet implemented. The design is open to argument — open an
> issue.

[Model Context Protocol](https://modelcontextprotocol.io/) is how whisper-street
is meant to be driven by LLMs and agents: not by an agent shelling out to a CLI
and parsing whatever it prints, but through typed tools with documented
arguments, documented return shapes, and documented failure modes.

Like the [HTTP API](../api/README.md), the tool surface is a **public contract**.

## Designing for an agent caller

An agent is a different kind of caller than a script, and the design follows from
that:

- **An agent cannot see the deployment.** It doesn't know which models are
  installed or what the limits are. So capability discovery is a tool, not
  documentation.
- **An agent pays for every token of output.** Returning a 90-minute transcript
  inline destroys the caller's context window. Large results are returned as
  resources or handles that the agent can query, with a summary inline.
- **An agent recovers from errors by reading them.** An error must say what to do
  differently — "audio exceeds the 60-minute limit; split it or use a job" — not
  just that something failed.
- **An agent will call tools it doesn't fully understand.** Every parameter needs
  a description, a type, a default, and units. Ambiguity produces confidently
  wrong calls.
- **Transcription outlasts a tool call.** Long work returns a handle immediately
  and is polled, rather than blocking until timeout.

## Proposed tool surface

| Tool | Purpose |
| --- | --- |
| `describe_capabilities` | What this deployment supports: models, languages, formats, limits. Call before assuming. |
| `inspect_audio` | Metadata about a source without processing it: duration, channels, sample rate, estimated speaker count. Cheap; use it to plan. |
| `transcribe` | Run the full pipeline. Returns a result handle plus an inline summary. |
| `isolate_voice` | Run isolation only, producing cleaned audio — for callers doing their own recognition. |
| `get_job` | Status of a running job. |
| `get_transcript` | Fetch a result: whole, by time range, by speaker, or as a specific format. |
| `search_transcript` | Find spans matching a query without pulling the whole transcript into context. |

`search_transcript` and the range/speaker filters on `get_transcript` are the
context-economy tools. The common agent task — "what did they say about the
budget?" — should cost a few hundred tokens, not the whole transcript.

## Return shapes

Every tool returns structured content, not prose. Prose returns force the model
to parse natural language, which is exactly the ambiguity MCP exists to remove.

`transcribe` returns a handle, plus enough inline for the agent to decide what to
do next: duration processed, speakers detected, segment count, mean confidence,
detected language, and any spans that failed. Never the full transcript inline.

## Errors

Failures are returned as tool errors with a stable code, a message that states
the corrective action, and a retryable flag. The messages are written for a model
to act on:

> `AUDIO_TOO_LONG`: audio is 94 minutes; this deployment's synchronous limit is
> 60. Submit it as a job with `transcribe(async=true)`, or split it first.

## Safety considerations specific to agent callers

- **Consent and provenance.** An agent processing audio usually cannot tell
  whether the speakers consented to it. The server should not make that easier
  to ignore: retention defaults to off, and results should carry provenance.
- **No arbitrary URL fetching by default.** An agent can be induced by its own
  context to pass a URL. If URL input is enabled, it is allowlisted — the same
  SSRF concern as the [HTTP API](../api/README.md#submitting-a-job), and more
  reachable here.
- **Cost visibility.** Transcription is expensive and an agent may loop.
  Capability discovery should expose limits, and jobs should be cancellable.
- **Transcripts are untrusted input.** A transcript of arbitrary audio is
  attacker-controlled text entering a model's context. It may contain
  instructions. Transcript content is data, and consuming agents should treat it
  as such — anyone building on this surface should know that.

## Compatibility

The same rules as the HTTP API: tools and optional parameters may be added;
existing tool names, parameter names, semantics, and return field types do not
change within a major version. Removing or renaming a tool is a breaking change.

Agents cache tool schemas and build behaviour around them, so churn here is more
disruptive than in a REST API — a changed parameter meaning doesn't produce an
error, it produces silently wrong calls.

## Implementation notes

_TBD — lands with the prototype import._ The server should wrap the same pipeline
the CLI and HTTP API use, not reimplement it. Three interfaces over one
implementation; where they diverge, they diverge in presentation only.

The [`mcp-builder`](https://modelcontextprotocol.io/) guidance on tool design is
worth reading before implementing this.
