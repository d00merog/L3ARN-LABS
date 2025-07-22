/**
 * Secure API Client
 * Enhanced API client with security features and error handling
 */

import { securityManager } from '../utils/security';

interface ApiRequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: HeadersInit;
  body?: any;
  timeout?: number;
  retries?: number;
  cacheable?: boolean;
}

interface ApiResponse<T> {
  data: T;
  status: number;
  headers: Headers;
  success: boolean;
}

interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

class SecureApiClient {
  private baseURL: string;
  private defaultTimeout: number = 30000;
  private requestCache: Map<string, { data: any; expires: number }> = new Map();

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseURL = baseURL.replace(/\/$/, ''); // Remove trailing slash
  }

  /**
   * Make secure API request
   */
  async request<T>(
    endpoint: string, 
    config: ApiRequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const {
      method = 'GET',
      body,
      timeout = this.defaultTimeout,
      retries = 3,
      cacheable = false
    } = config;

    // Check client-side rate limiting
    if (!securityManager.isRequestAllowed(endpoint)) {
      throw new ApiError({
        message: 'Too many requests. Please try again later.',
        status: 429,
        code: 'RATE_LIMITED'
      });
    }

    // Check cache for GET requests
    if (method === 'GET' && cacheable) {
      const cached = this.getFromCache(endpoint);
      if (cached) {
        return {
          data: cached,
          status: 200,
          headers: new Headers(),
          success: true
        };
      }
    }

    const url = `${this.baseURL}${endpoint}`;
    
    // Prepare headers with security measures
    const headers = new Headers({
      ...securityManager.getSecureHeaders(),
      ...config.headers
    });

    // Add authentication token if available
    const token = this.getAuthToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    // Prepare request body
    let requestBody: string | FormData | undefined;
    if (body) {
      if (body instanceof FormData) {
        requestBody = body;
        // Don't set Content-Type for FormData (browser sets it with boundary)
        headers.delete('Content-Type');
      } else {
        requestBody = JSON.stringify(this.sanitizeRequestBody(body));
      }
    }

    // Create abort controller for timeout
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => abortController.abort(), timeout);

    try {
      const response = await this.executeRequestWithRetry({
        url,
        method,
        headers,
        body: requestBody,
        signal: abortController.signal
      }, retries);

      clearTimeout(timeoutId);

      // Handle response
      if (!response.ok) {
        await this.handleErrorResponse(response);
      }

      const responseData = await this.parseResponse<T>(response);

      // Cache successful GET responses
      if (method === 'GET' && cacheable && response.status === 200) {
        this.setCache(endpoint, responseData, 5 * 60 * 1000); // 5 minutes
      }

      return {
        data: responseData,
        status: response.status,
        headers: response.headers,
        success: true
      };

    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof ApiError) {
        throw error;
      }

      // Handle network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new ApiError({
          message: 'Network error. Please check your connection.',
          status: 0,
          code: 'NETWORK_ERROR'
        });
      }

      // Handle timeout
      if (error.name === 'AbortError') {
        throw new ApiError({
          message: 'Request timeout. Please try again.',
          status: 408,
          code: 'TIMEOUT'
        });
      }

      throw new ApiError({
        message: 'An unexpected error occurred.',
        status: 500,
        code: 'UNKNOWN_ERROR',
        details: error.message
      });
    }
  }

  /**
   * Execute request with exponential backoff retry
   */
  private async executeRequestWithRetry(
    requestInit: RequestInfo | URL & RequestInit, 
    retries: number
  ): Promise<Response> {
    let lastError: Error;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(requestInit.url, {
          method: requestInit.method,
          headers: requestInit.headers,
          body: requestInit.body,
          signal: requestInit.signal
        });

        // Don't retry on client errors (4xx) except specific cases
        if (response.status >= 400 && response.status < 500) {
          if (response.status === 429) {
            // Rate limited - wait and retry
            const retryAfter = response.headers.get('Retry-After');
            const delay = retryAfter ? parseInt(retryAfter) * 1000 : Math.pow(2, attempt) * 1000;
            await this.delay(delay);
            continue;
          }
          return response; // Don't retry other client errors
        }

        // Retry on server errors (5xx)
        if (response.status >= 500 && attempt < retries) {
          await this.delay(Math.pow(2, attempt) * 1000); // Exponential backoff
          continue;
        }

        return response;

      } catch (error) {
        lastError = error as Error;
        if (attempt < retries) {
          await this.delay(Math.pow(2, attempt) * 1000);
          continue;
        }
      }
    }

    throw lastError!;
  }

  /**
   * Parse API response safely
   */
  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('Content-Type');
    
    if (contentType && contentType.includes('application/json')) {
      try {
        return await response.json();
      } catch (error) {
        throw new ApiError({
          message: 'Invalid JSON response from server.',
          status: response.status,
          code: 'INVALID_JSON'
        });
      }
    }
    
    // Handle text responses
    if (contentType && contentType.includes('text/')) {
      return (await response.text()) as unknown as T;
    }
    
    // Handle binary responses
    return (await response.blob()) as unknown as T;
  }

  /**
   * Handle error responses
   */
  private async handleErrorResponse(response: Response): Promise<never> {
    let errorData: any;
    
    try {
      errorData = await response.json();
    } catch {
      // If JSON parsing fails, use status text
      errorData = { message: response.statusText || 'Unknown error' };
    }

    const apiError = new ApiError({
      message: errorData.message || errorData.detail || 'Request failed',
      status: response.status,
      code: errorData.code || this.getErrorCodeFromStatus(response.status),
      details: errorData
    });

    // Log security-relevant errors
    if (response.status === 401) {
      this.handleAuthenticationError();
    } else if (response.status === 403) {
      console.warn('Access forbidden:', errorData);
    } else if (response.status === 429) {
      console.warn('Rate limit exceeded:', errorData);
    }

    throw apiError;
  }

  /**
   * Sanitize request body to prevent injection attacks
   */
  private sanitizeRequestBody(body: any): any {
    if (typeof body === 'string') {
      return securityManager.sanitizeText(body);
    }

    if (typeof body === 'object' && body !== null) {
      const sanitized: any = Array.isArray(body) ? [] : {};
      
      for (const [key, value] of Object.entries(body)) {
        if (typeof value === 'string') {
          sanitized[key] = securityManager.sanitizeText(value);
        } else if (typeof value === 'object' && value !== null) {
          sanitized[key] = this.sanitizeRequestBody(value);
        } else {
          sanitized[key] = value;
        }
      }
      
      return sanitized;
    }

    return body;
  }

  /**
   * Get authentication token
   */
  private getAuthToken(): string | null {
    return securityManager.secureStorage.getItem('auth_token');
  }

  /**
   * Handle authentication errors
   */
  private handleAuthenticationError(): void {
    // Clear stored authentication data
    securityManager.secureStorage.removeItem('auth_token');
    securityManager.secureStorage.removeItem('user_data');
    
    // Redirect to login if in browser environment
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  /**
   * Get error code from HTTP status
   */
  private getErrorCodeFromStatus(status: number): string {
    const statusCodes: { [key: number]: string } = {
      400: 'BAD_REQUEST',
      401: 'UNAUTHORIZED', 
      403: 'FORBIDDEN',
      404: 'NOT_FOUND',
      409: 'CONFLICT',
      422: 'VALIDATION_ERROR',
      429: 'RATE_LIMITED',
      500: 'INTERNAL_ERROR',
      502: 'BAD_GATEWAY',
      503: 'SERVICE_UNAVAILABLE',
      504: 'GATEWAY_TIMEOUT'
    };

    return statusCodes[status] || 'UNKNOWN_ERROR';
  }

  /**
   * Simple delay utility
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Cache management
   */
  private getFromCache(key: string): any | null {
    const cached = this.requestCache.get(key);
    if (cached && cached.expires > Date.now()) {
      return cached.data;
    }
    
    this.requestCache.delete(key);
    return null;
  }

  private setCache(key: string, data: any, ttl: number): void {
    this.requestCache.set(key, {
      data,
      expires: Date.now() + ttl
    });
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.requestCache.clear();
  }

  /**
   * Convenience methods
   */
  async get<T>(endpoint: string, config?: Omit<ApiRequestConfig, 'method'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  async post<T>(endpoint: string, body?: any, config?: Omit<ApiRequestConfig, 'method' | 'body'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'POST', body });
  }

  async put<T>(endpoint: string, body?: any, config?: Omit<ApiRequestConfig, 'method' | 'body'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'PUT', body });
  }

  async patch<T>(endpoint: string, body?: any, config?: Omit<ApiRequestConfig, 'method' | 'body'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'PATCH', body });
  }

  async delete<T>(endpoint: string, config?: Omit<ApiRequestConfig, 'method'>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }

  /**
   * File upload with security validation
   */
  async uploadFile<T>(
    endpoint: string, 
    file: File, 
    additionalData?: Record<string, string>
  ): Promise<ApiResponse<T>> {
    // Validate file security
    const validation = securityManager.validateFile(file);
    if (!validation.valid) {
      throw new ApiError({
        message: validation.error!,
        status: 400,
        code: 'INVALID_FILE'
      });
    }

    const formData = new FormData();
    formData.append('file', file, validation.sanitizedName);

    // Add additional form data
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, securityManager.sanitizeText(value));
      });
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      body: formData
    });
  }
}

// Custom error class
class ApiError extends Error {
  public status: number;
  public code?: string;
  public details?: any;

  constructor({ message, status, code, details }: {
    message: string;
    status: number;
    code?: string;
    details?: any;
  }) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// Create and export global API client instance
export const apiClient = new SecureApiClient();

// Export types and classes
export type { ApiResponse, ApiError, ApiRequestConfig };
export { SecureApiClient, ApiError as ApiErrorClass };