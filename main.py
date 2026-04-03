"""
CENTENARYO Main Entry Point
===========================

Purpose: Desktop application launcher using PyWebView framework
Connects to: frontend/index.html (login interface), backend/services/*.py
Dependencies: webview, logging, pathlib, sys, os

This file serves as the main entry point that wraps the web frontend
in a desktop application window using PyWebView. It provides the
desktop container for the entire CENTENARYO OSCA management system.

Features:
- Configurable window dimensions and settings
- Error handling and logging
- Backend API bridge setup
- Development vs production mode detection
- Graceful shutdown handling
- Resource path management
"""

import webview
import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import tkinter as tk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/centenaryo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CentenaryoApp:
    """Main application class for CENTENARYO desktop application"""
    
    def __init__(self):
        self.window: Optional[webview.Window] = None
        self.is_dev_mode = self._detect_dev_mode()
        self.config = self._load_config()
        
        # Ensure required directories exist
        self._ensure_directories()
    
    def _detect_dev_mode(self) -> bool:
        """Detect if running in development mode"""
        return getattr(sys, 'frozen', False) is False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load application configuration"""
        default_config = {
            'title': 'CENTENARYO - OSCA Management System',
            'url': 'frontend/index.html',
            'width': 800,
            'height': 600,
            'min_size': (800, 600),
            'resizable': True,
            'frameless': False,
            'easy_drag': True,
            'on_top': False,
            'shadow': True,
            'vibrancy': False,
            'background_color': '#FFFFFF'
        }
        
        # Override with environment variables if present
        config = default_config.copy()
        
        if self.is_dev_mode:
            # Development-specific settings
            config.update({
                'width': int(os.getenv('CENTENARYO_WIDTH', 1000)),
                'height': int(os.getenv('CENTENARYO_HEIGHT', 700)),
                'debug': True
            })
        
        return config
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = ['logs', 'data', 'data/backups']
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _get_resource_path(self, relative_path: str) -> str:
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def _setup_api_bridge(self) -> Dict[str, Any]:
        """Setup API bridge between frontend and backend"""
        api_bridge = {}
        
        try:
            # Import backend services when implemented
            # from backend.services.senior_service import senior_service
            # from backend.services.payroll_service import payroll_service
            # from backend.services.inventory_service import inventory_service
            # from backend.services.audit_service import audit_service
            
            # For now, provide placeholder functions
            api_bridge = {
                'get_version': self._get_version,
                'get_config': self._get_config,
                'is_dev_mode': lambda: self.is_dev_mode,
                'log_message': self._log_frontend_message,
                'get_system_info': self._get_system_info
            }
            
            logger.info("API bridge initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Backend services not available: {e}")
            # Provide minimal API for frontend-only operation
            api_bridge = {
                'get_version': self._get_version,
                'is_dev_mode': lambda: self.is_dev_mode,
                'log_message': self._log_frontend_message
            }
        
        return api_bridge
    
    def _get_version(self) -> Dict[str, str]:
        """Get application version information"""
        return {
            'version': '1.0.0',
            'build': '2026.04.03',
            'mode': 'development' if self.is_dev_mode else 'production'
        }
    
    def _get_config(self) -> Dict[str, Any]:
        """Get current configuration (safe for frontend)"""
        safe_config = {
            'title': self.config['title'],
            'is_dev_mode': self.is_dev_mode,
            'version': self._get_version()['version']
        }
        return safe_config
    
    def _log_frontend_message(self, level: str, message: str):
        """Log messages from frontend"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, f"Frontend: {message}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for diagnostics"""
        import platform
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'app_path': os.getcwd()
        }
    
    def _get_screen_center(self, width: int, height: int) -> Tuple[int, int]:
        """Calculate center position for window on screen"""
        try:
            # Use tkinter to get screen dimensions
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            # Calculate center position
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            return x, y
        except Exception as e:
            logger.warning(f"Could not get screen center: {e}, using default position")
            return 100, 100  # Fallback position
    
    def create_window(self):
        """Create and configure the main application window"""
        try:
            # Prepare URL
            if self.is_dev_mode:
                # In development, use local file
                url = self._get_resource_path(self.config['url'])
            else:
                # In production, use bundled file
                url = self._get_resource_path(self.config['url'])
            
            # Setup API bridge
            api_bridge = self._setup_api_bridge()
            
            # Calculate center position
            x, y = self._get_screen_center(
                self.config['width'],
                self.config['height']
            )
            
            # Create window with configuration
            self.window = webview.create_window(
                title=self.config['title'],
                url=url,
                width=self.config['width'],
                height=self.config['height'],
                x=x,
                y=y,
                min_size=self.config['min_size'],
                resizable=self.config['resizable'],
                frameless=self.config['frameless'],
                easy_drag=self.config['easy_drag'],
                on_top=self.config['on_top'],
                shadow=self.config['shadow'],
                vibrancy=self.config['vibrancy'],
                background_color=self.config['background_color'],
                js_api=api_bridge
            )
            
            logger.info(f"Window created: {self.config['width']}x{self.config['height']} at position ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Failed to create window: {e}")
            raise
    
    def run(self):
        """Start the application"""
        try:
            logger.info("Starting CENTENARYO application...")
            logger.info(f"Mode: {'Development' if self.is_dev_mode else 'Production'}")
            
            # Create and start window
            self.create_window()
            webview.start()
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            sys.exit(1)
        finally:
            logger.info("Application shutdown complete")

def main():
    """Main entry point"""
    try:
        app = CentenaryoApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()