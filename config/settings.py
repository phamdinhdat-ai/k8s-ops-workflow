"""Configuration settings."""
import os
from pathlib import Path


class Settings:
    """Application settings."""
    
    # API Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    
    # Kubernetes Configuration
    KUBECONFIG = os.getenv("KUBECONFIG", "~/.kube/config")
    DEFAULT_NAMESPACE = os.getenv("DEFAULT_NAMESPACE", "default")
    DEFAULT_CLUSTER = os.getenv("DEFAULT_CLUSTER", "production")
    
    # Vector DB Configuration
    VECTORDB_PATH = os.getenv("VECTORDB_PATH", "./data/vectordb")
    VECTORDB_COLLECTION = os.getenv("VECTORDB_COLLECTION", "k8s_logs")
    
    # Workflow Configuration
    STREAMING_ENABLED = os.getenv("STREAMING_ENABLED", "true").lower() == "true"
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))
    
    # Memory Configuration
    MEMORY_STORAGE_PATH = os.getenv("MEMORY_STORAGE_PATH", "./data/memory")
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    @classmethod
    def validate(cls):
        """Validate required settings."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        # Create directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)


settings = Settings()
