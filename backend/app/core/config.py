import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Configuration manager that loads YAML config files and supports environment variable overrides."""
    
    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self._config: Dict[str, Any] = {}
        self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self):
        """Load configuration from YAML file based on environment."""
        config_file = self.config_dir / f"{self.environment}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as file:
            self._config = yaml.safe_load(file)
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides for sensitive data."""
        # Server configuration
        if port := os.getenv("PORT"):
            self._config["server"]["port"] = int(port)
        if host := os.getenv("HOST"):
            self._config["server"]["host"] = host
        
        # Logging configuration
        if log_level := os.getenv("LOG_LEVEL"):
            self._config["logging"]["level"] = log_level.upper()
        
        # LLM configuration
        if openai_api_key := os.getenv("OPENAI_API_KEY"):
            if "llm" not in self._config:
                self._config["llm"] = {}
            self._config["llm"]["api_key"] = openai_api_key
        
        if claude_api_key := os.getenv("CLAUDE_API_KEY"):
            if "llm" not in self._config:
                self._config["llm"] = {}
            self._config["llm"]["claude_api_key"] = claude_api_key
        
        if gemini_api_key := os.getenv("GEMINI_API_KEY"):
            if "llm" not in self._config:
                self._config["llm"] = {}
            self._config["llm"]["gemini_api_key"] = gemini_api_key
        
        # Database configuration
        if database_url := os.getenv("DATABASE_URL"):
            self._config["database"]["url"] = database_url
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'server.port')."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self._config.get(section, {})
    
    @property
    def environment(self) -> str:
        """Get current environment."""
        return self._environment
    
    @environment.setter
    def environment(self, value: str):
        """Set environment."""
        self._environment = value
    
    @property
    def all_config(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()


# Global config instance
config = ConfigManager()