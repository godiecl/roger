/**
 * Input Sanitization Utilities
 * Protects against XSS and injection attacks
 */

/**
 * Escape HTML special characters to prevent XSS
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };

  return text.replace(/[&<>"'/]/g, (char) => map[char] || char);
}

/**
 * Remove all HTML tags from a string
 */
export function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, '');
}

/**
 * Sanitize email input
 */
export function sanitizeEmail(email: string): string {
  return email
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9@._+-]/g, '');
}

/**
 * Sanitize username (alphanumeric, underscore, hyphen)
 */
export function sanitizeUsername(username: string): string {
  return username
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9_-]/g, '');
}

/**
 * Sanitize general text input
 */
export function sanitizeText(text: string, maxLength: number = 1000): string {
  return escapeHtml(text.trim()).slice(0, maxLength);
}

/**
 * Validate and sanitize URL
 */
export function sanitizeUrl(url: string): string | null {
  try {
    const parsed = new URL(url);

    // Only allow http and https protocols
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return null;
    }

    return parsed.toString();
  } catch {
    return null;
  }
}

/**
 * Remove potentially dangerous SQL characters (for additional safety)
 * Note: You should ALWAYS use parameterized queries in the backend
 */
export function sanitizeSqlInput(input: string): string {
  return input.replace(/['";\\]/g, '');
}

/**
 * Sanitize search query
 */
export function sanitizeSearchQuery(query: string): string {
  return query
    .trim()
    .replace(/[<>'"]/g, '')
    .slice(0, 200); // Limit search query length
}

/**
 * Validate file name
 */
export function sanitizeFileName(fileName: string): string {
  return fileName
    .replace(/[^a-zA-Z0-9._-]/g, '_')
    .replace(/\.{2,}/g, '.') // Prevent directory traversal
    .slice(0, 255); // Max filename length
}

/**
 * Check if string contains potential XSS patterns
 */
export function containsXss(input: string): boolean {
  const xssPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i, // Event handlers like onclick=
    /<iframe/i,
    /<object/i,
    /<embed/i,
    /eval\(/i,
    /expression\(/i
  ];

  return xssPatterns.some(pattern => pattern.test(input));
}

/**
 * Comprehensive input validator
 */
export function validateInput(
  input: string,
  options: {
    maxLength?: number;
    allowHtml?: boolean;
    pattern?: RegExp;
  } = {}
): { valid: boolean; sanitized: string; errors: string[] } {
  const errors: string[] = [];
  let sanitized = input.trim();

  // Check max length
  if (options.maxLength && sanitized.length > options.maxLength) {
    errors.push(`Input exceeds maximum length of ${options.maxLength}`);
    sanitized = sanitized.slice(0, options.maxLength);
  }

  // Check for XSS if HTML not allowed
  if (!options.allowHtml && containsXss(sanitized)) {
    errors.push('Input contains potentially dangerous content');
    sanitized = stripHtml(sanitized);
  }

  // Validate pattern if provided
  if (options.pattern && !options.pattern.test(sanitized)) {
    errors.push('Input does not match required format');
  }

  // Sanitize HTML if not allowed
  if (!options.allowHtml) {
    sanitized = escapeHtml(sanitized);
  }

  return {
    valid: errors.length === 0,
    sanitized,
    errors
  };
}
