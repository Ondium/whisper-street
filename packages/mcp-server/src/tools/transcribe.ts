import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import type { WhisperStreetClient } from '../client.js';
import { toToolError } from '../errors.js';
import type { JobStatus, Transcript } from '../types.js';

export const name = 'transcribe';

export const description =
  'Run the full pipeline (isolation + transcription) on an audio source. Returns ' +
  'a job handle plus an inline summary — never the full transcript inline (see ' +
  'docs/mcp/README.md#return-shapes); call get_transcript separately once the ' +
  'job has succeeded. By default (async=false) this blocks and processes ' +
  'synchronously, which this deployment\'s capabilities may cap to short audio ' +
  'only — pass async=true for anything longer, or after checking ' +
  'describe_capabilities().limits.max_audio_duration_seconds.';

const pipelineConfigShape = z.object({
  model: z
    .string()
    .optional()
    .describe('Transcription model name from describe_capabilities().models. Deployment default if omitted.'),
  isolation_profile: z
    .string()
    .optional()
    .describe('Isolation profile name from describe_capabilities().isolation_profiles. Deployment default if omitted.'),
  diarization: z
    .boolean()
    .optional()
    .describe('Whether to identify and label distinct speakers. Deployment default if omitted.'),
  timestamp_granularity: z
    .enum(['word', 'segment'])
    .optional()
    .describe('Timestamp precision: per-word or per-segment. Deployment default if omitted.'),
  language: z
    .string()
    .optional()
    .describe('Expected language (e.g. an ISO 639-1 code). Auto-detected if omitted.'),
  output_formats: z
    .array(z.string())
    .optional()
    .describe('Rendered formats to prepare in addition to JSON, e.g. ["srt","vtt"]. None extra if omitted.'),
});

export const inputShape = {
  source: z
    .string()
    .describe(
      'Audio source: a URL. Server-side URL fetching is disabled by default (SSRF ' +
        'surface — see docs/api/README.md#submitting-a-job); if this deployment has ' +
        'not enabled and allowlisted URL fetching, this call fails with a tool error ' +
        'naming that.',
    ),
  config: pipelineConfigShape
    .partial()
    .optional()
    .describe('Pipeline configuration overrides. Optional; deployment defaults apply to any field omitted.'),
  async: z
    .boolean()
    .optional()
    .default(false)
    .describe(
      'false (default): process synchronously and block until done or until the ' +
        'deployment\'s sync duration limit rejects the request. true: submit as a ' +
        'job and return immediately with { job_id, state: "queued" } to poll via ' +
        'get_job.',
    ),
  webhook_url: z
    .string()
    .optional()
    .describe('Only used when async=true. URL this deployment POSTs to on job completion. Optional.'),
};

export type TranscribeInput = z.infer<z.ZodObject<typeof inputShape>>;

const SUMMARY_FIELDS = [
  'duration_processed_seconds',
  'speakers_detected',
  'segment_count',
  'mean_confidence',
  'detected_language',
  'failed_spans',
] as const;

function summarizeJobStatus(job: JobStatus): Record<string, unknown> {
  const summary: Record<string, unknown> = { job_id: job.job_id, state: job.state };
  for (const field of SUMMARY_FIELDS) {
    const value = job[field];
    if (value !== undefined) {
      summary[field] = value;
    }
  }
  return summary;
}

/**
 * Project a synchronous transcribe result down to the same handle+summary
 * shape as the async path, so this tool never returns transcript segments
 * inline regardless of which path the caller took.
 */
function summarizeSyncResult(result: Transcript): Record<string, unknown> {
  const summary: Record<string, unknown> = {
    job_id: result.job_id,
    state: 'succeeded',
    segment_count: result.segments.length,
  };
  if (result.language !== undefined) summary.detected_language = result.language;
  if (result.failed_spans !== undefined) summary.failed_spans = result.failed_spans;
  return summary;
}

export function createHandler(client: WhisperStreetClient) {
  return async (args: TranscribeInput): Promise<CallToolResult> => {
    try {
      const body = { source: args.source, config: args.config };
      const summary = args.async
        ? summarizeJobStatus(await client.createJob({ ...body, webhook_url: args.webhook_url }))
        : summarizeSyncResult(await client.transcribeSync(body));
      return {
        content: [{ type: 'text', text: JSON.stringify(summary, null, 2) }],
        structuredContent: summary,
      };
    } catch (err) {
      return toToolError(err);
    }
  };
}

export function register(server: McpServer, client: WhisperStreetClient): void {
  server.registerTool(name, { description, inputSchema: inputShape }, createHandler(client));
}
