/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_ENABLE_GOOGLE_CALENDAR?: string;
  readonly VITE_ENABLE_CONVERSATION_HISTORY?: string;
  readonly VITE_ENABLE_DEBUG_LOGGING?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
