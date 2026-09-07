/**
 * Error types shared by the HTTP client and the tool layer.
 *
 * Per docs/mcp/README.md#errors: failures are returned as tool errors with a
 * stable code, a message that states the corrective action, and a retryable
 * flag — written for a model to act on, not just a human.
 */
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';

export interface ApiErrorOptions {
  code: string;
  message: string;
  retryable: boolean;
  field?: string;
}

/** An error surfaced by the whisper-street HTTP API, or synthesized locally. */
export class ApiError extends Error {
  readonly code: string;
  readonly retryable: boolean;
  readonly field?: string;

  constructor(options: ApiErrorOptions) {
    super(options.message);
    this.name = 'ApiError';
    this.code = options.code;
    this.retryable = options.retryable;
    this.field = options.field;
  }
}

/**
 * Client-only error code for tools with no backing HTTP endpoint yet
 * (inspect_audio, isolate_voice, search_transcript). These tools are
 * schema-complete — an agent can read their contract and call them
 * correctly — but the whisper-street HTTP API does not implement the
 * corresponding endpoint. No network call is made for these tools.
 */
export const NO_BACKEND_ENDPOINT = 'NO_BACKEND_ENDPOINT';

export function noBackendEndpointError(toolName: string, missingEndpoint: string): ApiError {
  return new ApiError({
    code: NO_BACKEND_ENDPOINT,
    message:
      `${toolName} has no backing HTTP endpoint yet: ${missingEndpoint} is not ` +
      'implemented by this deployment\'s whisper-street API. This is tracked for ' +
      'the v1 governance review (see docs/mcp/README.md); do not retry, and do ' +
      'not fall back to another tool to synthesize this result.',
    retryable: false,
  });
}

/** Render any thrown error as an MCP tool error result. */
export function toToolError(err: unknown): CallToolResult {
  if (err instanceof ApiError) {
    const lines = [
      `code: ${err.code}`,
      `message: ${err.message}`,
      `retryable: ${err.retryable}`,
    ];
    if (err.field) {
      lines.push(`field: ${err.field}`);
    }
    return { content: [{ type: 'text', text: lines.join('\n') }], isError: true };
  }
  const message = err instanceof Error ? err.message : String(err);
  return {
    content: [
      {
        type: 'text',
        text: `code: UNKNOWN_ERROR\nmessage: ${message}\nretryable: false`,
      },
    ],
    isError: true,
  };
}
