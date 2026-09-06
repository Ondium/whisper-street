/**
 * Server configuration, read from the environment.
 *
 * WHISPER_STREET_API_URL — base URL of the whisper-street HTTP API.
 *   Default: "http://localhost:8000".
 * WHISPER_STREET_API_KEY — bearer token forwarded as `Authorization: Bearer
 *   <key>` on every request. Optional; omitted entirely when unset.
 */
export interface Config {
  apiUrl: string;
  apiKey?: string;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): Config {
  const apiUrl = env.WHISPER_STREET_API_URL?.trim();
  const apiKey = env.WHISPER_STREET_API_KEY?.trim();
  return {
    apiUrl: apiUrl && apiUrl.length > 0 ? apiUrl : 'http://localhost:8000',
    apiKey: apiKey && apiKey.length > 0 ? apiKey : undefined,
  };
}
