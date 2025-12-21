/**
 * Data models for the RAG Chatbot component
 * Defines the structure and validation for chat-related entities
 */

/**
 * ChatMessage
 * Represents a single message in the chat conversation
 */
export class ChatMessage {
  /**
   * Create a ChatMessage instance
   * @param {Object} params - Message parameters
   * @param {string} params.id - Unique identifier for the message
   * @param {string} params.content - The text content of the message
   * @param {'user'|'assistant'} params.sender - Type of sender
   * @param {string} params.timestamp - ISO 8601 timestamp
   * @param {Array<string>} [params.sources] - Source references for assistant responses
   * @param {'pending'|'sent'|'error'} [params.status] - Message status for UI display
   */
  constructor({ id, content, sender, timestamp, sources, status }) {
    this.id = this._validateId(id);
    this.content = this._validateContent(content);
    this.sender = this._validateSender(sender);
    this.timestamp = this._validateTimestamp(timestamp);
    this.sources = sources ? this._validateSources(sources) : [];
    this.status = status || 'sent'; // Default status is 'sent' for new messages

    // Validate the complete object
    this._validate();
  }

  /**
   * Validate message ID
   * @param {string} id - Message ID
   * @returns {string} Validated ID
   */
  _validateId(id) {
    if (!id || typeof id !== 'string' || id.trim() === '') {
      throw new Error('Message ID must be a non-empty string');
    }
    return id.trim();
  }

  /**
   * Validate message content
   * @param {string} content - Message content
   * @returns {string} Validated content
   */
  _validateContent(content) {
    if (!content || typeof content !== 'string' || content.trim() === '') {
      throw new Error('Message content must be a non-empty string');
    }
    if (content.length > 5000) {
      throw new Error('Message content must be less than 5000 characters');
    }
    return content;
  }

  /**
   * Validate sender type
   * @param {string} sender - Sender type
   * @returns {'user'|'assistant'} Validated sender
   */
  _validateSender(sender) {
    const validSenders = ['user', 'assistant'];
    if (!validSenders.includes(sender)) {
      throw new Error(`Sender must be one of: ${validSenders.join(', ')}`);
    }
    return sender;
  }

  /**
   * Validate timestamp
   * @param {string} timestamp - Timestamp string
   * @returns {string} Validated timestamp
   */
  _validateTimestamp(timestamp) {
    if (!timestamp || typeof timestamp !== 'string') {
      throw new Error('Timestamp must be a valid string');
    }
    // Try to parse the timestamp to ensure it's valid
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      throw new Error('Timestamp must be a valid ISO 8601 datetime string');
    }
    return timestamp;
  }

  /**
   * Validate sources array
   * @param {Array<string>} sources - Sources array
   * @returns {Array<string>} Validated sources
   */
  _validateSources(sources) {
    if (!Array.isArray(sources)) {
      throw new Error('Sources must be an array');
    }
    return sources.map(source => {
      if (typeof source !== 'string' || source.trim() === '') {
        throw new Error('Each source must be a non-empty string');
      }
      return source.trim();
    });
  }

  /**
   * Validate the complete message object
   */
  _validate() {
    // Additional validation logic can be added here
  }

  /**
   * Convert to plain object for serialization
   * @returns {Object} Plain object representation
   */
  toObject() {
    return {
      id: this.id,
      content: this.content,
      sender: this.sender,
      timestamp: this.timestamp,
      sources: this.sources,
      status: this.status
    };
  }

  /**
   * Create ChatMessage from plain object
   * @param {Object} obj - Plain object to convert
   * @returns {ChatMessage} New ChatMessage instance
   */
  static fromObject(obj) {
    return new ChatMessage({
      id: obj.id,
      content: obj.content,
      sender: obj.sender,
      timestamp: obj.timestamp,
      sources: obj.sources,
      status: obj.status
    });
  }
}

/**
 * ChatSession
 * Represents a single chat session on a book page
 */
