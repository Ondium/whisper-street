/**
 * Thin HTTP client over the whisper-street HTTP API (docs/api/README.md).
 *
 * This is deliberately a wrapper, not a reimplementation: it builds requests,
 * forwards auth, and maps the API's structured error body to ApiError. All
 * pipeline logic — and all interpretation of results — stays server-side.
 */
import type { Config } from './config.js';
import { ApiError } from './errors.js';
import type {
  ApiErrorBody,
  Capabilities,
  HealthStatus,
  JobStatus,
  PipelineConfig,
  Transcript,
} from './types.js';

export interface CreateJobBody {
  /** Audio source: a URL, subject to the deployment's URL-fetch policy. */
  source: string;
  config?: Partial<PipelineConfig>;
  webhook_url?: string;
}

export type TranscribeSyncBody = CreateJobBody;

export interface GetJobResultParams {
  format?: 'json' | 'text' | 'srt' | 'vtt';
  start_seconds?: number;
  end_seconds?: number;
  speaker?: string;
}

/** Result of GET /v1/jobs/{id}/result: the structured transcript, or rendered text. */
export type JobResult = Transcript | string;

const TEXT_FORMATS = new Set(['text', 'srt', 'vtt']);

export class WhisperStreetClient {
  private readonly baseUrl: string;
  private readonly apiKey?: string;

  constructor(config: Config) {
    this.baseUrl = config.apiUrl.replace(/\/+$/, '');
    this.apiKey = config.apiKey;
  }

  async getCapabilities(): Promise<Capabilities> {
    return this.requestJson<Capabilities>('GET', '/v1/capabilities');
  }

  async getHealth(): Promise<HealthStatus> {
    return this.requestJson<HealthStatus>('GET', '/v1/health');
  }

  async createJob(body: CreateJobBody): Promise<JobStatus> {
    return this.requestJson<JobStatus>('POST', '/v1/jobs', body);
  }

  async getJob(id: string): Promise<JobStatus> {
    return this.requestJson<JobStatus>('GET', `/v1/jobs/${encodeURIComponent(id)}`);
  }

  async getJobResult(id: string, params: GetJobResultParams = {}): Promise<JobResult> {
    const query = new URLSearchParams();
    if (params.format !== undefined) query.set('format', params.format);
    if (params.start_seconds !== undefined) {
      query.set('start_seconds', String(params.start_seconds));
    }
    if (params.end_seconds !== undefined) {
      query.set('end_seconds', String(params.end_seconds));
    }
    if (params.speaker !== undefined) query.set('speaker', params.speaker);

    const qs = query.toString();
    const path = `/v1/jobs/${encodeURIComponent(id)}/result${qs ? `?${qs}` : ''}`;

    if (params.format !== undefined && TEXT_FORMATS.has(params.format)) {
      return this.requestText('GET', path);
    }
    return this.requestJson<Transcript>('GET', path);
  }

  async deleteJob(id: string): Promise<void> {
    await this.requestJson<unknown>('DELETE', `/v1/jobs/${encodeURIComponent(id)}`);
  }

  async transcribeSync(body: TranscribeSyncBody): Promise<Transcript> {
    return this.requestJson<Transcript>('POST', '/v1/transcribe', body);
  }

  private authHeaders(extra?: Record<string, string>): Record<string, string> {
    const headers: Record<string, string> = { ...extra };
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  private async requestJson<T>(method: string, path: string, body?: unknown): Promise<T> {
    const headers = this.authHeaders(
      body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
    );
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) {
      throw await this.toApiError(response);
    }
    if (response.status === 204) {
      return undefined as T;
    }
    return (await response.json()) as T;
  }

  private async requestText(method: string, path: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: this.authHeaders(),
    });
    if (!response.ok) {
      throw await this.toApiError(response);
    }
    return response.text();
  }

  private async toApiError(response: Response): Promise<ApiError> {
    let body: ApiErrorBody | undefined;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = undefined;
    }
    if (body?.error?.code && body.error.message) {
      return new ApiError({
        code: body.error.code,
        message: body.error.message,
        retryable: Boolean(body.error.retryable),
        field: body.error.field,
      });
    }
    return new ApiError({
      code: 'HTTP_ERROR',
      message: `Request to ${path(response)} failed with status ${response.status} ${response.statusText}`,
      retryable: response.status >= 500,
    });
  }
}

function path(response: Response): string {
  try {
    return new URL(response.url).pathname;
  } catch {
    return response.url;
  }
}
