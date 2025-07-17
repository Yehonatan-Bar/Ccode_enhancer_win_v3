# ILands.io Logging System Documentation

## Overview

The ILands.io platform implements a comprehensive, structured logging system designed for production environments. The system provides centralized logging with configurable filtering, multiple storage backends, and built-in security features.

## Architecture

### Core Components

#### 1. Logger Class (`shared/logging/logger.ts`)
The main logging implementation that handles:
- Log level filtering
- Feature and module tag filtering
- Context tracking (userId, sessionId, requestId)
- Automatic parameter sanitization
- Multiple storage backend support
- Configurable output formatting

#### 2. Logging Configuration (`shared/logging/logging-config.ts`)
Provides dynamic configuration capabilities:
- Global enable/disable toggle
- Log level threshold setting
- Feature-specific filtering
- Module-specific filtering
- Configuration loading from JSON file

#### 3. Storage Backends
- **MemoryLogStorage** (`storage/memory-storage.ts`): In-memory storage with size limits
- **FileLogStorage** (`storage/file-storage.ts`): File-based storage with rotation support
- **ArchivedFileLogStorage** (`storage/archived-file-storage.ts`): Enhanced file storage with archive directory support

#### 4. Formatters
- **JsonFormatter**: Outputs logs in JSON format for parsing
- **PrettyFormatter**: Human-readable format for console output

## Configuration

### Configuration File (`logging.json`)
Place a `logging.json` file in the project root to customize logging behavior:

```json
{
  "enabled": true,
  "logLevel": "INFO",
  "features": {
    "AUTH": true,
    "PROJECT_MANAGEMENT": true,
    "MAP_INTEGRATION": true,
    "ISLANDS": true,
    "COMBAT": false,
    "DEBUG": false
    // ... other features
  },
  "modules": {
    "COMPONENTS": true,
    "SERVICES": true,
    "CONTROLLERS": true,
    "TESTS": false
    // ... other modules
  }
}
```

### Disabling All Logging
To completely disable logging:

1. Set `"enabled": false` in `logging.json`:
```json
{
  "enabled": false,
  "logLevel": "INFO",
  "features": { ... },
  "modules": { ... }
}
```

2. The logging system enforces strict filtering:
   - If `enabled` is `false`, no logs will be written
   - If a feature/module tag is not explicitly set to `true` in the config, logs with that tag will be denied
   - Unknown tags are denied by default for security

### Important Notes on Configuration Loading
- The logging configuration is loaded asynchronously from `logging.json`
- On initial server startup, the default configuration is used until `logging.json` is loaded
- The default configuration has `enabled: false` to prevent unwanted logging
- Changes to `logging.json` require a server restart to take effect

### Log Levels
Available log levels in order of severity:
1. `DEBUG` - Detailed debugging information
2. `INFO` - General informational messages
3. `WARN` - Warning messages
4. `ERROR` - Error messages
5. `FATAL` - Fatal errors requiring immediate attention

### Feature Tags
Core features that can be filtered:
- `AUTH` - Authentication and authorization
- `PROJECT_MANAGEMENT` - Project-related operations
- `MAP_INTEGRATION` - Map and geospatial features
- `ISLANDS` - Island management
- `PORTALS` - Portal functionality
- `RESOURCES` - Resource management
- `COMBAT` - Combat system
- `INVENTORY` - Inventory management
- `TRADING` - Trading system
- `CHAT` - Chat functionality
- `GUILDS` - Guild management
- `ACHIEVEMENTS` - Achievement system
- `ANALYTICS` - Analytics tracking
- `ADMIN` - Administrative functions
- `GAME_STATE` - Game state management
- `PERFORMANCE` - Performance monitoring
- `NETWORK` - Network operations
- `DATABASE` - Database operations
- `API` - API endpoints
- `WEBSOCKET` - WebSocket connections
- `SECURITY` - Security-related operations
- `ERROR_HANDLING` - Error handling
- And many more...