export class ChatSession {
  /**
   * Create a ChatSession instance
   * @param {Object} params - Session parameters
   * @param {string} params.id - Unique identifier for the session
   * @param {string} params.pageUrl - URL of the book page where the chat is active
   * @param {string} [params.selectedText] - Text that was selected when the query was initiated
   * @param {Array<ChatMessage>} [params.messages] - Array of messages in the conversation
   * @param {string} params.createdAt - ISO 8601 datetime when the session was created
   * @param {string} params.updatedAt - ISO 8601 datetime when the session was last updated
   */
  constructor({ id, pageUrl, selectedText, messages = [], createdAt, updatedAt }) {
    this.id = this._validateId(id);
    this.pageUrl = this._validatePageUrl(pageUrl);
    this.selectedText = selectedText ? this._validateSelectedText(selectedText) : '';
    this.messages = this._validateMessages(messages);
    this.createdAt = this._validateTimestamp(createdAt);
    this.updatedAt = this._validateTimestamp(updatedAt);

    this._validate();
  }

  /**
   * Validate session ID
   * @param {string} id - Session ID
   * @returns {string} Validated ID
   */
  _validateId(id) {
    if (!id || typeof id !== 'string' || id.trim() === '') {
      throw new Error('Session ID must be a non-empty string');
    }
    return id.trim();
  }

  /**
   * Validate page URL
   * @param {string} pageUrl - Page URL
   * @returns {string} Validated URL
   */
  _validatePageUrl(pageUrl) {
    if (!pageUrl || typeof pageUrl !== 'string') {
      throw new Error('Page URL must be a valid string');
    }

    try {
      new URL(pageUrl);
      return pageUrl;
    } catch (e) {
      throw new Error('Page URL must be a valid URL format');
    }
  }

  /**
   * Validate selected text
   * @param {string} selectedText - Selected text
   * @returns {string} Validated selected text
   */
  _validateSelectedText(selectedText) {
    if (typeof selectedText !== 'string') {
      throw new Error('Selected text must be a string');
    }
    if (selectedText.length > 1000) {
      throw new Error('Selected text must be less than 1000 characters');
    }
    return selectedText;
  }

  /**
   * Validate messages array
   * @param {Array<ChatMessage>} messages - Messages array
   * @returns {Array<ChatMessage>} Validated messages
   */
  _validateMessages(messages) {
    if (!Array.isArray(messages)) {
      throw new Error('Messages must be an array');
    }

    if (messages.length > 50) {
      throw new Error('Session must not exceed 50 messages');
    }

    return messages.map(msg => {
      if (!(msg instanceof ChatMessage)) {
        // If it's a plain object, convert it to ChatMessage
        if (typeof msg === 'object' && msg.id && msg.content && msg.sender) {
          return ChatMessage.fromObject(msg);
        }
        throw new Error('Each message must be a ChatMessage instance or valid object');
      }
      return msg;
    });
  }

  /**
   * Validate timestamp
   * @param {string} timestamp - Timestamp string
   * @returns {string} Validated timestamp
   */
  _validateTimestamp(timestamp) {
    if (!timestamp || typeof timestamp !== 'string') {
      throw new Error('Timestamp must be a valid string');
    }
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      throw new Error('Timestamp must be a valid ISO 8601 datetime string');
    }
    return timestamp;
  }

  /**
   * Validate the complete session object
   */
  _validate() {
    // Additional validation logic can be added here
  }

  /**
   * Add a message to the session
   * @param {ChatMessage} message - Message to add
   */
  addMessage(message) {
    if (!(message instanceof ChatMessage)) {
      throw new Error('Message must be a ChatMessage instance');
    }

    if (this.messages.length >= 50) {
      throw new Error('Session cannot exceed 50 messages');
    }

    this.messages.push(message);
    this.updatedAt = new Date().toISOString();
  }

  /**
   * Get the last message in the session
   * @returns {ChatMessage|null} Last message or null if no messages
   */
  getLastMessage() {
    if (this.messages.length === 0) {
      return null;
    }
    return this.messages[this.messages.length - 1];
  }

  /**
   * Convert to plain object for serialization
   * @returns {Object} Plain object representation
   */
  toObject() {
    return {
      id: this.id,
      pageUrl: this.pageUrl,
      selectedText: this.selectedText,
      messages: this.messages.map(msg => msg.toObject()),
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }

  /**
   * Create ChatSession from plain object
   * @param {Object} obj - Plain object to convert
   * @returns {ChatSession} New ChatSession instance
   */
  static fromObject(obj) {
    return new ChatSession({
      id: obj.id,
      pageUrl: obj.pageUrl,
      selectedText: obj.selectedText,
      messages: (obj.messages || []).map(ChatMessage.fromObject),
      createdAt: obj.createdAt,
      updatedAt: obj.updatedAt
    });
  }
}

