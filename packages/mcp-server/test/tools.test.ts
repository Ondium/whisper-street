import assert from 'node:assert/strict';
import { afterEach, describe, test } from 'node:test';
import { WhisperStreetClient } from '../src/client.js';
import * as describeCapabilities from '../src/tools/describeCapabilities.js';
import * as getJob from '../src/tools/getJob.js';
import * as inspectAudio from '../src/tools/inspectAudio.js';
import * as isolateVoice from '../src/tools/isolateVoice.js';
import * as searchTranscript from '../src/tools/searchTranscript.js';
import * as transcribe from '../src/tools/transcribe.js';

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
});

function refuseAllFetch(): void {
  globalThis.fetch = (async () => {
    throw new Error('fetch should not have been called');
  }) as typeof fetch;
}

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function textOf(result: { content: Array<{ type: string; text?: string }> }): string {
  return result.content.map((c) => c.text ?? '').join('\n');
}

describe('stub tools make no network call and report NO_BACKEND_ENDPOINT', () => {
  test('inspect_audio', async () => {
    refuseAllFetch();
    const handler = inspectAudio.createHandler();
    const result = await handler({ source: 'https://example.test/a.wav' });

    assert.equal(result.isError, true);
    assert.match(textOf(result), /NO_BACKEND_ENDPOINT/);
  });

  test('isolate_voice', async () => {
    refuseAllFetch();
    const handler = isolateVoice.createHandler();
    const result = await handler({ source: 'https://example.test/a.wav' });

    assert.equal(result.isError, true);
    assert.match(textOf(result), /NO_BACKEND_ENDPOINT/);
  });

  test('search_transcript', async () => {
    refuseAllFetch();
    const handler = searchTranscript.createHandler();
    const result = await handler({ job_id: 'j1', query: 'budget', max_results: 20 });

    assert.equal(result.isError, true);
    assert.match(textOf(result), /NO_BACKEND_ENDPOINT/);
  });
});

describe('describe_capabilities', () => {
  test('calls GET /v1/capabilities and returns structured content', async () => {
    const calls: string[] = [];
    globalThis.fetch = (async (input: string | URL | Request) => {
      calls.push(typeof input === 'string' ? input : input.toString());
      return jsonResponse(200, {
        models: ['base'],
        languages: ['en'],
        output_formats: ['json'],
        url_fetch_enabled: false,
        limits: {
          max_file_size_bytes: 1,
          max_audio_duration_seconds: 1,
          max_concurrent_jobs_per_caller: 1,
          request_rate_limit_per_minute: 1,
          result_retention_period_seconds: 1,
        },
      });
    }) as typeof fetch;

    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });
    const handler = describeCapabilities.createHandler(client);
    const result = await handler();

    assert.deepEqual(calls, ['http://example.test/v1/capabilities']);
    assert.equal(result.isError, undefined);
    assert.equal(result.structuredContent?.url_fetch_enabled, false);
  });
});

describe('get_job', () => {
  test('calls GET /v1/jobs/{id}', async () => {
    const calls: string[] = [];
    globalThis.fetch = (async (input: string | URL | Request) => {
      calls.push(typeof input === 'string' ? input : input.toString());
      return jsonResponse(200, { job_id: 'j1', state: 'running' });
    }) as typeof fetch;

    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });
    const handler = getJob.createHandler(client);
    const result = await handler({ job_id: 'j1' });

    assert.deepEqual(calls, ['http://example.test/v1/jobs/j1']);
    assert.equal(result.structuredContent?.state, 'running');
  });
});

describe('transcribe', () => {
  test('async=true hits POST /v1/jobs and returns only a handle + summary, never full segments', async () => {
    const calls: Array<{ url: string; method: string | undefined }> = [];
    globalThis.fetch = (async (input: string | URL | Request, init?: RequestInit) => {
      calls.push({ url: typeof input === 'string' ? input : input.toString(), method: init?.method });
      return jsonResponse(200, {
        job_id: 'job-123',
        state: 'queued',
      });
    }) as typeof fetch;

    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });
    const handler = transcribe.createHandler(client);
    const result = await handler({ source: 'https://example.test/a.wav', async: true });

    assert.equal(calls.length, 1);
    assert.equal(calls[0]?.url, 'http://example.test/v1/jobs');
    assert.equal(calls[0]?.method, 'POST');

    assert.equal(result.isError, undefined);
    assert.equal(result.structuredContent?.job_id, 'job-123');
    assert.equal(result.structuredContent?.state, 'queued');
    assert.equal('segments' in (result.structuredContent ?? {}), false);
    assert.doesNotMatch(textOf(result), /"segments"/);
  });

  test('async=false (default) calls POST /v1/transcribe and never returns full segments inline', async () => {
    globalThis.fetch = (async () =>
      jsonResponse(200, {
        job_id: 'job-456',
        language: 'en',
        segments: [{ start_seconds: 0, end_seconds: 1, text: 'hi' }],
        config: {},
      })) as typeof fetch;

    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });
    const handler = transcribe.createHandler(client);
    const result = await handler({ source: 'https://example.test/a.wav', async: false });

    assert.equal(result.structuredContent?.job_id, 'job-456');
    assert.equal(result.structuredContent?.segment_count, 1);
    assert.equal('segments' in (result.structuredContent ?? {}), false);
  });

  test('async=false surfaces the stub backend\'s PIPELINE_NOT_IMPLEMENTED as a tool error', async () => {
    globalThis.fetch = (async () =>
      jsonResponse(501, {
        error: {
          code: 'PIPELINE_NOT_IMPLEMENTED',
          message: 'the transcription pipeline is not implemented in this build.',
          retryable: false,
        },
      })) as typeof fetch;

    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });
    const handler = transcribe.createHandler(client);
    const result = await handler({ source: 'https://example.test/a.wav', async: false });

    assert.equal(result.isError, true);
    assert.match(textOf(result), /PIPELINE_NOT_IMPLEMENTED/);
  });
});
