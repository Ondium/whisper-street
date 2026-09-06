import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { noBackendEndpointError, toToolError } from '../errors.js';

export const name = 'inspect_audio';

export const description =
  'STUB — schema-complete, not yet backed by an HTTP endpoint. Once implemented, ' +
  'this will return cheap metadata about an audio source without running the ' +
  'pipeline on it: { duration_seconds: number, channels: number, ' +
  'sample_rate_hz: number, estimated_speaker_count: number }, so a caller can ' +
  'plan (e.g. decide sync vs. async transcribe) before paying for processing. ' +
  'Calling this tool today makes no network request and always returns a ' +
  'NO_BACKEND_ENDPOINT tool error.';

export const inputShape = {
  source: z
    .string()
    .describe(
      'Audio source to inspect: a URL. Subject to this deployment\'s URL-fetch ' +
        'policy (disabled by default; see docs/api/README.md#submitting-a-job).',
    ),
};

export type InspectAudioInput = z.infer<z.ZodObject<typeof inputShape>>;

export function createHandler() {
  return async (_args: InspectAudioInput): Promise<CallToolResult> => {
    return toToolError(
      noBackendEndpointError(name, 'GET /v1/audio/inspect (or equivalent) is not in the HTTP API yet'),
    );
  };
}

export function register(server: McpServer): void {
  server.registerTool(name, { description, inputSchema: inputShape }, createHandler());
}
