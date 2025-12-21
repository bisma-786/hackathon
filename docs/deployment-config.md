# Deployment and Environment Configuration

This document provides detailed information about deploying the RAG chatbot component and configuring environment variables for different deployment scenarios.

## Table of Contents
- [Environment Variables](#environment-variables)
- [Deployment Scenarios](#deployment-scenarios)
- [Configuration for Different Environments](#configuration-for-different-environments)
- [Backend Integration](#backend-integration)
- [Security Considerations](#security-considerations)
- [Monitoring and Logging](#monitoring-and-logging)
- [Performance Optimization](#performance-optimization)

## Environment Variables

The chatbot component uses the following environment variables:

### Required Variables
- `CHATBOT_API_ENDPOINT` - The URL of the backend RAG service
  - Example: `https://your-backend-service.com`
  - Default: `http://localhost:8000` (for development)

### Optional Variables
- `CHATBOT_TIMEOUT_MS` - Request timeout in milliseconds
  - Default: `30000` (30 seconds)
  - Minimum: `5000` (5 seconds)
  - Maximum: `60000` (60 seconds)

- `CHATBOT_API_KEY` - Authentication token for the backend service (if required)
  - Optional, only needed if the backend requires authentication

## Deployment Scenarios

### Local Development
```bash
# Create .env file in the project root
CHATBOT_API_ENDPOINT=http://localhost:8000
CHATBOT_TIMEOUT_MS=30000
```

### Staging Environment
```bash
# .env.staging
CHATBOT_API_ENDPOINT=https://staging-backend.yourdomain.com
CHATBOT_TIMEOUT_MS=45000
```

### Production Environment
```bash
# .env.production
CHATBOT_API_ENDPOINT=https://api.yourdomain.com
CHATBOT_TIMEOUT_MS=30000
CHATBOT_API_KEY=your_production_api_key_here
```

## Configuration for Different Environments

### Development
```javascript
// For local development
{
  chatbot: {
    enabled: true,
    apiEndpoint: process.env.CHATBOT_API_ENDPOINT || 'http://localhost:8000',
    showOnDocPages: true,
    showOnBlogPages: false,
    showOnNonDocPages: false,
    showSources: true,
    enableSelectedText: true
  }
}
```

### Production
```javascript
// For production deployment
{
  chatbot: {
    enabled: true,
    apiEndpoint: process.env.CHATBOT_API_ENDPOINT || 'https://api.yourdomain.com',
    showOnDocPages: true,
    showOnBlogPages: false,
    showOnNonDocPages: false,
    showSources: true,
    enableSelectedText: true
  }
}
```

## Backend Integration

### API Endpoint Requirements
The backend service must provide the following endpoints:

1. **Query Endpoint**: `POST /api/agent/query`
   - Accepts JSON payload with query and context
   - Returns AI-generated response with sources and metadata
   - Expected response format:
   ```json
   {
     "answer": "Response text",
     "sources": ["source1", "source2"],
     "confidence": 0.85,
     "retrieved_context": ["context1", "context2"],
     "followup_questions": ["Question 1?", "Question 2?"]
   }
   ```

2. **Health Check Endpoint**: `GET /health`
   - Returns service health status
   - Expected response format:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "timestamp": "2023-01-01T00:00:00Z"
   }
   ```

### CORS Configuration
Ensure your backend allows requests from your frontend domain:
- Add your frontend domain to CORS allowed origins
- Example for Express.js:
```javascript
app.use(cors({
  origin: ['https://your-frontend-domain.com', 'http://localhost:3000']
}));
```

## Security Considerations

### API Key Management
- Store API keys in environment variables, never in code
- Use different API keys for different environments
- Rotate API keys regularly
- Implement rate limiting on the backend

### Input Validation
- The frontend sanitizes user inputs before sending to backend
- Backend should also validate and sanitize all inputs
- Implement content filtering for security

### HTTPS Requirements
- Always use HTTPS in production environments
- The chatbot will work over HTTPS connections
- Mixed content (HTTP/HTTPS) should be avoided

### Content Security Policy
Consider adding the following to your CSP header:
```
connect-src 'self' https://your-backend-domain.com;
```

## Monitoring and Logging

### Frontend Monitoring
The chatbot includes built-in monitoring features:

1. **Connection Status**: Real-time connection status indicator
2. **Error Tracking**: Comprehensive error handling and reporting
3. **Performance Metrics**: Loading times and response times

### Backend Monitoring Requirements
Your backend should provide:
- Health check endpoints
- Response time metrics
- Error rate tracking
- Usage analytics (optional)

### Logging Best Practices
```javascript
// Example of error logging in production
if (process.env.NODE_ENV === 'production') {
  console.error('Chatbot error:', error);
  // Send to error tracking service (e.g., Sentry, LogRocket)
}
```

## Performance Optimization

### Caching Strategies
- Implement backend response caching for common queries
- Consider client-side caching for frequently accessed content
- Use CDN for static assets

### Bundle Optimization
- The chatbot is designed to be lightweight
- Lazy load the chatbot component when needed
- Optimize images and assets

### Loading Performance
- The chatbot loads asynchronously
- Connection monitoring starts after initial load
- Input remains responsive during API calls

### Resource Management
- Connection monitoring interval: 30 seconds (configurable)
- Automatic cleanup of intervals and listeners
- Session persistence using localStorage

## Troubleshooting Deployment Issues

### Common Deployment Problems

**Issue**: Chatbot not loading on deployed site
**Solution**:
1. Verify `CHATBOT_API_ENDPOINT` is correctly set
2. Check browser console for CORS errors
3. Ensure backend is accessible from the deployed domain

**Issue**: API requests failing in production
**Solution**:
1. Check if HTTPS is being used consistently
2. Verify CORS headers are properly configured
3. Confirm API endpoint is accessible

**Issue**: Slow response times
**Solution**:
1. Check network connectivity to backend
2. Verify backend performance
3. Consider implementing caching strategies

### Environment-Specific Configurations

#### Netlify
Add environment variables in the Netlify dashboard:
- `CHATBOT_API_ENDPOINT`: Your backend URL
- `CHATBOT_TIMEOUT_MS`: Request timeout

#### Vercel
Add environment variables in Vercel project settings:
- `CHATBOT_API_ENDPOINT`: Your backend URL
- `CHATBOT_TIMEOUT_MS`: Request timeout

#### GitHub Pages
For GitHub Pages, you may need to use a different approach:
1. Create environment-specific build scripts
2. Use GitHub Actions to set environment variables during build

## Testing in Different Environments

### Local Testing
```bash
# Test with development backend
npm run start

# Test with staging backend
CHATBOT_API_ENDPOINT=https://staging-api.yourdomain.com npm run start
```

### Production Testing
- Test with actual production backend
- Verify all environment variables are correctly set
- Check cross-origin requests and responses
- Validate security headers

## Rollback Procedures

If deployment issues occur:

1. Keep a backup of the previous working configuration
2. Maintain access to previous environment variables
3. Have a quick rollback plan for the chatbot component
4. Monitor error rates after deployment

## Version Compatibility

- Frontend chatbot component version should be compatible with backend API
- Maintain backward compatibility for API responses
- Plan for version-specific features and deprecations