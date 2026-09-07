import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { noBackendEndpointError, toToolError } from '../errors.js';

export const name = 'isolate_voice';

export const description =
  'STUB — schema-complete, not yet backed by an HTTP endpoint. Once implemented, ' +
  'this will run voice isolation only (no transcription), producing cleaned ' +
  'audio for a caller doing its own speech recognition. Calling this tool today ' +
  'makes no network request and always returns a NO_BACKEND_ENDPOINT tool error.';

export const inputShape = {
  source: z
    .string()
    .describe(
      'Audio source to isolate: a URL. Subject to this deployment\'s URL-fetch ' +
        'policy (disabled by default; see docs/api/README.md#submitting-a-job).',
    ),
  config: z
    .object({
      isolation_profile: z
        .string()
        .optional()
        .describe(
          'Name of an isolation profile from describe_capabilities().isolation_profiles. ' +
            'Defaults to the deployment\'s default profile when omitted.',
        ),
    })
    .optional()
    .describe('Isolation-specific configuration. Optional; deployment defaults apply when omitted.'),
};

export type IsolateVoiceInput = z.infer<z.ZodObject<typeof inputShape>>;

export function createHandler() {
  return async (_args: IsolateVoiceInput): Promise<CallToolResult> => {
    return toToolError(
      noBackendEndpointError(name, 'POST /v1/isolate (or equivalent) is not in the HTTP API yet'),
    );
  };
}

export function register(server: McpServer): void {
  server.registerTool(name, { description, inputSchema: inputShape }, createHandler());
}
