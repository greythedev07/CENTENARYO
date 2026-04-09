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

from dotenv import load_dotenv
load_dotenv()

import webview
import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import tkinter as tk

from backend.database import DatabaseManager
from backend.services.login import LoginService
from backend.services.registration import RegistrationService
from backend.services.inventory_service import InventoryService
from backend.services.senior_service import SeniorService

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

test_db = DatabaseManager()
logger.info(f"Database mode: {'CLOUD (team sync)' if test_db.is_cloud_mode() else 'LOCAL (offline)'}")
del test_db

class CentenaryoApp:
    """Main application class for CENTENARYO desktop application"""
    
    def __init__(self):
        self.window: Optional[webview.Window] = None
        self.is_dev_mode = self._detect_dev_mode()
        self.config = self._load_config()
        self.database = DatabaseManager()
        self.login_service = LoginService(self.database)
        self.registration_service = RegistrationService(self.database)
        self.inventory_service = InventoryService(self.database)
        self.senior_service = SeniorService(self.database)
        
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
    
    def _setup_api_bridge(self):
        """Setup API bridge between frontend and backend"""
        
        app = self
        
        # Create an API bridge object that pywebview can use
        class APIBridge:
            def get_version(self):
                return app._get_version()
            
            def get_config(self):
                return app._get_config()
            
            def is_dev_mode(self):
                return app.is_dev_mode
            
            def log_message(self, level: str, message: str):
                return app._log_frontend_message(level, message)
            
            def get_system_info(self):
                return app._get_system_info()
            
            def register(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._register_user(payload)
            
            def login(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._login_user(payload)
            
            def logout(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._logout_user(payload)
            
            def get_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._get_session(payload)

            def inventory_list_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._inventory_list_items(payload)

            def inventory_create_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._inventory_create_item(payload)

            def inventory_update_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._inventory_update_item(payload)

            def inventory_delete_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._inventory_delete_item(payload)

            def inventory_search_seniors(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._inventory_search_seniors(payload)

            def inventory_get_senior_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._inventory_get_senior_profile(payload)

            def inventory_issue_booklet(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._inventory_issue_booklet(payload)

            def inventory_history(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._inventory_history(payload)

            def senior_list(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._senior_list(payload)

            def senior_get(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._senior_get(payload)

            def senior_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._senior_create(payload)

            def senior_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._senior_update(payload)

            def senior_delete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                return app._senior_delete(payload)
        
        try:
            api_bridge = APIBridge()
            logger.info("API bridge initialized successfully")
        except Exception as e:
            logger.warning(f"Backend services error: {e}")
            # Fallback API bridge with minimal functionality
            class MinimalAPIBridge:
                def get_version(self):
                    return app._get_version()
                
                def is_dev_mode(self):
                    return app.is_dev_mode
                
                def log_message(self, level: str, message: str):
                    return app._log_frontend_message(level, message)
            
            api_bridge = MinimalAPIBridge()
        
        return api_bridge

    def _register_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.registration_service.register(
                full_name=str(payload.get('full_name', '')),
                username=str(payload.get('username', '')),
                password=str(payload.get('password', '')),
                confirm_password=str(payload.get('confirm_password', ''))
            )
        except Exception as error:
            logger.exception("Registration error")
            return {'ok': False, 'error': f"Registration failed: {error}"}

    def _login_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.login_service.login(
                username=str(payload.get('username', '')),
                password=str(payload.get('password', '')),
                remember_me=bool(payload.get('remember_me', False))
            )
        except Exception as error:
            logger.exception("Login error")
            return {'ok': False, 'error': f"Login failed: {error}"}

    def _logout_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        token = str(payload.get('token', ''))
        return self.login_service.logout(token)

    def _get_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        token = str(payload.get('token', ''))
        return self.login_service.get_session(token)

    def _inventory_list_items(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        search = str(payload.get('search', ''))
        return self.inventory_service.list_items(search=search)

    def _inventory_create_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.inventory_service.create_item(payload)

    def _inventory_update_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.inventory_service.update_item(payload)

    def _inventory_delete_item(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.inventory_service.delete_item(payload.get('id'))

    def _inventory_search_seniors(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = str(payload.get('query', ''))
        return self.inventory_service.search_seniors(query=query)

    def _inventory_get_senior_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.inventory_service.get_senior_profile(payload.get('senior_id'))

    def _inventory_issue_booklet(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.inventory_service.issue_booklet(payload)

    def _inventory_history(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.inventory_service.get_history(limit=payload.get('limit', 20))

    def _senior_list(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.senior_service.list_seniors(
            query=str(payload.get('query', '')),
            status=str(payload.get('status', '')),
            page=payload.get('page', 1),
            page_size=payload.get('page_size', 20),
            sort_key=str(payload.get('sort_key', 'id')),
            sort_dir=str(payload.get('sort_dir', 'asc')),
        )

    def _senior_get(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.senior_service.get_senior(payload.get('id'))

    def _senior_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.senior_service.create_senior(payload)

    def _senior_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.senior_service.update_senior(payload)

    def _senior_delete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.senior_service.delete_senior(payload.get('id'))
    
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