# Contributing to whisper-street

Thank you for being here. This project was opened up specifically to take in work
from people (and agents) outside the original team. Improvements to accuracy,
speed, separation quality, output formats, documentation, and developer
experience are all in scope.

## Table of contents

- [Ground rules](#ground-rules)
- [Ways to contribute](#ways-to-contribute)
- [Before you write code](#before-you-write-code)
- [Development setup](#development-setup)
- [Making a change](#making-a-change)
- [Commit and PR conventions](#commit-and-pr-conventions)
- [Review: what we look for](#review-what-we-look-for)
- [Audio, models, and test fixtures](#audio-models-and-test-fixtures)
- [Contributions from AI agents](#contributions-from-ai-agents)
- [Licensing of contributions](#licensing-of-contributions)

## Ground rules

Everyone here — human or agent, first-time or maintainer — follows the
[Code of Conduct](CODE_OF_CONDUCT.md).

Two more, specific to this project:

1. **Claims about quality need evidence.** "This is faster" or "this is more
   accurate" needs numbers on a stated dataset with a stated configuration. See
   [Review: what we look for](#review-what-we-look-for).
2. **Never commit audio you don't have the right to redistribute.** See
   [Audio, models, and test fixtures](#audio-models-and-test-fixtures).

## Ways to contribute

You do not need to write code to help.

| Contribution | Where to start |
| --- | --- |
| Report a bug | [Open a bug report](https://github.com/Ondium/whisper-street/issues/new?template=bug_report.yml) |
| Propose a feature or a pipeline stage | [Open a feature request](https://github.com/Ondium/whisper-street/issues/new?template=feature_request.yml) |
| Fix or improve documentation | [Open a docs issue](https://github.com/Ondium/whisper-street/issues/new?template=docs_issue.yml), or send the PR directly |
| Report a failure case | A bug report with the audio characteristics that broke it is one of the most valuable things you can file |
| Improve accuracy or speed | Read [Review: what we look for](#review-what-we-look-for) first — benchmarks matter here |
| Report a vulnerability | **Not** an issue. Follow [SECURITY.md](SECURITY.md) |

## Before you write code

For anything beyond a small, obvious fix, **open an issue first** and say what
you intend to do. This is not bureaucracy — it is the cheapest way to find out
that someone is already doing it, that it conflicts with a planned change, or
that there is a constraint you can't see from outside.

Small and obvious ("typo", "this link 404s", "this crashes on empty input") —
just send the PR.

Large and architectural (new pipeline stage, changed output schema, new model
backend, changed public API or MCP tool surface) — open an issue, and expect a
design conversation before implementation. Changes to the API or MCP surface are
contracts other people depend on; see [docs/api/README.md](docs/api/README.md)
and [docs/mcp/README.md](docs/mcp/README.md) for the compatibility rules.

## Development setup

_TBD — lands with the prototype import. It will cover the supported runtimes,
how to install dependencies, how to fetch models, and how to run the test suite._

Until then, the parts of the repo you can work on today are the documentation
under `docs/`, the interface designs, and this contribution process itself.

## Making a change

1. **Fork** the repository and create a branch off `main`. Name it for what it
   does: `fix/vad-drops-short-utterances`, `docs/mcp-tool-examples`.
2. **Make the change.** Keep it focused — one concern per pull request. A PR that
   fixes a bug *and* reformats three files is a PR that is hard to review and
   hard to revert.
3. **Add or update tests.** A bug fix should come with a test that fails without
   the fix. A new capability should come with tests that describe its contract.
4. **Update the docs in the same PR.** Documentation that lags the code is worse
   than no documentation, because people trust it. If you change behaviour that
   `docs/` describes, change `docs/` too.
5. **Run the checks locally** before pushing, so CI confirms your work rather
   than discovering it.
6. **Open the pull request** and fill in the template.

## Commit and PR conventions

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <what changed, imperative mood>

<why it changed, and anything a reviewer needs to know>
```

Types in use: `feat`, `fix`, `perf`, `docs`, `test`, `refactor`, `build`, `ci`,
`chore`. Breaking changes get a `!` after the type (`feat!:`) and a
`BREAKING CHANGE:` footer explaining the migration path.

This matters beyond tidiness: the changelog and version bumps are derived from
these messages. See [CHANGELOG.md](CHANGELOG.md).

Pull request titles follow the same format — the squashed commit becomes the
changelog entry.

## Review: what we look for

A maintainer reviewing your PR is asking, in order:

1. **Is the contract clear?** What goes in, what comes out, what happens on bad
   input. Public functions, API endpoints, and MCP tools need this written down,
   not inferred.
2. **Is it tested?** Including the unhappy paths — empty audio, a single
   speaker, twelve speakers, a file that isn't audio at all.
3. **Does it hold up on real audio?** Clean studio audio is not the target. If
   your change touches isolation, segmentation, or transcription quality,
   include before/after numbers:
   - the dataset or clips used (and where anyone can get them),
   - the metric (WER, CER, SI-SDR, DER, RTF — say which),
   - the hardware and configuration,
   - both the win *and* anything it regressed.

   A change that improves one class of audio and degrades another can still be a
   good change — but only if we know that's the trade.
4. **Is it documented for the next reader?** Including the non-human ones —
   see [AGENTS.md](AGENTS.md).

Maintainers aim to give a first response within a week. If a PR goes quiet
longer than that, a polite nudge on the thread is welcome and not rude.

## Audio, models, and test fixtures

**Audio.** Do not commit audio you do not have the right to redistribute. This
includes podcast clips, broadcast recordings, music, and recordings of people
who have not consented to their voice being published in a public repository.

Test fixtures must be short, small, and license-clear: material you recorded
yourself, or public-domain / permissively licensed material with the source and
license recorded in `tests/fixtures/README.md`. `.gitignore` deliberately
excludes audio formats — adding a legitimate fixture requires `git add -f`, and
that friction is intentional.

For anything larger, contribute a *script that fetches* the dataset rather than
the dataset itself.

**Models.** Model weights are never committed. They are fetched at runtime or
build time from their upstream source. If you add a model backend, record its
licence in [docs/architecture.md](docs/architecture.md#model-licensing) — some
speech models are research-only and cannot be used commercially, and downstream
users need to know that before they ship.

**Privacy.** Voice is biometric data and is regulated as such in several
jurisdictions. Anything that logs, caches, or transmits audio or transcripts
needs to be documented explicitly, default to off where it's not essential, and
be called out in review.

## Contributions from AI agents

Agent-authored pull requests are welcome. This project is meant to be workable
by agents, and a PR is judged on the same criteria whichever kind of contributor
wrote it.

Two requirements:

- **Disclose it.** Note in the PR description that it was agent-generated, and
  say which parts a human reviewed. This is context for reviewers, not a mark
  against the PR.
- **A human is accountable.** Someone must be able to answer questions on the
  thread, respond to review feedback, and stand behind the change.

Agents working in this repository should read [AGENTS.md](AGENTS.md) first — it
describes the layout, the invariants, and the checks to run before proposing a
change.

Unreviewed bulk-generated PRs (mass "fixes" across many files with no stated
problem) will be closed.

## Licensing of contributions

whisper-street is [MIT licensed](LICENSE). By submitting a contribution you agree
that it is licensed under the same terms, and that you have the right to submit
it — that it is your own work, or that you have permission from whoever holds
the rights.

If your contribution includes third-party code, say so in the PR, name the
licence, and keep the attribution intact. Code under a licence incompatible with
MIT cannot be merged.
