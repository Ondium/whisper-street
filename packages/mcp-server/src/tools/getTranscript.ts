import { z } from 'zod';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import type { WhisperStreetClient } from '../client.js';
import { toToolError } from '../errors.js';

export const name = 'get_transcript';

export const description =
  'Fetch a completed job\'s result: the whole transcript, a time range, a single ' +
  'speaker\'s lines, or a rendering in a specific format. The structured JSON is ' +
  'canonical; text/srt/vtt are renderings of it (see docs/api/README.md#design-principles). ' +
  'Returns a structured tool error (e.g. job not succeeded yet) instead of a ' +
  'partial or guessed result.';

export const inputShape = {
  job_id: z.string().describe('The job ID returned by transcribe(async=true) or get_job().'),
  format: z
    .enum(['json', 'text', 'srt', 'vtt'])
    .optional()
    .default('json')
    .describe('Output rendering. Default: "json" (the canonical structured transcript).'),
  start_seconds: z
    .number()
    .nonnegative()
    .optional()
    .describe('Only return content at or after this offset, in seconds. Omit for the start of the audio.'),
  end_seconds: z
    .number()
    .nonnegative()
    .optional()
    .describe('Only return content at or before this offset, in seconds. Omit for the end of the audio.'),
  speaker: z
    .string()
    .optional()
    .describe('Only return segments attributed to this speaker label. Omit for all speakers.'),
};

export type GetTranscriptInput = z.infer<z.ZodObject<typeof inputShape>>;

export function createHandler(client: WhisperStreetClient) {
  return async (args: GetTranscriptInput): Promise<CallToolResult> => {
    try {
      const result = await client.getJobResult(args.job_id, {
        format: args.format,
        start_seconds: args.start_seconds,
        end_seconds: args.end_seconds,
        speaker: args.speaker,
      });
      if (typeof result === 'string') {
        return {
          content: [{ type: 'text', text: result }],
          structuredContent: { job_id: args.job_id, format: args.format, content: result },
        };
      }
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        structuredContent: result as unknown as Record<string, unknown>,
      };
    } catch (err) {
      return toToolError(err);
    }
  };
}

export function register(server: McpServer, client: WhisperStreetClient): void {
  server.registerTool(name, { description, inputSchema: inputShape }, createHandler(client));
}
