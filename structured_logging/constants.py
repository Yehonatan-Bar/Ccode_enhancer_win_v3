class FEATURE_TAGS:
    # Core System Features
    AUTH = "AUTH"
    PROJECT_MANAGEMENT = "PROJECT_MANAGEMENT"
    USER_MANAGEMENT = "USER_MANAGEMENT"
    SECURITY = "SECURITY"
    ERROR_HANDLING = "ERROR_HANDLING"
    
    # Browser Automation Features
    BROWSER_AUTOMATION = "BROWSER_AUTOMATION"
    ELEMENT_INTERACTION = "ELEMENT_INTERACTION"
    SCREENSHOT_CAPTURE = "SCREENSHOT_CAPTURE"
    NETWORK_MONITORING = "NETWORK_MONITORING"
    PAGE_ANALYSIS = "PAGE_ANALYSIS"
    
    # Vision Processing Features
    VISION_PROCESSING = "VISION_PROCESSING"
    IMAGE_COMPRESSION = "IMAGE_COMPRESSION"
    ELEMENT_DETECTION = "ELEMENT_DETECTION"
    
    # Utility Features
    FILE_OPERATIONS = "FILE_OPERATIONS"
    CONFIGURATION = "CONFIGURATION"
    MONITORING = "MONITORING"
    
    # Development Features
    DEBUG = "DEBUG"
    TESTING = "TESTING"
    PERFORMANCE = "PERFORMANCE"
    
    # System Features
    SYSTEM_INTEGRATION = "SYSTEM_INTEGRATION"
    HARDWARE_DETECTION = "HARDWARE_DETECTION"
    LOGGING = "LOGGING"


class MODULE_TAGS:
    # Core Module Types
    SERVICES = "SERVICES"
    CONTROLLERS = "CONTROLLERS"
    HANDLERS = "HANDLERS"
    UTILS = "UTILS"
    
    # Browser Module Types
    BROWSER_MANAGER = "BROWSER_MANAGER"
    ELEMENT_PROCESSORS = "ELEMENT_PROCESSORS"
    NETWORK_ANALYZERS = "NETWORK_ANALYZERS"
    VISION_PROCESSORS = "VISION_PROCESSORS"
    
    # System Module Types
    STORAGE = "STORAGE"
    FORMATTERS = "FORMATTERS"
    VALIDATORS = "VALIDATORS"
    ANALYZERS = "ANALYZERS"
    
    # Infrastructure Module Types
    MIDDLEWARE = "MIDDLEWARE"
    REPOSITORIES = "REPOSITORIES"
    MODELS = "MODELS"
    COMPONENTS = "COMPONENTS"
    
    # Development Module Types
    TESTS = "TESTS"
    TOOLS = "TOOLS"
    SCRIPTS = "SCRIPTS"
    CONFIGS = "CONFIGS"


# Predefined tag combinations for common use cases
COMMON_TAG_COMBINATIONS = {
    'browser_automation': (FEATURE_TAGS.BROWSER_AUTOMATION, MODULE_TAGS.BROWSER_MANAGER),
    'element_click': (FEATURE_TAGS.ELEMENT_INTERACTION, MODULE_TAGS.ELEMENT_PROCESSORS),
    'screenshot': (FEATURE_TAGS.SCREENSHOT_CAPTURE, MODULE_TAGS.VISION_PROCESSORS),
    'network_analysis': (FEATURE_TAGS.NETWORK_MONITORING, MODULE_TAGS.NETWORK_ANALYZERS),
    'file_ops': (FEATURE_TAGS.FILE_OPERATIONS, MODULE_TAGS.UTILS),
    'error_handling': (FEATURE_TAGS.ERROR_HANDLING, MODULE_TAGS.HANDLERS),
    'system_config': (FEATURE_TAGS.CONFIGURATION, MODULE_TAGS.CONFIGS),
    'debug_tools': (FEATURE_TAGS.DEBUG, MODULE_TAGS.TOOLS),
}

# Security-sensitive parameter names that should be redacted
SENSITIVE_PARAMETERS = {
    'password', 'pwd', 'pass', 'secret', 'token', 'key', 'auth', 'credential',
    'api_key', 'apikey', 'access_token', 'refresh_token', 'session_token',
    'private_key', 'public_key', 'cert', 'certificate', 'signature',
    'hash', 'salt', 'oauth', 'bearer', 'authorization'
}