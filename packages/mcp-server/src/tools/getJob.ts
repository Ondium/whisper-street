import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import type { WhisperStreetClient } from '../client.js';
import { toToolError } from '../errors.js';

export const name = 'get_job';

export const description =
  'Fetch the status of a job: its lifecycle state (queued, running, succeeded, ' +
  'partial, failed, or cancelled — see docs/api/README.md#job-lifecycle) plus, ' +
  'once processing has produced results, duration_processed_seconds, ' +
  'speakers_detected, segment_count, mean_confidence, detected_language, and ' +
  'failed_spans. Does not return the transcript itself — call get_transcript ' +
  'for that once state is succeeded or partial.';

export const inputShape = {
  job_id: z.string().describe('The job ID returned by transcribe(async=true).'),
};

export type GetJobInput = z.infer<z.ZodObject<typeof inputShape>>;

export function createHandler(client: WhisperStreetClient) {
  return async (args: GetJobInput): Promise<CallToolResult> => {
    try {
      const job = await client.getJob(args.job_id);
      return {
        content: [{ type: 'text', text: JSON.stringify(job, null, 2) }],
        structuredContent: job as unknown as Record<string, unknown>,
      };
    } catch (err) {
      return toToolError(err);
    }
  };
}

export function register(server: McpServer, client: WhisperStreetClient): void {
  server.registerTool(name, { description, inputSchema: inputShape }, createHandler(client));
}
