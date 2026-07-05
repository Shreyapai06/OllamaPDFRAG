declare global {
  interface Window { __env?: Record<string, string>; }
}

export const environment = {
  apiUrl: window.__env?.['NG_APP_API_URL'] || 'http://localhost:8000',
};
