# Quickstart Guide: Frontend Environment Constraint Implementation

## Overview
This guide provides instructions for implementing constraints that ensure frontend code doesn't reference Node.js globals and uses Docusaurus-supported environment injection mechanisms.

## Prerequisites
- Docusaurus 3.x project
- Node.js 18+
- ESLint configured in your project

## Implementation Steps

### 1. Configure ESLint Rules
Add ESLint rules to prevent Node.js global usage in frontend code:

```javascript
// .eslintrc.js
module.exports = {
  rules: {
    'no-process-env': 'error',
    'no-undef': ['error', { 'typeof': true }],
    'no-restricted-globals': [
      'error',
      'process', 'require', 'module', 'exports', '__dirname', '__filename'
    ]
  }
};
```

### 2. Update Docusaurus Configuration
Configure environment variables through docusaurus.config.js:

```javascript
// docusaurus.config.js
module.exports = {
  themeConfig: {
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
};
```

### 3. Use BrowserOnly for Runtime Access
For any environment variables that need to be accessed at runtime, use Docusaurus BrowserOnly:

```jsx
import BrowserOnly from '@docusaurus/BrowserOnly';

const MyComponent = () => {
  return (
    <BrowserOnly fallback={<div>Loading...</div>}>
      {() => {
        // Safe to access browser globals here
        const apiUrl = process.env.REACT_APP_API_URL;
        return <div>Using API: {apiUrl}</div>;
      }}
    </BrowserOnly>
  );
};
```

### 4. Create Environment Configuration Objects
Use configuration objects that can be populated with environment values:

```javascript
// src/config/environment.js
export const createEnvironmentConfig = (overrides = {}) => {
  return {
    apiEndpoint: process.env.CHATBOT_API_ENDPOINT || 'http://localhost:8000',
    timeoutMs: parseInt(process.env.CHATBOT_TIMEOUT_MS) || 30000,
    maxQueryLength: parseInt(process.env.CHATBOT_MAX_QUERY_LENGTH) || 1000,
    ...overrides
  };
};
```

### 5. Update Build Configuration
Ensure webpack configuration handles environment variables safely:

```javascript
// webpack.config.js
module.exports = {
  plugins: [
    new webpack.DefinePlugin({
      'process.env.CHATBOT_API_ENDPOINT': JSON.stringify(process.env.CHATBOT_API_ENDPOINT),
      'process.env.CHATBOT_TIMEOUT_MS': JSON.stringify(process.env.CHATBOT_TIMEOUT_MS)
    })
  ]
};
```

## Testing Environment Constraints

### 1. ESLint Validation
Run ESLint to check for Node.js global usage:

```bash
npm run lint
```

### 2. Build Validation
Verify the site builds without SSR errors:

```bash
npm run build
```

### 3. Runtime Validation
Test that environment variables are properly available:

```bash
npm run serve
```

## Best Practices

### 1. Environment Variable Injection
- Use docusaurus.config.js for configuration
- Use DefinePlugin for build-time constants
- Use BrowserOnly for runtime access

### 2. SSR Safety
- Never access Node.js globals directly in components
- Use typeof checks before accessing browser APIs
- Provide fallbacks for server-side rendering

### 3. Validation
- Implement static analysis checks
- Use TypeScript for compile-time validation
- Test both build and runtime behavior

## Troubleshooting

### Build Errors Related to Node.js Globals
- Check ESLint rules are properly configured
- Verify environment variables are injected through Docusaurus config
- Ensure no direct process.env access in components

### SSR Compatibility Issues
- Confirm BrowserOnly is used for browser-specific code
- Verify all required variables are available during build
- Check that no Node.js APIs are called during SSR

### Environment Variable Not Available
- Verify variable is properly defined in environment
- Check that Docusaurus config includes the variable
- Confirm variable name matches between config and code