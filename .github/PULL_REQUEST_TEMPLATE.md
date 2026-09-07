## What does this change?

<!-- One or two sentences. What is different after this PR that wasn't before? -->

## Why?

<!-- The problem this solves. Link the issue: "Closes #123" / "Part of #123". -->

## How was it verified?

<!--
How do you know it works? Tests you added, checks you ran, manual verification.
"CI is green" alone isn't verification if CI doesn't cover this path yet.
-->

## Quality impact

<!--
Only if this touches isolation, segmentation, transcription accuracy, or
performance. Delete this section otherwise.

Include: the audio or dataset used (and where to get it), the metric (WER, CER,
SI-SDR, DER, RTF), the hardware and configuration, and both what improved and
what regressed.
-->

| Metric | Before | After | Dataset / config |
| --- | --- | --- | --- |
|  |  |  |  |

## Compatibility

- [ ] Purely additive — no existing behaviour changes
- [ ] Changes default behaviour (described above)
- [ ] Breaking change to a public contract (HTTP API, MCP tools, output schema, CLI flags)

<!-- If breaking: describe the migration path. It belongs in the commit's
     BREAKING CHANGE footer too. -->

## Checklist

- [ ] The PR title follows [Conventional Commits](https://www.conventionalcommits.org/) — it becomes the changelog entry
- [ ] This PR does one thing (unrelated cleanups moved to their own PR)
- [ ] Tests added or updated; a bug fix has a test that fails without it
- [ ] Documentation updated in this same PR where behaviour changed
- [ ] No audio, model weights, secrets, or personal data committed
- [ ] I have read [CONTRIBUTING.md](https://github.com/Ondium/whisper-street/blob/main/CONTRIBUTING.md) and agree to the [MIT license](https://github.com/Ondium/whisper-street/blob/main/LICENSE) terms for this contribution

## Was this authored with AI assistance?

<!--
Agent-authored PRs are welcome and judged on the same criteria — we just ask
that you say so, and that a human is available to answer review questions.
See CONTRIBUTING.md#contributions-from-ai-agents.
-->

- [ ] Partly or fully agent-generated — reviewed by: <!-- who, and which parts -->