/**
 * APIRequest
 * Represents a request sent from the frontend to the backend API
 */
export class APIRequest {
  /**
   * Create an APIRequest instance
   * @param {Object} params - Request parameters
   * @param {string} params.query - The user's question/query text
   * @param {string} [params.selectedText] - The text that was selected on the page
   * @param {Object} [params.pageContext] - Additional context about the current page
   * @param {string} params.timestamp - When the request was made
   */
  constructor({ query, selectedText, pageContext, timestamp }) {
    this.query = this._validateQuery(query);
    this.selectedText = selectedText ? this._validateSelectedText(selectedText) : '';
    this.pageContext = pageContext || {};
    this.timestamp = this._validateTimestamp(timestamp);

    this._validate();
  }

  /**
   * Validate query text
   * @param {string} query - Query text
   * @returns {string} Validated query
   */
  _validateQuery(query) {
    if (!query || typeof query !== 'string' || query.trim() === '') {
      throw new Error('Query must be a non-empty string');
    }
    if (query.length > 1000) {
      throw new Error('Query must be less than 1000 characters');
    }
    return query;
  }

  /**
   * Validate selected text
   * @param {string} selectedText - Selected text
   * @returns {string} Validated selected text
   */
  _validateSelectedText(selectedText) {
    if (typeof selectedText !== 'string') {
      throw new Error('Selected text must be a string');
    }
    if (selectedText.length > 1000) {
      throw new Error('Selected text must be less than 1000 characters');
    }
    return selectedText;
  }

  /**
   * Validate page context
   * @param {Object} pageContext - Page context object
   * @returns {Object} Validated page context
   */
  _validatePageContext(pageContext) {
    if (pageContext && typeof pageContext !== 'object') {
      throw new Error('Page context must be an object');
    }
    return pageContext || {};
  }

  /**
   * Validate timestamp
   * @param {string} timestamp - Timestamp string
   * @returns {string} Validated timestamp
   */
  _validateTimestamp(timestamp) {
    if (!timestamp || typeof timestamp !== 'string') {
      throw new Error('Timestamp must be a valid string');
    }
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      throw new Error('Timestamp must be a valid ISO 8601 datetime string');
    }
    return timestamp;
  }

  /**
   * Validate the complete request object
   */
  _validate() {
    // Additional validation logic can be added here
  }

  /**
   * Convert to plain object for serialization
   * @returns {Object} Plain object representation
   */
  toObject() {
    return {
      query: this.query,
      selectedText: this.selectedText,
      pageContext: this.pageContext,
      timestamp: this.timestamp
    };
  }

  /**
   * Create APIRequest from plain object
   * @param {Object} obj - Plain object to convert
   * @returns {APIRequest} New APIRequest instance
   */
  static fromObject(obj) {
    return new APIRequest({
      query: obj.query,
      selectedText: obj.selectedText,
      pageContext: obj.pageContext,
      timestamp: obj.timestamp
    });
  }
}

/**
 * APIResponse
 * Represents a response received from the backend API
 */
export class APIResponse {
  /**
   * Create an APIResponse instance
   * @param {Object} params - Response parameters
   * @param {string} params.answer - The answer to the user's query
   * @param {Array<string>} [params.sources] - Source references for the answer
   * @param {number} [params.confidence] - Confidence score for the answer (0.0 to 1.0)
   * @param {Array<Object>} [params.retrievedContext] - Context used to generate the answer
   * @param {Array<string>} [params.followupQuestions] - Suggested follow-up questions
   * @param {string} params.timestamp - When the response was generated
   */
  constructor({ answer, sources, confidence, retrievedContext, followupQuestions, timestamp }) {
    this.answer = this._validateAnswer(answer);
    this.sources = sources || [];
    this.confidence = confidence !== undefined ? this._validateConfidence(confidence) : 0.5;
    this.retrievedContext = retrievedContext || [];
    this.followupQuestions = followupQuestions || [];
    this.timestamp = this._validateTimestamp(timestamp);

    this._validate();
  }

