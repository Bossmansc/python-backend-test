from typing import Any, Dict, List, Optional, Union
import re
from urllib.parse import urlparse
from datetime import datetime


class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_github_url(url: str) -> tuple[bool, str]:
        """Validate GitHub repository URL"""
        if not url:
            return False, "URL is required"
        
        # Parse URL
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False, "URL must start with http:// or https://"
        
        # Check domain
        if parsed.netloc not in ['github.com', 'www.github.com']:
            return False, "URL must be a GitHub repository (github.com)"
        
        # Check path format (should be /username/repository)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            return False, "GitHub URL must be in format: https://github.com/username/repository"
        
        # Check repository name format
        repo_name = path_parts[1]
        if not re.match(r'^[a-zA-Z0-9_.-]+$', repo_name):
            return False, "Repository name contains invalid characters"
        
        return True, "Valid GitHub URL"
    
    @staticmethod
    def validate_project_name(name: str) -> tuple[bool, str]:
        """Validate project name"""
        if not name:
            return False, "Project name is required"
        
        if len(name) < 3:
            return False, "Project name must be at least 3 characters"
        
        if len(name) > 100:
            return False, "Project name must be less than 100 characters"
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\s\-_\.]*$', name):
            return False, "Project name can only contain letters, numbers, spaces, hyphens, underscores, and dots"
        
        return True, "Valid project name"
    
    @staticmethod
    def validate_deployment_config(config: Dict[str, Any]) -> tuple[bool, str]:
        """Validate deployment configuration"""
        if not config:
            return False, "Configuration is required"
        
        # Validate build command
        if 'build_command' in config:
            build_command = config['build_command']
            if not isinstance(build_command, str):
                return False, "Build command must be a string"
            if len(build_command) > 1000:
                return False, "Build command too long"
        
        # Validate environment variables
        if 'env_vars' in config:
            env_vars = config['env_vars']
            if not isinstance(env_vars, dict):
                return False, "Environment variables must be a dictionary"
            
            for key, value in env_vars.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    return False, "Environment variable keys and values must be strings"
                if len(key) > 100 or len(value) > 1000:
                    return False, "Environment variable key or value too long"
        
        return True, "Valid deployment configuration"
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        # Remove control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        return value
    
    @staticmethod
    def validate_pagination_params(skip: int, limit: int) -> tuple[bool, str]:
        """Validate pagination parameters"""
        if skip < 0:
            return False, "Skip must be >= 0"
        
        if limit < 1:
            return False, "Limit must be >= 1"
        
        if limit > 1000:
            return False, "Limit must be <= 1000"
        
        return True, "Valid pagination parameters"
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> tuple[bool, str]:
        """Validate date range"""
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            if start > end:
                return False, "Start date must be before end date"
            
            # Check if range is too large (e.g., more than 1 year)
            if (end - start).days > 365:
                return False, "Date range cannot exceed 1 year"
            
            return True, "Valid date range"
        except ValueError:
            return False, "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"
    
    @staticmethod
    def validate_sort_field(field: str, allowed_fields: List[str]) -> tuple[bool, str]:
        """Validate sort field"""
        if field not in allowed_fields:
            return False, f"Invalid sort field. Allowed: {', '.join(allowed_fields)}"
        
        return True, "Valid sort field"
    
    @staticmethod
    def validate_enum_value(value: str, enum_class) -> tuple[bool, str]:
        """Validate enum value"""
        try:
            enum_class(value)
            return True, "Valid enum value"
        except ValueError:
            allowed_values = [e.value for e in enum_class]
            return False, f"Invalid value. Allowed: {', '.join(allowed_values)}"


# Global validator instance
validator = Validator()
