# whisper-street

**Voice isolation and transcription** — take messy real-world audio, separate the
speech from everything else, and turn it into an accurate, timed, speaker-aware
transcript.

whisper-street is built to be used three ways, and to be equally good at all three:

- **By people**, from a command line or the web app.
- **By agents and LLMs**, through an [MCP server](docs/mcp/README.md) that exposes
  the pipeline as typed, documented tools.
- **By platforms**, through a versioned [HTTP API](docs/api/README.md).

> [!NOTE]
> **Status: early public migration.** This repository is being opened up from a
> working local prototype. The scaffolding, contribution process, and interface
> designs are in place; the pipeline source is being imported now. Sections marked
> _TBD_ land with that import, and the stage breakdown below is a working draft
> that will be reconciled against the prototype. Issues and discussion are welcome
> immediately — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Why this exists

Transcription quality collapses on the audio people actually have: overlapping
speakers, street noise, HVAC hum, music beds, one bad microphone in a room of
six. Most tooling treats isolation and transcription as separate problems and
makes you glue them together.

whisper-street treats them as one pipeline, and makes every stage inspectable —
so you can see *why* a transcript came out the way it did, and swap any stage for
a better one.

## The pipeline

```
ingest  ─▶  isolate  ─▶  segment  ─▶  transcribe  ─▶  emit
  │           │            │             │             │
  │           │            │             │             └─ text, JSON, SRT, VTT
  │           │            │             └─ speech → tokens, with timings
  │           │            └─ voice activity + speaker turns
  │           └─ speech separated from noise, music, other speakers
  └─ any container/codec, normalized to a known sample rate
```

Each stage has a defined input and output contract, so a stage can be replaced
without touching the others. The contracts are documented in
[docs/architecture.md](docs/architecture.md).

## Quick start

_TBD — lands with the prototype import._

## Documentation

| If you want to… | Read |
| --- | --- |
| Understand how the pipeline fits together | [docs/architecture.md](docs/architecture.md) |
| Drive it from an agent or LLM | [docs/mcp/README.md](docs/mcp/README.md) |
| Integrate it into a platform | [docs/api/README.md](docs/api/README.md) |
| Contribute code, docs, or ideas | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Work on this repo *as* an AI agent | [AGENTS.md](AGENTS.md) |
| Report a vulnerability | [SECURITY.md](SECURITY.md) |
| See how decisions get made | [GOVERNANCE.md](GOVERNANCE.md) |

Machine-readable documentation index: [llms.txt](llms.txt).

## Contributing

This project is opening up specifically to take in improvements, optimizations,
and ideas we haven't had. Accuracy gains, speed gains, better separation models,
new output formats, better docs — all in scope.

Start with [CONTRIBUTING.md](CONTRIBUTING.md). If you're not sure where to begin,
open an issue describing what you want to change before writing code; that's the
cheapest way to find out whether it's already in flight.

## License

[MIT](LICENSE) © Ondium

Note that the models this project can drive are licensed separately by their
respective authors. See [docs/architecture.md](docs/architecture.md#model-licensing)
before shipping anything commercially.
