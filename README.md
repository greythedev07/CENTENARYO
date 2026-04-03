# CENTENARYO

CENTENARYO: A Centralized End-to-end Network for Transactional Entitlement, Notification, Anomaly Review, and Year-end Oversight using Random Forest Anomaly Detection and Prescriptive Audit Analytics.

## PROJECT OVERVIEW

CENTENARYO is an offline-first desktop management system for Local Government Unit (LGU) Offices of Senior Citizens Affairs (OSCA). It replaces Excel spreadsheets and paper-based workflows with a centralized, secure platform for managing senior citizen records, automating pension payroll, tracking benefit assets, and detecting fraudulent records using machine learning.

## TECHSTACK

### Backend
- **Python 3.11**: Core business logic, database management, ML processing
- **SQLite3**: Local relational database for offline operation
- **PyWebView**: Desktop application wrapper

### Frontend  
- **HTML5**: Semantic markup for accessibility
- **Pico.css**: Minimalist responsive framework for government staff
- **Chart.js**: Analytics dashboards and data visualization

### Machine Learning
- **Random Forest**: Anomaly detection for fraud prevention
- **Feature Engineering**: Data preprocessing for ML models

## CORE MODULES

1. **Senior Citizen Registry** - Centralized citizen database with duplicate detection
2. **Payroll Automation** - Automated pension disbursement generation  
3. **Inventory Tracking** - Physical benefit asset management (IDs, booklets)
4. **Anomaly Detection** - ML-powered fraud detection and risk scoring
5. **Analytics Dashboard** - Decision-making insights for LGU officials
6. **Audit Logging** - Complete traceability of all system actions

## DEVELOPMENT STATUS

### Current State
- Project structure and architecture established
- Login interface with splash screen completed
- Global styling system implemented
- Backend services need implementation
- Database schema needs integration
- ML models need training and deployment

### Next Development Priorities
1. Implement SQLite database connection and schema
2. Create backend service classes (senior, payroll, inventory, audit)
3. Develop Random Forest anomaly detection system
4. Build module-specific frontend pages
5. Integrate PyWebView API bridge between frontend and backend

## SYSTEM REQUIREMENTS

- Windows 10/11 (primary target for LGU deployment)
- 4GB RAM minimum (optimized for low-end government computers)
- 500MB disk space
- No internet connection required (offline-first design)

## FILE STRUCTURE

```
centenaryo/
├── main.py                 # PyWebView desktop launcher
├── backend/                # Python backend services
│   ├── database.py         # SQLite connection and queries
│   ├── models.py           # Data models and ORM
│   └── services/           # Business logic modules
├── frontend/               # Web interface
│   ├── index.html          # Login and splash screen
│   ├── css/styles.css      # Global styling system
│   └── libs/               # Third-party libraries
└── data/                   # SQLite database and backups