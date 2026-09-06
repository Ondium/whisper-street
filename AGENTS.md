# AGENTS.md

Instructions for AI agents and automated tools working in this repository.

This file follows the [agents.md](https://agentsmd.net/) convention and is the
canonical entry point for non-human contributors. Human contributors should read
[CONTRIBUTING.md](CONTRIBUTING.md) — everything there applies to you too; this
file adds what an agent specifically needs.

> **Repository status:** the pipeline source is being imported from a local
> prototype. Sections marked _TBD_ are filled in as that lands. If a section you
> need is still TBD, say so rather than inferring — an inferred build command
> that silently does nothing is worse than an admitted gap.

## What this project is

whisper-street turns messy real-world audio into accurate, timed, speaker-aware
transcripts. Two coupled problems, one pipeline:

- **Voice isolation** — separating speech from noise, music, and other speakers.
- **Transcription** — turning isolated speech into text with timings.

It is consumed three ways: a CLI, an [HTTP API](docs/api/README.md), and an
[MCP server](docs/mcp/README.md). All three are public contracts.

## Repository map

```
├── AGENTS.md            ← you are here
├── CLAUDE.md            → points here
├── llms.txt             machine-readable documentation index
├── README.md            human entry point
├── CONTRIBUTING.md      contribution process (applies to agents too)
├── GOVERNANCE.md        who decides what
├── SECURITY.md          threat surface + private disclosure
├── docs/
│   ├── architecture.md  pipeline stages and their contracts
│   ├── api/             HTTP API design and compatibility rules
│   └── mcp/             MCP tool surface design
└── .github/             issue/PR templates, CODEOWNERS, workflows
```

Source layout: _TBD — lands with the prototype import._

## Non-negotiable rules

These are the things that cause real harm if an agent gets them wrong.

1. **Never commit audio, model weights, or secrets.** `.gitignore` blocks audio
   and weight formats deliberately. If a `git add -f` seems necessary, stop and
   ask a human — that friction exists to catch exactly this.
2. **Never commit recordings of identifiable voices.** Voice is biometric data.
   This is a legal exposure, not a style preference.
3. **Never weaken a test to make CI pass.** Not by skipping it, not by loosening
   an assertion, not by marking it flaky. A failing test is information. If a
   test is genuinely wrong, fix it in its own commit with the reasoning stated.
4. **Never change a public contract silently.** The HTTP API, MCP tool surface,
   output schemas, and CLI flags are depended on by people you can't see. Change
   them only as a deliberate, documented, versioned change.
5. **Never claim a quality improvement without measurement.** "Should be faster"
   is not a benchmark. See [Measuring quality](#measuring-quality).
6. **Never invent behaviour in documentation.** If you don't know what the code
   does, read it or say you don't know. Documentation is trusted; a confident
   wrong sentence propagates into other people's systems and into other models'
   context.

## Before you change anything

1. Read [docs/architecture.md](docs/architecture.md) to find which stage owns the
   behaviour you're changing.
2. Read the contract for that stage. Stages are swappable *because* their
   contracts are stable — a change that widens or narrows a stage's input/output
   affects every alternative implementation of it.
3. Check whether the change crosses a public contract (API, MCP, schema, CLI). If
   it does, it needs a design conversation before implementation — see
   [GOVERNANCE.md](GOVERNANCE.md#proposing-significant-changes).
4. Search open issues and PRs for the same work in flight.

## Verifying your work

Run these before proposing any change. Do not rely on CI to discover problems
you could have found locally.

```
# TBD — lands with the prototype import.
# This block will contain the exact install, lint, typecheck, and test commands.
```

Whatever the eventual commands, the standard is the same:

- **The failing case first.** For a bug fix, reproduce the bug and show the test
  failing *before* your fix. A fix without a reproduction is a guess.
- **The unhappy paths.** Empty audio, silence, a single speaker, a dozen
  overlapping speakers, a file that isn't audio, a truncated file, an unexpected
  sample rate, a language the model wasn't asked for.
- **Read your own diff adversarially** before proposing it. What would a
  reviewer object to? Fix that first.

## Measuring quality

Changes to isolation, segmentation, or transcription need numbers. State:

| What | Why it's needed |
| --- | --- |
| Dataset or clips, and where to obtain them | Otherwise nobody can reproduce it |
| Metric — WER, CER, SI-SDR, DER, RTF | "Better" is ambiguous across these |
| Hardware and configuration | Speed claims are meaningless without it |
| What regressed | Trade-offs are acceptable; hidden trade-offs are not |

A change that helps noisy multi-speaker audio and hurts clean single-speaker
audio may well be worth merging. That decision belongs to a human who can see
both numbers.

## Writing code here

- **Type it.** Public functions carry type annotations. Agents and humans both
  navigate this codebase by signature.
- **Document the contract, not the implementation.** A docstring should say what
  goes in, what comes out, what raises, and what the units are — sample rates,
  channel counts, timestamp bases (seconds vs. samples vs. milliseconds) are the
  single most common source of bugs in audio code. State them.
- **Make errors specific.** `ValueError("bad input")` tells a caller nothing.
  Say which input, what was expected, and what arrived.
- **Match the surrounding code.** Its naming, comment density, and idiom are the
  local standard, whatever your defaults are.
- **Keep changes minimal and focused.** One concern per PR. Do not reformat files
  you're editing for another reason — it destroys the diff.

## Writing documentation here

This project is meant to be readable by models as well as people. That implies:

- **State facts explicitly rather than implying them.** Units, defaults, ranges,
  and error conditions written out, not left to be inferred from an example.
- **Keep examples runnable and correct.** A broken example in documentation is a
  broken example in every downstream context window that ingests it.
- **Use stable heading structure and descriptive link text.** Documents get
  chunked and retrieved by section; a section should make sense retrieved alone.
- **Update [llms.txt](llms.txt)** when you add or move a document.

## Opening a pull request

Follow [CONTRIBUTING.md](CONTRIBUTING.md#commit-and-pr-conventions), plus:

- **Disclose that it's agent-generated** in the PR description, and say which
  parts a human reviewed. The PR template has a field for this. This is context
  for reviewers, not a mark against the change.
- **A human must be accountable** for the PR — available to answer review
  questions and stand behind the change.
- **State what you could not verify.** If you couldn't run the audio tests
  because you had no fixtures, say that in the PR. An honest gap gets reviewed
  properly; a silent one gets merged and breaks later.

Do not open bulk PRs that apply the same mechanical change across many files
without a stated problem. They will be closed.

## When you're stuck or uncertain

Say so. Explicitly, in the PR or issue, naming what you don't know.

The failure mode this project cares most about is an agent producing something
that *looks* complete — documented, tested, confident — over an assumption that
was never checked. A stated uncertainty costs a reviewer thirty seconds. An
unstated one costs a debugging session weeks later, and erodes the trust that
makes agent contribution viable at all.
