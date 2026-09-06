import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import type { WhisperStreetClient } from '../client.js';
import { toToolError } from '../errors.js';

export const name = 'describe_capabilities';

export const description =
  'Discover what this whisper-street deployment actually supports, instead of ' +
  'assuming: available transcription models, supported languages, output ' +
  'formats, isolation profiles, and the limits every deployment publishes — ' +
  'max file size (bytes), max audio duration (seconds), max concurrent jobs per ' +
  'caller, request rate limit (requests per minute), and result retention ' +
  'period (seconds). Call this before calling transcribe or isolate_voice; ' +
  'deployments differ in what they have installed. Takes no arguments.';

/** Empty input: this tool takes no arguments. */
export const inputShape = {};

export function createHandler(client: WhisperStreetClient) {
  return async (): Promise<CallToolResult> => {
    try {
      const capabilities = await client.getCapabilities();
      return {
        content: [{ type: 'text', text: JSON.stringify(capabilities, null, 2) }],
        structuredContent: capabilities as unknown as Record<string, unknown>,
      };
    } catch (err) {
      return toToolError(err);
    }
  };
}

export function register(server: McpServer, client: WhisperStreetClient): void {
  server.registerTool(name, { description, inputSchema: inputShape }, createHandler(client));
}
