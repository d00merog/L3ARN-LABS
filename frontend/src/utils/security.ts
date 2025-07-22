/**
 * Frontend Security Utilities
 * Client-side security measures and input sanitization
 */

import DOMPurify from 'dompurify';

interface SecurityConfig {
  maxInputLength: number;
  allowedFileTypes: string[];
  maxFileSize: number;
  csrfToken?: string;
}

const DEFAULT_SECURITY_CONFIG: SecurityConfig = {
  maxInputLength: 10000,
  allowedFileTypes: ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.md', '.py', '.js', '.ts'],
  maxFileSize: 10 * 1024 * 1024 // 10MB
};

class SecurityManager {
  private config: SecurityConfig;
  private csrfToken: string | null = null;

  constructor(config: Partial<SecurityConfig> = {}) {
    this.config = { ...DEFAULT_SECURITY_CONFIG, ...config };
    this.initializeCSRFToken();
  }

  /**
   * Initialize CSRF token from meta tag or API
   */
  private initializeCSRFToken(): void {
    // Try to get CSRF token from meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (metaToken) {
      this.csrfToken = metaToken;
      return;
    }

    // Generate client-side token if not provided by server
    this.csrfToken = this.generateSecureToken();
  }

  /**
   * Generate secure random token
   */
  private generateSecureToken(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * Sanitize HTML input to prevent XSS
   */
  sanitizeHTML(input: string): string {
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'],
      ALLOWED_ATTR: ['href', 'target'],
      ALLOW_DATA_ATTR: false
    });
  }

  /**
   * Sanitize plain text input
   */
  sanitizeText(input: string): string {
    if (typeof input !== 'string') {
      throw new Error('Input must be a string');
    }

    // Remove null bytes and control characters
    let sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
    
    // Trim and limit length
    sanitized = sanitized.trim().slice(0, this.config.maxInputLength);
    
    // Remove script tags and javascript: protocols
    sanitized = sanitized.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    sanitized = sanitized.replace(/javascript:/gi, '');
    sanitized = sanitized.replace(/data:/gi, '');
    sanitized = sanitized.replace(/vbscript:/gi, '');
    
    return sanitized;
  }

  /**
   * Validate and sanitize file input
   */
  validateFile(file: File): { valid: boolean; error?: string; sanitizedName?: string } {
    // Check file size
    if (file.size > this.config.maxFileSize) {
      return {
        valid: false,
        error: `File size exceeds maximum allowed size of ${this.config.maxFileSize / (1024 * 1024)}MB`
      };
    }

    // Check file type
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!this.config.allowedFileTypes.includes(extension)) {
      return {
        valid: false,
        error: `File type ${extension} is not allowed`
      };
    }

    // Sanitize filename
    const sanitizedName = this.sanitizeFilename(file.name);

    return {
      valid: true,
      sanitizedName
    };
  }

  /**
   * Sanitize filename
   */
  sanitizeFilename(filename: string): string {
    // Remove path separators and dangerous characters
    let sanitized = filename.replace(/[\/\\<>:"|?*]/g, '');
    
    // Remove leading/trailing dots and spaces
    sanitized = sanitized.replace(/^[\s.]+|[\s.]+$/g, '');
    
    // Ensure reasonable length
    if (sanitized.length > 255) {
      const parts = sanitized.split('.');
      const extension = parts.length > 1 ? '.' + parts.pop() : '';
      const name = parts.join('.').slice(0, 250 - extension.length);
      sanitized = name + extension;
    }

    return sanitized || 'file';
  }

  /**
   * Validate email format
   */
  validateEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email) && email.length <= 254;
  }

  /**
   * Validate URL
   */
  validateURL(url: string): boolean {
    try {
      const urlObj = new URL(url);
      return ['http:', 'https:'].includes(urlObj.protocol);
    } catch {
      return false;
    }
  }

  /**
   * Get CSRF token for requests
   */
  getCSRFToken(): string | null {
    return this.csrfToken;
  }

  /**
   * Add security headers to fetch requests
   */
  getSecureHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    };

    if (this.csrfToken) {
      headers['X-CSRF-Token'] = this.csrfToken;
    }

    return headers;
  }

  /**
   * Secure localStorage wrapper
   */
  secureStorage = {
    setItem: (key: string, value: string): void => {
      try {
        // Add timestamp and checksum for integrity
        const data = {
          value,
          timestamp: Date.now(),
          checksum: this.generateChecksum(value)
        };
        localStorage.setItem(key, JSON.stringify(data));
      } catch (error) {
        console.error('Secure storage set error:', error);
      }
    },

    getItem: (key: string): string | null => {
      try {
        const storedData = localStorage.getItem(key);
        if (!storedData) return null;

        const data = JSON.parse(storedData);
        
        // Verify checksum
        if (this.generateChecksum(data.value) !== data.checksum) {
          console.warn('Storage integrity check failed for key:', key);
          this.secureStorage.removeItem(key);
          return null;
        }

        // Check if data is too old (24 hours)
        if (Date.now() - data.timestamp > 24 * 60 * 60 * 1000) {
          this.secureStorage.removeItem(key);
          return null;
        }

        return data.value;
      } catch (error) {
        console.error('Secure storage get error:', error);
        return null;
      }
    },

    removeItem: (key: string): void => {
      localStorage.removeItem(key);
    },

    clear: (): void => {
      localStorage.clear();
    }
  };

  /**
   * Generate simple checksum for data integrity
   */
  private generateChecksum(data: string): string {
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(36);
  }

  /**
   * Rate limiting for client-side requests
   */
  private requestCounts: Map<string, { count: number; resetTime: number }> = new Map();

  isRequestAllowed(endpoint: string, maxRequests: number = 100, windowMs: number = 60000): boolean {
    const now = Date.now();
    const key = endpoint;
    
    const current = this.requestCounts.get(key);
    
    if (!current || now > current.resetTime) {
      this.requestCounts.set(key, { count: 1, resetTime: now + windowMs });
      return true;
    }
    
    if (current.count >= maxRequests) {
      return false;
    }
    
    current.count++;
    return true;
  }

  /**
   * Content Security Policy violation reporter
   */
  setupCSPReporting(): void {
    document.addEventListener('securitypolicyviolation', (event) => {
      console.warn('CSP Violation:', {
        violatedDirective: event.violatedDirective,
        blockedURI: event.blockedURI,
        originalPolicy: event.originalPolicy
      });

      // Report to analytics or security service
      this.reportSecurityEvent('csp_violation', {
        directive: event.violatedDirective,
        blockedURI: event.blockedURI,
        lineNumber: event.lineNumber,
        sourceFile: event.sourceFile
      });
    });
  }

  /**
   * Report security events
   */
  private reportSecurityEvent(eventType: string, details: any): void {
    // This would typically send to a security monitoring service
    console.log('Security Event:', { eventType, details, timestamp: new Date().toISOString() });
    
    // You could integrate with services like Sentry, LogRocket, etc.
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'security_event', {
        event_category: 'security',
        event_label: eventType,
        value: 1
      });
    }
  }

  /**
   * Detect and prevent clickjacking
   */
  preventClickjacking(): void {
    if (window.top !== window.self) {
      console.warn('Potential clickjacking attempt detected');
      this.reportSecurityEvent('clickjacking_attempt', { 
        topOrigin: document.referrer 
      });
      
      // Break out of frame
      window.top!.location = window.self.location;
    }
  }

  /**
   * Initialize all security measures
   */
  initialize(): void {
    this.setupCSPReporting();
    this.preventClickjacking();
    
    console.log('🛡️ Security manager initialized');
  }
}

// Create global security manager instance
export const securityManager = new SecurityManager();

// Initialize security on module load
if (typeof window !== 'undefined') {
  securityManager.initialize();
}

// Export types and utilities
export type { SecurityConfig };
export default SecurityManager;