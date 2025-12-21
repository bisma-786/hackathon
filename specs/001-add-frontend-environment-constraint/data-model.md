# Data Model: Frontend Environment Constraint

## Entity: EnvironmentConfig
**Description**: Represents the configuration for environment variable handling in the frontend

**Fields**:
- `apiEndpoint` (string): Base URL for the backend API, injected via Docusaurus
- `timeoutMs` (number): Request timeout in milliseconds, configured at build time
- `maxQueryLength` (number): Maximum length for user queries, configured via environment
- `showSources` (boolean): Whether to display source information, configured via environment
- `enableSelectedText` (boolean): Whether to enable text selection feature, configured via environment
- `injectionMethod` (enum: 'docusaurus_config'|'build_time'|'runtime_safe'): Method of environment variable injection

**Validation Rules**:
- `apiEndpoint` must be a valid URL string
- `timeoutMs` must be a positive integer between 1000 and 60000
- `maxQueryLength` must be a positive integer between 100 and 5000
- `showSources` and `enableSelectedText` must be booleans
- `injectionMethod` must be one of the allowed values

## Entity: EnvironmentInjectionRule
**Description**: Defines rules for how environment variables should be injected

**Fields**:
- `variableName` (string): Name of the environment variable to inject
- `injectionTarget` (enum: 'component_prop'|'global_context'|'config_object'): Where to inject the variable
- `fallbackValue` (any): Value to use if environment variable is not provided
- `isRequired` (boolean): Whether the variable is required for proper functioning
- `validationPattern` (string, optional): Regex pattern to validate the variable value
- `ssrSafe` (boolean): Whether the injection method is safe for server-side rendering

**Validation Rules**:
- `variableName` must be a non-empty string
- `injectionTarget` must be one of allowed values
- `isRequired` implies that fallbackValue is optional
- `validationPattern` must be a valid regex string if provided
- `ssrSafe` must be boolean

## Entity: NodeJsGlobalConstraint
**Description**: Defines constraints to prevent Node.js global usage in frontend code

**Fields**:
- `globalName` (string): Name of the Node.js global to restrict (e.g., 'process', 'fs', 'path')
- `errorMessage` (string): Error message to show when the global is used inappropriately
- `allowedContexts` (array of strings): Contexts where the global may be used (e.g., build scripts)
- `detectionMethod` (enum: 'eslint_rule'|'build_check'|'manual_review'): How to detect violations
- `severity` (enum: 'error'|'warning'|'off'): Severity level for violations

**Validation Rules**:
- `globalName` must be a non-empty string
- `errorMessage` must be a non-empty string
- `allowedContexts` items must be non-empty strings
- `detectionMethod` must be one of allowed values
- `severity` must be one of allowed values

## Entity: SSRCompatibilityCheck
**Description**: Represents checks for server-side rendering compatibility

**Fields**:
- `checkName` (string): Name of the compatibility check
- `description` (string): Description of what the check validates
- `testMethod` (enum: 'static_analysis'|'runtime_check'|'build_validation'): How the check is performed
- `failureAction` (enum: 'build_fail'|'warning'|'runtime_fallback'): What happens when check fails
- `affectedComponents` (array of strings): Components affected by this check

**Validation Rules**:
- `checkName` must be a non-empty string
- `description` must be a non-empty string
- `testMethod` must be one of allowed values
- `failureAction` must be one of allowed values
- `affectedComponents` items must be non-empty strings

## Entity: ValidationResult
**Description**: Represents the result of environment variable validation

**Fields**:
- `isValid` (boolean): Whether the validation passed
- `variableName` (string): Name of the validated environment variable
- `actualValue` (any): The actual value of the variable (masked if sensitive)
- `expectedType` (string): Expected type of the variable
- `validationErrors` (array of strings): Errors found during validation
- `timestamp` (string, ISO 8601): When the validation was performed

**Validation Rules**:
- `isValid` must be boolean
- `variableName` must be a non-empty string
- `expectedType` must be a valid JavaScript type name
- `validationErrors` items must be non-empty strings
- `timestamp` must be valid ISO 8601 date string