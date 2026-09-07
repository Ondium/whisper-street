import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { noBackendEndpointError, toToolError } from '../errors.js';

export const name = 'search_transcript';

export const description =
  'STUB — schema-complete, not yet backed by an HTTP endpoint. Once implemented, ' +
  'this will find spans of a completed transcript matching a query without ' +
  'pulling the whole transcript into context — the context-economy path for ' +
  '"what did they say about X?" questions. Calling this tool today makes no ' +
  'network request and always returns a NO_BACKEND_ENDPOINT tool error.';

export const inputShape = {
  job_id: z.string().describe('The job ID returned by transcribe() or get_job().'),
  query: z.string().describe('Text or phrase to search for within the transcript.'),
  max_results: z
    .number()
    .int()
    .positive()
    .optional()
    .default(20)
    .describe('Maximum number of matching spans to return. Default: 20.'),
};

export type SearchTranscriptInput = z.infer<z.ZodObject<typeof inputShape>>;

export function createHandler() {
  return async (_args: SearchTranscriptInput): Promise<CallToolResult> => {
    return toToolError(
      noBackendEndpointError(
        name,
        'GET /v1/jobs/{id}/search (or equivalent) is not in the HTTP API yet',
      ),
    );
  };
}

export function register(server: McpServer): void {
  server.registerTool(name, { description, inputSchema: inputShape }, createHandler());
}
