import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../store/auth";

// Resolve the API base URL even if VITE_API_BASE_URL wasn't set.
const BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ||
  `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
});

// Attach bearer token to every request.
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Queue 401s while we refresh the token, then replay the originals.
let refreshing: Promise<void> | null = null;
api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retried?: boolean };
    if (error.response?.status !== 401 || !original || original._retried) {
      return Promise.reject(error);
    }
    const { refreshToken, setTokens, logout } = useAuthStore.getState();
    if (!refreshToken) {
      logout();
      return Promise.reject(error);
    }
    original._retried = true;
    if (!refreshing) {
      refreshing = (async () => {
        try {
          const res = await axios.post(`${BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const data = res.data;
          setTokens(data.access_token, data.refresh_token);
        } catch {
          logout();
        } finally {
          refreshing = null;
        }
      })();
    }
    await refreshing;
    const newToken = useAuthStore.getState().accessToken;
    if (newToken && original.headers) {
      original.headers.Authorization = `Bearer ${newToken}`;
    }
    return api(original);
  }
);