  /**
   * Validate answer
   * @param {string} answer - Answer text
   * @returns {string} Validated answer
   */
  _validateAnswer(answer) {
    if (!answer || typeof answer !== 'string' || answer.trim() === '') {
      throw new Error('Answer must be a non-empty string');
    }
    return answer;
  }

  /**
   * Validate confidence score
   * @param {number} confidence - Confidence score
   * @returns {number} Validated confidence score
   */
  _validateConfidence(confidence) {
    if (typeof confidence !== 'number' || confidence < 0.0 || confidence > 1.0) {
      throw new Error('Confidence must be a number between 0.0 and 1.0');
    }
    return confidence;
  }

  /**
   * Validate sources array
   * @param {Array<string>} sources - Sources array
   * @returns {Array<string>} Validated sources
   */
  _validateSources(sources) {
    if (!Array.isArray(sources)) {
      throw new Error('Sources must be an array');
    }
    return sources.map(source => {
      if (typeof source !== 'string' || source.trim() === '') {
        throw new Error('Each source must be a non-empty string');
      }
      return source.trim();
    });
  }

  /**
   * Validate retrieved context
   * @param {Array<Object>} retrievedContext - Retrieved context array
   * @returns {Array<Object>} Validated retrieved context
   */
  _validateRetrievedContext(retrievedContext) {
    if (!Array.isArray(retrievedContext)) {
      throw new Error('Retrieved context must be an array');
    }

    return retrievedContext.map(ctx => {
      if (typeof ctx !== 'object' || !ctx.content || typeof ctx.content !== 'string') {
        throw new Error('Each retrieved context item must be an object with a content property');
      }
      return ctx;
    });
  }

  /**
   * Validate follow-up questions
   * @param {Array<string>} followupQuestions - Follow-up questions array
   * @returns {Array<string>} Validated follow-up questions
   */
  _validateFollowupQuestions(followupQuestions) {
    if (!Array.isArray(followupQuestions)) {
      throw new Error('Follow-up questions must be an array');
    }
    return followupQuestions.map(q => {
      if (typeof q !== 'string' || q.trim() === '') {
        throw new Error('Each follow-up question must be a non-empty string');
      }
      return q.trim();
    });
  }

  /**
   * Validate timestamp
   * @param {string} timestamp - Timestamp string
   * @returns {string} Validated timestamp
   */
  _validateTimestamp(timestamp) {
    if (!timestamp || typeof timestamp !== 'string') {
      throw new Error('Timestamp must be a valid string');
    }
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      throw new Error('Timestamp must be a valid ISO 8601 datetime string');
    }
    return timestamp;
  }

  /**
   * Validate the complete response object
   */
  _validate() {
    // Additional validation logic can be added here
  }

  /**
   * Convert to plain object for serialization
   * @returns {Object} Plain object representation
   */
  toObject() {
    return {
      answer: this.answer,
      sources: this.sources,
      confidence: this.confidence,
      retrievedContext: this.retrievedContext,
      followupQuestions: this.followupQuestions,
      timestamp: this.timestamp
    };
  }

  /**
   * Create APIResponse from plain object
   * @param {Object} obj - Plain object to convert
   * @returns {APIResponse} New APIResponse instance
   */
  static fromObject(obj) {
    return new APIResponse({
      answer: obj.answer,
      sources: obj.sources,
      confidence: obj.confidence,
      retrievedContext: obj.retrievedContext,
      followupQuestions: obj.followupQuestions,
      timestamp: obj.timestamp
    });
  }
}

/**
 * ChatbotConfig
 * Configuration settings for the chatbot component
 */