### Module Tags
Module types that can be filtered:
- `COMPONENTS` - UI components
- `HOOKS` - React hooks
- `SERVICES` - Service layer
- `CONTROLLERS` - API controllers
- `MIDDLEWARE` - Express middleware
- `UTILS` - Utility functions
- `VALIDATORS` - Input validators
- `REPOSITORIES` - Data repositories
- `HANDLERS` - Event handlers
- `MODELS` - Data models
- And many more...

## Usage

### Basic Usage

```typescript
import { logger } from '@/shared/logging';
import { FEATURE_TAGS, MODULE_TAGS } from '@/shared/logging/constants';

// Info log
logger.info(
  FEATURE_TAGS.AUTH,
  MODULE_TAGS.SERVICES,
  'authenticateUser',
  'User authenticated successfully',
  { username: 'john.doe', userId: '12345' }
);

// Error log
logger.error(
  FEATURE_TAGS.DATABASE,
  MODULE_TAGS.REPOSITORIES,
  'fetchUserData',
  'Failed to fetch user data',
  error,
  { userId: '12345' }
);

// Debug log
logger.debug(
  FEATURE_TAGS.PERFORMANCE,
  MODULE_TAGS.UTILS,
  'calculateMetrics',
  'Performance metrics calculated',
  { executionTime: 150, memoryUsage: '45MB' }
);
```

### Setting Context

```typescript
// Set request-specific context
logger.setContext({
  userId: '12345',
  sessionId: 'abc123',
  requestId: 'req-xyz'
});

// All subsequent logs will include this context
logger.info(FEATURE_TAGS.API, MODULE_TAGS.CONTROLLERS, 'handleRequest', 'Processing request');

// Clear context when done
logger.clearContext();
```

### Security Features

The logger automatically sanitizes sensitive parameters:
```typescript
// This will log with password redacted
logger.info(
  FEATURE_TAGS.AUTH,
  MODULE_TAGS.SERVICES,
  'login',
  'Login attempt',
  { 
    username: 'john.doe',
    password: 'secret123', // Will be logged as '[REDACTED]'
    apiKey: 'key-abc123'   // Will be logged as '[REDACTED]'
  }
);
```

## HTTP Request Logging

### Middleware Integration (`server/middleware/logging-middleware.ts`)
Automatically logs all HTTP requests and responses:
- Request method, URL, headers
- Response status code and time
- User context (if authenticated)
- Request ID for tracing

## Log Management

### REST API Endpoints (`server/routes/logs.ts`)

#### Query Logs
```http
GET /api/logs?level=ERROR&feature=AUTH&userId=12345&limit=100&offset=0
```

#### Get Archive Directories
```http
GET /api/logs/archives
```
Returns a list of archived log directories from previous server sessions.

#### Get Statistics
```http
GET /api/logs/statistics
```

#### Export Logs
```http
GET /api/logs/export?format=json&startDate=2024-01-01&endDate=2024-01-31
```

#### Clear Logs (Admin Only)
```http
DELETE /api/logs
```
Note: This only clears the current session logs. Archived logs are preserved.

### Log Viewer UI (`client/src/components/admin/LogViewer.tsx`)
Admin interface features:
- Real-time log viewing
- Advanced filtering options
- Search functionality
- Statistics dashboard
- Export capabilities
- Log level distribution charts

## Log Analysis

### LogAnalyzer Class (`shared/logging/log-analyzer.ts`)
Provides programmatic log analysis:

```typescript
const analyzer = new LogAnalyzer(logStorage);

// Get statistics
const stats = await analyzer.getStatistics({
  startDate: new Date('2024-01-01'),
  endDate: new Date('2024-01-31')
});

// Find errors
const errors = await analyzer.findErrors();

// Get user activity
const activity = await analyzer.getUserActivity('userId123');

// Group logs by feature
const byFeature = await analyzer.groupByFeature();
```

## Storage Configuration

### Memory Storage
```typescript
const memoryStorage = new MemoryLogStorage({
  maxEntries: 10000  // Keep last 10,000 entries
});
logger.addStorage(memoryStorage);
```

### File Storage
```typescript
const fileStorage = new FileLogStorage({
  directory: './logs',
  maxFileSize: 10 * 1024 * 1024,  // 10MB per file
  maxFiles: 5,  // Keep 5 log files
  filename: 'app.log'
});
logger.addStorage(fileStorage);
```

