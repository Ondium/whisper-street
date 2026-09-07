# Security Policy

## Reporting a vulnerability

**Please do not open a public issue for a security vulnerability.**

Report it privately through GitHub:
[**Report a vulnerability**](https://github.com/Ondium/whisper-street/security/advisories/new).
This creates a private advisory visible only to you and the maintainers.

If you cannot use GitHub advisories, email **_TBD — maintainer security
address_**.

### What to include

The more of this you can give us, the faster we can act:

- What kind of issue it is (path traversal, command injection, SSRF, resource
  exhaustion, secret disclosure, model-file deserialization, …)
- The affected version, commit, or deployment
- Step-by-step reproduction, ideally with a minimal input
- What an attacker gets out of it
- Any suggested fix

### What to expect

| Stage | Target |
| --- | --- |
| Acknowledgement that we received the report | 3 business days |
| Initial assessment and severity | 10 business days |
| Fix or documented mitigation for confirmed high-severity issues | 90 days from acknowledgement |

We will keep you updated as we work, credit you in the advisory unless you'd
rather stay anonymous, and let you know before we publish.

## Scope

**In scope:** the code in this repository — the pipeline, CLI, HTTP API, and MCP
server — and its build, release, and CI configuration.

**Out of scope:**

- Vulnerabilities in upstream models or third-party dependencies. Report those
  upstream. If whisper-street's *use* of a dependency is what makes it
  exploitable, that is in scope.
- Findings from automated scanners with no demonstrated impact.
- Denial of service achieved by simply submitting very large audio files to a
  deployment that has not configured limits. Configuring limits is the
  operator's job and is documented in [docs/api/README.md](docs/api/README.md).
- Social engineering, physical attacks, and issues in third-party hosting.

## Things worth knowing about this project's threat surface

This project processes untrusted media and loads machine-learning models. If
you're auditing it or deploying it, these are the areas that matter most:

- **Media decoding.** Audio and video containers are parsed by native decoders.
  Malformed input is an attack surface, and it reaches native code.
- **Model loading.** Some model formats are deserialization formats and can
  execute code on load. Only load weights from sources you trust; prefer formats
  that cannot carry executable payloads.
- **Subprocess invocation.** Anywhere a filename or user-supplied string reaches
  a media tool's command line is a place to check for injection.
- **Path handling.** Uploaded filenames must never determine where a file is
  written.
- **Resource exhaustion.** Transcription is expensive. Any endpoint accepting
  audio needs size, duration, and concurrency limits.
- **Data sensitivity.** Audio and transcripts are personal — often biometric —
  data. Logs, caches, temporary files, and error messages should not retain them
  by default, and anything that does must be documented.

## Supported versions

The project has not yet cut a stable release. Until `1.0.0`, security fixes are
made against `main` only. This table will be maintained once releases begin.

| Version | Supported |
| --- | --- |
| `main` | ✅ |