export class ChatbotConfig {
  /**
   * Create a ChatbotConfig instance
   * @param {Object} params - Configuration parameters
   * @param {string} params.apiEndpoint - Base URL for the backend API
   * @param {number} [params.maxQueryLength] - Maximum allowed query length (default: 1000)
   * @param {number} [params.maxHistorySize] - Maximum number of messages to keep in session (default: 50)
   * @param {number} [params.timeoutMs] - Request timeout in milliseconds (default: 30000)
   * @param {boolean} [params.showSources] - Whether to display source information (default: true)
   * @param {boolean} [params.enableSelectedText] - Whether to capture and send selected text (default: true)
   */
  constructor({
    apiEndpoint,
    maxQueryLength = 1000,
    maxHistorySize = 50,
    timeoutMs = 30000,
    showSources = true,
    enableSelectedText = true
  }) {
    this.apiEndpoint = this._validateApiEndpoint(apiEndpoint);
    this.maxQueryLength = this._validateMaxQueryLength(maxQueryLength);
    this.maxHistorySize = this._validateMaxHistorySize(maxHistorySize);
    this.timeoutMs = this._validateTimeoutMs(timeoutMs);
    this.showSources = this._validateShowSources(showSources);
    this.enableSelectedText = this._validateEnableSelectedText(enableSelectedText);

    this._validate();
  }

  /**
   * Validate API endpoint
   * @param {string} apiEndpoint - API endpoint URL
   * @returns {string} Validated API endpoint
   */
  _validateApiEndpoint(apiEndpoint) {
    if (!apiEndpoint || typeof apiEndpoint !== 'string') {
      throw new Error('API endpoint must be a valid string');
    }

    try {
      new URL(apiEndpoint);
      return apiEndpoint;
    } catch (e) {
      throw new Error('API endpoint must be a valid URL');
    }
  }

  /**
   * Validate maximum query length
   * @param {number} maxQueryLength - Maximum query length
   * @returns {number} Validated maximum query length
   */
  _validateMaxQueryLength(maxQueryLength) {
    if (typeof maxQueryLength !== 'number' || maxQueryLength <= 0) {
      throw new Error('Max query length must be a positive number');
    }
    return Math.floor(maxQueryLength); // Ensure it's an integer
  }

  /**
   * Validate maximum history size
   * @param {number} maxHistorySize - Maximum history size
   * @returns {number} Validated maximum history size
   */
  _validateMaxHistorySize(maxHistorySize) {
    if (typeof maxHistorySize !== 'number' || maxHistorySize <= 0) {
      throw new Error('Max history size must be a positive number');
    }
    return Math.floor(maxHistorySize); // Ensure it's an integer
  }

  /**
   * Validate timeout in milliseconds
   * @param {number} timeoutMs - Timeout in milliseconds
   * @returns {number} Validated timeout
   */
  _validateTimeoutMs(timeoutMs) {
    if (typeof timeoutMs !== 'number' || timeoutMs < 1000 || timeoutMs > 30000) {
      throw new Error('Timeout must be between 1000 and 30000 milliseconds');
    }
    return Math.floor(timeoutMs); // Ensure it's an integer
  }

  /**
   * Validate show sources flag
   * @param {boolean} showSources - Show sources flag
   * @returns {boolean} Validated flag
   */
  _validateShowSources(showSources) {
    if (typeof showSources !== 'boolean') {
      throw new Error('Show sources must be a boolean value');
    }
    return showSources;
  }

  /**
   * Validate enable selected text flag
   * @param {boolean} enableSelectedText - Enable selected text flag
   * @returns {boolean} Validated flag
   */
  _validateEnableSelectedText(enableSelectedText) {
    if (typeof enableSelectedText !== 'boolean') {
      throw new Error('Enable selected text must be a boolean value');
    }
    return enableSelectedText;
  }

  /**
   * Validate the complete config object
   */
  _validate() {
    // Additional validation logic can be added here
  }

  /**
   * Convert to plain object for serialization
   * @returns {Object} Plain object representation
   */
  toObject() {
    return {
      apiEndpoint: this.apiEndpoint,
      maxQueryLength: this.maxQueryLength,
      maxHistorySize: this.maxHistorySize,
      timeoutMs: this.timeoutMs,
      showSources: this.showSources,
      enableSelectedText: this.enableSelectedText
    };
  }

  /**
   * Create ChatbotConfig from plain object
   * @param {Object} obj - Plain object to convert
   * @returns {ChatbotConfig} New ChatbotConfig instance
   */
  static fromObject(obj) {
    return new ChatbotConfig({
      apiEndpoint: obj.apiEndpoint,
      maxQueryLength: obj.maxQueryLength,
      maxHistorySize: obj.maxHistorySize,
      timeoutMs: obj.timeoutMs,
      showSources: obj.showSources,
      enableSelectedText: obj.enableSelectedText
    });
  }
}