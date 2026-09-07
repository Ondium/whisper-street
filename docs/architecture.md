# Architecture

> **Status: working draft.** This describes the intended shape of the pipeline
> and will be reconciled against the prototype source as it is imported. Stage
> names and contracts here are a proposal, not a description of shipped code.

## The idea

Isolation and transcription are usually treated as separate problems that you
glue together. whisper-street treats them as one pipeline with **stable
contracts between stages**, so that:

- any stage can be replaced with a better implementation without touching the
  others,
- the intermediate results are inspectable, so a bad transcript can be traced to
  the stage that caused it,
- contributors can improve one thing without understanding all of it.

The second point is the one that matters most in practice. When a transcript is
wrong, the useful question is *where* it went wrong — did the separator remove
the speech along with the noise, did the segmenter merge two speakers into one
turn, or did the recognizer simply mishear? A pipeline that discards its
intermediates can't answer that.

## Stages

```
ingest  ─▶  isolate  ─▶  segment  ─▶  transcribe  ─▶  emit
```

### ingest

**Purpose:** accept whatever the user has and produce a known-shape audio buffer.

**In:** a file, stream, or URL in any container/codec the decoder supports.
**Out:** PCM audio at a defined sample rate and channel layout, plus source
metadata (original duration, codec, channel count, detected sample rate).

**Why it's separate:** every downstream stage assumes a known sample rate. Making
that assumption explicit and enforcing it in one place removes an entire class of
bug — resampling errors that show up as timestamp drift much later.

_Contract details TBD with the prototype import: target sample rate, channel
handling for multi-channel sources, and behaviour on unsupported input._

### isolate

**Purpose:** separate speech from everything that isn't the speech you want.

**In:** normalized PCM audio.
**Out:** one or more audio streams containing isolated speech, plus a record of
what was removed.

This covers denoising, dereverberation, music/speech separation, and source
separation for overlapping speakers — which of these run, and in what order, is
configuration.

**The trade to be aware of:** aggressive separation removes speech along with
noise. A separator that scores well on SI-SDR can still make transcription worse
by clipping quiet consonants. This is why quality claims here need *downstream*
metrics (WER after transcription), not just separation metrics.

_Contract details TBD._

### segment

**Purpose:** decide where speech is, and who is speaking.

**In:** isolated speech audio.
**Out:** time-bounded segments with optional speaker labels.

Covers voice activity detection (where is there speech at all) and diarization
(which speaker is which). Segments are the unit that transcription operates on,
and the unit that timestamps ultimately refer back to.

**The trade to be aware of:** segment boundaries that cut mid-word damage
recognition accuracy at the seams. Padding boundaries helps accuracy and hurts
timestamp precision.

_Contract details TBD._

### transcribe

**Purpose:** turn speech into text with timings.

**In:** segments of isolated speech.
**Out:** tokens or words with start/end times, confidence, and language.

This is where a Whisper-family model (or an alternative backend) runs. The stage
is defined by its contract rather than by a specific model, so backends can be
compared directly on the same inputs.

**The trade to be aware of:** larger models are more accurate and slower;
timestamp granularity (segment-level vs. word-level) has a real cost. Both are
configuration, not hardcoded choices.

_Contract details TBD._

### emit

**Purpose:** render the result in the form the consumer needs.

**In:** timed, labelled transcription results.
**Out:** plain text, structured JSON, SRT, VTT, or a caller-defined format.

The structured JSON form is the canonical one — every other format is derived
from it. This means a new output format is an additive change that cannot break
existing consumers.

_Schema TBD. Once published, the JSON schema is a public contract under the
compatibility rules in [api/README.md](api/README.md#compatibility)._

## Timestamps

Audio code accumulates timestamp bugs faster than any other kind, because there
are three plausible units (samples, milliseconds, seconds) and two plausible
origins (start of file, start of segment), and mixing any of them produces
results that look almost right.

**The rule for this codebase:** every timestamp crossing a stage boundary is in
**seconds from the start of the original source media**, as a float. Segment-relative
times are permitted inside a stage and must be converted before they leave it.
Any function that accepts or returns a time states its unit and origin in its
signature or docstring.

## Configuration

Model choice, separation aggressiveness, segment padding, timestamp granularity,
and output format are configuration — not code paths. The reason is
reproducibility: a quality claim is only meaningful alongside the configuration
that produced it, so configuration has to be nameable, serializable, and
recordable in results.

_Configuration format TBD._

## Model licensing

whisper-street's own code is [MIT](../LICENSE). **The models it can drive are
not.** Some widely used speech models — particularly in separation and
diarization — are released under research-only or non-commercial terms, or
require accepting terms before download.

If you add a model backend, record it here: the model, its licence, whether
commercial use is permitted, and any gating on obtaining the weights. Downstream
users need to know before they ship, and they will not go read every upstream
repository to find out.

| Model / backend | Licence | Commercial use | Notes |
| --- | --- | --- | --- |
| _TBD with the prototype import_ | | | |

## Open questions

These are genuinely undecided and good places to contribute an opinion — open an
issue:

- Should isolation run before or after segmentation? Separation quality benefits
  from knowing where the speakers are; segmentation benefits from cleaner audio.
  Running one before the other is a real trade, and it may need to be
  configurable.
- Should intermediate audio be retained by default? It makes debugging vastly
  easier and is a privacy liability. The default matters.
- How should partial failures be represented — one bad segment in an otherwise
  good transcript should probably not fail the whole job, but silently dropping
  it is worse.
