/**
 * Hand-written TypeScript mirrors of the whisper-street HTTP API JSON shapes.
 *
 * Field names are kept snake_case to match the wire format exactly (see
 * docs/api/README.md) rather than being camelCased for TypeScript convention —
 * that keeps this file a direct, diffable mirror of the API's JSON, and avoids
 * a translation layer that could silently drift from the contract.
 *
 * Per docs/api/README.md#compatibility, the API may add new response fields at
 * any time within a major version. Consumers of these types must not assume a
 * shape is exhaustive; extra unknown fields are expected and ignored.
 */

/** A job's lifecycle state. See docs/api/README.md#job-lifecycle. */
export type JobState =
  | 'queued'
  | 'running'
  | 'succeeded'
  | 'partial'
  | 'failed'
  | 'cancelled';

/** A span of audio that failed to process, with why. Timestamps in seconds. */
export interface FailedSpan {
  start_seconds: number;
  end_seconds: number;
  reason: string;
}

/**
 * The pipeline configuration that produced (or will produce) a result.
 * Echoed back on every result per docs/api/README.md design principle 3.
 */
export interface PipelineConfig {
  model?: string;
  isolation_profile?: string;
  diarization?: boolean;
  timestamp_granularity?: 'word' | 'segment';
  language?: string;
  output_formats?: string[];
}

/** A single recognized word with timing, in seconds. */
export interface Word {
  text: string;
  start_seconds: number;
  end_seconds: number;
  confidence?: number;
  speaker?: string;
}

/** A contiguous span of transcript, in seconds. */
export interface Segment {
  start_seconds: number;
  end_seconds: number;
  text: string;
  speaker?: string;
  confidence?: number;
  words?: Word[];
}

/** The canonical structured transcript. SRT/VTT/text are renderings of this. */
export interface Transcript {
  job_id: string;
  language?: string;
  segments: Segment[];
  config: PipelineConfig;
  failed_spans?: FailedSpan[];
}

/** Status of a job, and — once complete — its summary fields. */
export interface JobStatus {
  job_id: string;
  state: JobState;
  config?: PipelineConfig;
  duration_processed_seconds?: number;
  speakers_detected?: number;
  segment_count?: number;
  mean_confidence?: number;
  detected_language?: string;
  failed_spans?: FailedSpan[];
  created_at?: string;
  updated_at?: string;
}

/** Per-deployment limits, published so a caller (or agent) can plan around them. */
export interface CapabilityLimits {
  max_file_size_bytes: number;
  max_audio_duration_seconds: number;
  max_concurrent_jobs_per_caller: number;
  request_rate_limit_per_minute: number;
  result_retention_period_seconds: number;
}

/** What a given deployment supports: models, languages, formats, limits. */
export interface Capabilities {
  models: string[];
  languages: string[];
  output_formats: string[];
  isolation_profiles?: string[];
  url_fetch_enabled: boolean;
  limits: CapabilityLimits;
}

/** Liveness/readiness body for GET /v1/health. */
export interface HealthStatus {
  status: string;
}

/** The structured error body every non-2xx response carries. */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    field?: string;
    retryable: boolean;
  };
}
