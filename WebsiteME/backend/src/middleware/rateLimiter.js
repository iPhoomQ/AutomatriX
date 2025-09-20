const rateLimit = require('express-rate-limit');

/**
 * General API rate limiting
 */
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Strict rate limiting for authentication endpoints
 */
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  message: {
    error: 'Too many authentication attempts, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Code execution rate limiting (more restrictive)
 */
const codeLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 10, // limit each IP to 10 code executions per minute
  message: {
    error: 'Code execution rate limit exceeded. Please wait before running more code.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Search rate limiting
 */
const searchLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 30, // limit each IP to 30 searches per minute
  message: {
    error: 'Search rate limit exceeded. Please wait before searching again.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Post creation rate limiting
 */
const postLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // limit each IP to 10 posts per 15 minutes
  message: {
    error: 'Post creation rate limit exceeded. Please wait before creating more posts.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

module.exports = {
  generalLimiter,
  authLimiter,
  codeLimiter,
  searchLimiter,
  postLimiter
};