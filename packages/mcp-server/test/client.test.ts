import assert from 'node:assert/strict';
import { afterEach, describe, test } from 'node:test';
import { WhisperStreetClient } from '../src/client.js';
import { ApiError } from '../src/errors.js';

interface FetchCall {
  url: string;
  init: RequestInit | undefined;
}

function installFetchStub(handler: (call: FetchCall) => Response | Promise<Response>): FetchCall[] {
  const calls: FetchCall[] = [];
  globalThis.fetch = (async (input: string | URL | Request, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input.toString();
    const call = { url, init };
    calls.push(call);
    return handler(call);
  }) as typeof fetch;
  return calls;
}

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
});

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('WhisperStreetClient URL building', () => {
  test('getCapabilities calls GET /v1/capabilities on the configured base URL', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { models: [] }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test:9000' });

    await client.getCapabilities();

    assert.equal(calls.length, 1);
    assert.equal(calls[0]?.url, 'http://example.test:9000/v1/capabilities');
    assert.equal(calls[0]?.init?.method, 'GET');
  });

  test('getJob URL-encodes the job id', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { job_id: 'a b', state: 'queued' }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await client.getJob('a b');

    assert.equal(calls[0]?.url, 'http://example.test/v1/jobs/a%20b');
  });

  test('getJobResult builds query params for format, range, and speaker', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { job_id: 'j1', segments: [], config: {} }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await client.getJobResult('j1', {
      format: 'json',
      start_seconds: 1.5,
      end_seconds: 10,
      speaker: 'A',
    });

    const url = new URL(calls[0]!.url);
    assert.equal(url.pathname, '/v1/jobs/j1/result');
    assert.equal(url.searchParams.get('format'), 'json');
    assert.equal(url.searchParams.get('start_seconds'), '1.5');
    assert.equal(url.searchParams.get('end_seconds'), '10');
    assert.equal(url.searchParams.get('speaker'), 'A');
  });

  test('getJobResult omits query params that were not passed', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { job_id: 'j1', segments: [], config: {} }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await client.getJobResult('j1');

    assert.equal(calls[0]?.url, 'http://example.test/v1/jobs/j1/result');
  });

  test('getJobResult requests text for text/srt/vtt formats and returns the raw body', async () => {
    installFetchStub(() => new Response('1\n00:00:00,000 --> 00:00:01,000\nhi\n', { status: 200 }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    const result = await client.getJobResult('j1', { format: 'srt' });

    assert.equal(typeof result, 'string');
    assert.match(result as string, /-->/);
  });

  test('createJob POSTs a JSON body to /v1/jobs', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { job_id: 'j1', state: 'queued' }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await client.createJob({ source: 'https://example.test/a.wav' });

    assert.equal(calls[0]?.url, 'http://example.test/v1/jobs');
    assert.equal(calls[0]?.init?.method, 'POST');
    assert.equal(JSON.parse(calls[0]!.init!.body as string).source, 'https://example.test/a.wav');
  });

  test('transcribeSync POSTs to /v1/transcribe', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { job_id: 'j1', segments: [], config: {} }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await client.transcribeSync({ source: 'https://example.test/a.wav' });

    assert.equal(calls[0]?.url, 'http://example.test/v1/transcribe');
    assert.equal(calls[0]?.init?.method, 'POST');
  });

  test('deleteJob sends DELETE', async () => {
    const calls = installFetchStub(() => new Response(null, { status: 204 }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await client.deleteJob('j1');

    assert.equal(calls[0]?.url, 'http://example.test/v1/jobs/j1');
    assert.equal(calls[0]?.init?.method, 'DELETE');
  });

  test('strips a trailing slash from the configured base URL', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { status: 'ok' }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test/' });

    await client.getHealth();

    assert.equal(calls[0]?.url, 'http://example.test/v1/health');
  });
});

describe('WhisperStreetClient authentication', () => {
  test('forwards Authorization: Bearer <key> when an API key is configured', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { models: [] }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test', apiKey: 'secret-key' });

    await client.getCapabilities();

    const headers = new Headers(calls[0]?.init?.headers);
    assert.equal(headers.get('Authorization'), 'Bearer secret-key');
  });

  test('omits Authorization entirely when no API key is configured', async () => {
    const calls = installFetchStub(() => jsonResponse(200, { models: [] }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await client.getCapabilities();

    const headers = new Headers(calls[0]?.init?.headers);
    assert.equal(headers.has('Authorization'), false);
  });
});

describe('WhisperStreetClient error mapping', () => {
  test('maps a non-2xx structured error body to ApiError with code/message/retryable/field', async () => {
    installFetchStub(() =>
      jsonResponse(422, {
        error: {
          code: 'AUDIO_TOO_LONG',
          message: "audio is 94 minutes; this deployment's synchronous limit is 60.",
          field: 'source',
          retryable: false,
        },
      }),
    );
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await assert.rejects(
      () => client.transcribeSync({ source: 'https://example.test/a.wav' }),
      (err: unknown) => {
        assert.ok(err instanceof ApiError);
        assert.equal(err.code, 'AUDIO_TOO_LONG');
        assert.equal(err.retryable, false);
        assert.equal(err.field, 'source');
        assert.match(err.message, /94 minutes/);
        return true;
      },
    );
  });

  test('marks 5xx retryable when the body is not structured JSON', async () => {
    installFetchStub(() => new Response('internal error', { status: 503 }));
    const client = new WhisperStreetClient({ apiUrl: 'http://example.test' });

    await assert.rejects(
      () => client.getHealth(),
      (err: unknown) => {
        assert.ok(err instanceof ApiError);
        assert.equal(err.retryable, true);
        return true;
      },
    );
  });
});
