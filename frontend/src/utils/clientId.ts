/**
 * Utility functions for managing client ID in cookies
 */

const CLIENT_ID_COOKIE_NAME = 'renter_chat_client_id';
const COOKIE_EXPIRY_DAYS = 30;

/**
 * Generate a new UUID-like client ID
 */
function generateClientId(): string {
  return 'client_' + Math.random().toString(36).substring(2) + '_' + Date.now().toString(36);
}

/**
 * Set a cookie with the given name, value, and expiry days
 */
function setCookie(name: string, value: string, days: number): void {
  const expires = new Date();
  expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

/**
 * Get a cookie value by name
 */
function getCookie(name: string): string | null {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

/**
 * Get or create a client ID, storing it in a cookie
 */
export function getOrCreateClientId(): string {
  let clientId = getCookie(CLIENT_ID_COOKIE_NAME);
  
  if (!clientId) {
    clientId = generateClientId();
    setCookie(CLIENT_ID_COOKIE_NAME, clientId, COOKIE_EXPIRY_DAYS);
    console.log('Created new client ID:', clientId);
  } else {
    console.log('Using existing client ID:', clientId);
  }
  
  return clientId;
}

/**
 * Clear the client ID cookie (for testing or logout)
 */
export function clearClientId(): void {
  document.cookie = `${CLIENT_ID_COOKIE_NAME}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
  console.log('Cleared client ID cookie');
}

/**
 * Get the current client ID without creating a new one
 */
export function getCurrentClientId(): string | null {
  return getCookie(CLIENT_ID_COOKIE_NAME);
}