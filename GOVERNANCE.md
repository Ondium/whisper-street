# Governance

whisper-street is maintained by [Ondium](https://github.com/Ondium) and open to
contribution from anyone. This document says who decides what, so that
contributors know where a proposal goes and what happens to it.

It is deliberately lightweight. It will grow as the contributor base does.

## Roles

**Contributors** are anyone who opens an issue, a pull request, or improves the
documentation. No process to join — the first contribution makes you one.

**Maintainers** review and merge pull requests, triage issues, cut releases, and
enforce the [Code of Conduct](CODE_OF_CONDUCT.md). Maintainers are listed in
[`.github/CODEOWNERS`](.github/CODEOWNERS).

**Becoming a maintainer**: sustained, high-quality contribution — code, review,
documentation, or community support — over time. Existing maintainers extend the
invitation. There is no application form; the work is the application. If you're
doing that work and want to know where you stand, ask.

## How decisions are made

Most decisions are made in public on issues and pull requests, by consensus of
the people participating. If nobody objects, that's agreement.

When there is disagreement:

1. **Discuss it on the issue.** Most disagreements are two people optimizing for
   different real constraints, and surface as soon as both are written down.
2. **If it stays unresolved**, a maintainer makes the call and writes down the
   reasoning on the thread. Contributors can ask for that to be revisited with
   new evidence — new benchmarks, a new use case, a bug the decision caused.

Decisions that change the shape of the project — the public API, the MCP tool
surface, the output schemas, supported runtimes, licensing — need explicit
maintainer sign-off and a written rationale, because other people build on them.

## Proposing significant changes

For anything that changes a public contract or adds a substantial subsystem:

1. Open an issue with the **feature request** template describing the problem,
   the proposed shape, the alternatives you considered, and the compatibility
   impact.
2. Expect discussion. The goal is to find the objections before you write the
   code, not after.
3. Once the shape is agreed, implement it. Reference the issue from the PR.

This exists to protect your time. A rejected design costs an afternoon; a
rejected implementation costs a fortnight.

## Compatibility promises

The **HTTP API** and the **MCP tool surface** are contracts. Once a version is
released, breaking changes within that version are not made — they go into a new
version, with the old one supported for a stated deprecation window. The rules
are in [docs/api/README.md](docs/api/README.md) and
[docs/mcp/README.md](docs/mcp/README.md).

Internal modules are not contracts and can change between releases. If you are
depending on an internal, say so in an issue — that is the signal we need to
consider promoting it.

## Releases

Releases follow [Semantic Versioning](https://semver.org/) and are cut by
maintainers. The changelog is derived from Conventional Commit messages; see
[CONTRIBUTING.md](CONTRIBUTING.md#commit-and-pr-conventions).

Before `1.0.0`, minor versions may contain breaking changes; they will be called
out in [CHANGELOG.md](CHANGELOG.md) with a migration path.

## Code of Conduct enforcement

Reports go to the maintainers as described in
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md#enforcement). Maintainers who are the
subject of a report recuse themselves from handling it.

## Changing this document

Open a pull request. Changes to governance need maintainer consensus, not just a
single approval.