### Archived File Storage
The system now supports automatic log organization into timestamped directories:

```typescript
const archivedStorage = new ArchivedFileLogStorage(
  './logs',           // Base logs directory
  'app.log',          // Log filename
  10 * 1024 * 1024,   // 10MB per file
  5                   // Keep 5 rotated files
);
logger.addStorage(archivedStorage);
```

### Log Directory Organization
On server startup, existing log files are automatically moved to timestamped subdirectories:

- Format: `logs/yyyy-MM-dd_HH-mm-ss/`
- Example: `logs/2025-07-14_10-22-05/app.log`
- Previous sessions remain accessible through the API
- The log viewer automatically searches archived directories

This ensures:
- Clean separation between server sessions
- Easy identification of logs by timestamp
- Preservation of historical logs
- Continued access through the HTTP interface

## Best Practices

### 1. Use Structured Logging
Always use the structured logging format with appropriate tags:
```typescript
// Good
logger.info(FEATURE_TAGS.AUTH, MODULE_TAGS.SERVICES, 'login', 'User logged in', { userId });

// Avoid
console.log('User logged in:', userId);
```

### 2. Choose Appropriate Log Levels
- **DEBUG**: Development and debugging information
- **INFO**: Normal application flow
- **WARN**: Recoverable issues or deprecated usage
- **ERROR**: Errors that need attention
- **FATAL**: Critical errors requiring immediate action

### 3. Include Relevant Context
Always include relevant parameters that help with debugging:
```typescript
logger.error(
  FEATURE_TAGS.PAYMENT,
  MODULE_TAGS.SERVICES,
  'processPayment',
  'Payment processing failed',
  error,
  { 
    orderId,
    amount,
    currency,
    paymentMethod,
    attemptNumber
  }
);
```

### 4. Configure for Environment
- **Development**: Enable DEBUG level and all features
- **Staging**: Enable INFO level with most features
- **Production**: Enable WARN level with critical features only

### 5. Monitor Performance Impact
Disable verbose logging in production to minimize performance impact:
```json
{
  "enabled": true,
  "logLevel": "WARN",
  "features": {
    "DEBUG": false,
    "PERFORMANCE": false,
    "TESTING": false
  }
}
```

## Troubleshooting

### Logs Not Appearing
1. Check if logging is enabled in `logging.json`
2. Verify the log level threshold
3. Ensure feature/module tags are enabled
4. Check storage backend configuration

### Performance Issues
1. Reduce log level to WARN or ERROR
2. Disable verbose features (DEBUG, PERFORMANCE)
3. Use file storage instead of memory storage
4. Implement log rotation

### Missing Context
1. Ensure `setContext()` is called at request start
2. Verify middleware is properly configured
3. Check that context is not cleared prematurely

## Migration from console.log

The codebase currently has 99 files using direct `console.log`. To migrate:

1. Import logger and constants:
```typescript
import { logger } from '@/shared/logging';
import { FEATURE_TAGS, MODULE_TAGS } from '@/shared/logging/constants';
```

2. Replace console.log with appropriate logger method:
```typescript
// Before
console.log('Processing user data:', userData);

// After
logger.info(
  FEATURE_TAGS.USER_MANAGEMENT,
  MODULE_TAGS.SERVICES,
  'processUserData',
  'Processing user data',
  { userData }
);
```

3. Remove console.error in favor of logger.error:
```typescript
// Before
console.error('Failed to save:', error);

// After
logger.error(
  FEATURE_TAGS.DATABASE,
  MODULE_TAGS.REPOSITORIES,
  'saveData',
  'Failed to save data',
  error
);
```

## Future Enhancements

1. **External Log Aggregation**: Integration with services like ELK Stack, Datadog, or Splunk
2. **Distributed Tracing**: OpenTelemetry integration for microservices
3. **Alert System**: Automated alerts for critical errors
4. **Log Sampling**: Reduce volume in production while maintaining visibility
5. **Structured Queries**: SQL-like query language for log analysis