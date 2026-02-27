/**
 * Authentication utilities
 */

import {
  AUTH_COOKIE_KEY,
  AUTH_TOKEN_KEY,
  AUTH_TOKEN_MAX_AGE_SECONDS,
} from './utils/auth-constants';

const writeTokenCookie = (token: string) => {
  if (typeof document === 'undefined') return;
  const isHttps = window.location.protocol === 'https:';
  const secureAttr = isHttps ? '; Secure' : '';
  document.cookie = `${AUTH_COOKIE_KEY}=${encodeURIComponent(token)}; Path=/; Max-Age=${AUTH_TOKEN_MAX_AGE_SECONDS}; SameSite=Lax${secureAttr}`;
};

const clearTokenCookie = () => {
  if (typeof document === 'undefined') return;
  const isHttps = window.location.protocol === 'https:';
  const secureAttr = isHttps ? '; Secure' : '';
  document.cookie = `${AUTH_COOKIE_KEY}=; Path=/; Max-Age=0; SameSite=Lax${secureAttr}`;
};

export const setToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    writeTokenCookie(token);
  }
};

export const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  }
  return null;
};

export const removeToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    clearTokenCookie();
  }
};

export const isAuthenticated = (): boolean => {
  return !!getToken();
};
