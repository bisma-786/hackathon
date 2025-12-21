# API Contract: RAG Vector Retrieval and Validation

## Vector Retrieval Endpoints

### GET /vectors/by-url
Retrieve all vector chunks associated with a specific URL.

#### Request
```
GET /vectors/by-url?url={url}
```

#### Parameters
- `url` (string, required): The URL to retrieve vectors for
- `limit` (integer, optional): Maximum number of vectors to return (default: 100)
- `offset` (integer, optional): Offset for pagination (default: 0)

#### Response
```json
{
  "vectors": [
    {
      "id": "string",
      "embedding": [0.1, 0.2, 0.3, ...],
      "metadata": {
        "url": "string",
        "module": "string",
        "section": "string",
        "position": 0,
        "hash": "string",
        "source_text": "string"
      },
      "timestamps": {
        "ingestion": "2025-12-21T10:00:00Z",
        "retrieval": "2025-12-21T10:00:00Z"
      }
    }
  ],
  "count": 0,
  "query_time": 0.123
}
```

#### Success Response (200)
- All vectors for the specified URL retrieved successfully

#### Error Responses
- 400: Invalid URL parameter
- 404: No vectors found for the specified URL
- 500: Internal server error during retrieval

### GET /vectors/by-module
Retrieve all vector chunks associated with a specific module.

#### Request
```
GET /vectors/by-module?module={module}
```

#### Parameters
- `module` (string, required): The module name to retrieve vectors for
- `limit` (integer, optional): Maximum number of vectors to return (default: 100)
- `offset` (integer, optional): Offset for pagination (default: 0)

#### Response
```json
{
  "vectors": [
    {
      "id": "string",
      "embedding": [0.1, 0.2, 0.3, ...],
      "metadata": {
        "url": "string",
        "module": "string",
        "section": "string",
        "position": 0,
        "hash": "string",
        "source_text": "string"
      },
      "timestamps": {
        "ingestion": "2025-12-21T10:00:00Z",
        "retrieval": "2025-12-21T10:00:00Z"
      }
    }
  ],
  "count": 0,
  "query_time": 0.123
}
```

#### Success Response (200)
- All vectors for the specified module retrieved successfully

#### Error Responses
- 400: Invalid module parameter
- 404: No vectors found for the specified module
- 500: Internal server error during retrieval

### GET /vectors/by-section
Retrieve all vector chunks associated with a specific section.

#### Request
```
GET /vectors/by-section?section={section}
```

#### Parameters
- `section` (string, required): The section name to retrieve vectors for
- `limit` (integer, optional): Maximum number of vectors to return (default: 100)
- `offset` (integer, optional): Offset for pagination (default: 0)

#### Response
```json
{
  "vectors": [
    {
      "id": "string",
      "embedding": [0.1, 0.2, 0.3, ...],
      "metadata": {
        "url": "string",
        "module": "string",
        "section": "string",
        "position": 0,
        "hash": "string",
        "source_text": "string"
      },
      "timestamps": {
        "ingestion": "2025-12-21T10:00:00Z",
        "retrieval": "2025-12-21T10:00:00Z"
      }
    }
  ],
  "count": 0,
  "query_time": 0.123
}
```

#### Success Response (200)
- All vectors for the specified section retrieved successfully

#### Error Responses
- 400: Invalid section parameter
- 404: No vectors found for the specified section
- 500: Internal server error during retrieval

## Validation Endpoints

### POST /validate
Perform comprehensive validation of the retrieval pipeline.

#### Request
```
POST /validate
```

#### Body
```json
{
  "validation_type": "string",
  "parameters": {
    "url": "string",
    "module": "string",
    "threshold": 0.8
  }
}
```

#### Request Body Parameters
- `validation_type` (string): Type of validation to perform ("metadata_integrity", "similarity_check", "comprehensive")
- `parameters` (object, optional): Additional parameters for the validation

#### Response
```json
{
  "report": {
    "id": "string",
    "timestamp": "2025-12-21T10:00:00Z",
    "summary": {
      "total_vectors": 0,
      "successful_retrievals": 0,
      "failed_retrievals": 0,
      "success_rate": 0.0,
      "validation_type": "string"
    },
    "details": [
      {
        "vector_id": "string",
        "status": "string",
        "validation_steps": [
          {
            "step": "string",
            "status": "string",
            "details": "string"
          }
        ]
      }
    ],
    "errors": [
      {
        "vector_id": "string",
        "error_type": "string",
        "error_message": "string",
        "context": {}
      }
    ],
    "metrics": {
      "execution_time": 0.0,
      "queries_per_second": 0.0,
      "similarity_threshold": 0.0,
      "average_similarity_score": 0.0
    }
  },
  "status": "string"
}
```

#### Success Response (200)
- Validation completed successfully

#### Error Responses
- 400: Invalid validation type or parameters
- 500: Internal server error during validation

### GET /validate/{report_id}
Retrieve a specific validation report by ID.

#### Request
```
GET /validate/{report_id}
```

#### Path Parameters
- `report_id` (string): The ID of the validation report to retrieve

#### Response
```json
{
  "report": {
    "id": "string",
    "timestamp": "2025-12-21T10:00:00Z",
    "summary": {
      "total_vectors": 0,
      "successful_retrievals": 0,
      "failed_retrievals": 0,
      "success_rate": 0.0,
      "validation_type": "string"
    },
    "details": [
      {
        "vector_id": "string",
        "status": "string",
        "validation_steps": [
          {
            "step": "string",
            "status": "string",
            "details": "string"
          }
        ]
      }
    ],
    "errors": [
      {
        "vector_id": "string",
        "error_type": "string",
        "error_message": "string",
        "context": {}
      }
    ],
    "metrics": {
      "execution_time": 0.0,
      "queries_per_second": 0.0,
      "similarity_threshold": 0.0,
      "average_similarity_score": 0.0
    }
  },
  "status": "string"
}
```

#### Success Response (200)
- Validation report retrieved successfully

#### Error Responses
- 404: Validation report not found
- 500: Internal server error during retrieval