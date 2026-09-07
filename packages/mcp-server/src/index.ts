#!/usr/bin/env node
/**
 * whisper-street MCP server entry point.
 *
 * This is a thin wrapper over the whisper-street HTTP API (docs/api/README.md):
 * every tool either calls the API directly, or — for the three tools with no
 * backing endpoint yet — returns a NO_BACKEND_ENDPOINT tool error without
 * making a network call. No pipeline logic lives here.
 */
import { pathToFileURL } from 'node:url';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { WhisperStreetClient } from './client.js';
import { type Config, loadConfig } from './config.js';
import * as describeCapabilities from './tools/describeCapabilities.js';
import * as getJob from './tools/getJob.js';
import * as getTranscript from './tools/getTranscript.js';
import * as inspectAudio from './tools/inspectAudio.js';
import * as isolateVoice from './tools/isolateVoice.js';
import * as searchTranscript from './tools/searchTranscript.js';
import * as transcribe from './tools/transcribe.js';

const SERVER_INFO = { name: 'whisper-street-mcp', version: '0.1.0' };

/** Build a fully-wired MCP server. Exported so tests can construct one without stdio. */
export function buildServer(config: Config = loadConfig()): McpServer {
  const client = new WhisperStreetClient(config);
  const server = new McpServer(SERVER_INFO);

  describeCapabilities.register(server, client);
  inspectAudio.register(server);
  transcribe.register(server, client);
  isolateVoice.register(server);
  getJob.register(server, client);
  getTranscript.register(server, client);
  searchTranscript.register(server);

  return server;
}

async function main(): Promise<void> {
  const server = buildServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

const isMain = process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMain) {
  main().catch((err: unknown) => {
    console.error('whisper-street-mcp failed to start:', err);
    process.exitCode = 1;
  });
}
