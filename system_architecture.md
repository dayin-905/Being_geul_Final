
# System Architecture

## Overview
This document outlines the high-level architecture of the **Being Geul Youth Policy Platform**. The system follows a standard client-server architecture using **FastAPI** for the backend and **PostgreSQL** for the database, with a **Vanilla HTML/JS** frontend enhanced by **TailwindCSS** and **GSAP**.

## Architecture Diagram (Mermaid)

```mermaid
graph TD
    %% Define styles
    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef server fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef db fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    
    %% Setup Nodes
    Client[Browser Client]:::client
    LoadBalancer[Load Balancer / Reverse Proxy]:::server
    AppServer[FastAPI Application Server]:::server
    Database[(PostgreSQL Database)]:::db

    %% Connections
    Client -- HTTP/HTTPS --> LoadBalancer
    LoadBalancer -- Proxies Request --> AppServer
    AppServer -- SQL via SQLAlchemy --> Database

    %% Sub-components within AppServer (Logical View)
    subgraph Backend_Modules [Backend Modules]
        direction TB
        Auth["Auth Router<br/>(auth.py)"]
        MainPage["Main Router<br/>(main_page.py)"]
        MyPage["My Page Router<br/>(mypage.py)"]
        AllPage["Search/Filter Router<br/>(all.py)"]
        RecSys["Recommendation Engine<br/>(recommendation.py)"]
        Shared["Database Session<br/>(database.py)"]
    end
    
    %% Connect AppServer to Logical Components
    AppServer -.-> Backend_Modules

    %% External Configuration
    Config[.env Config]
    Config -.-> AppServer
```

## Component Details

### 1. Frontend (Client)
- **Tech Stack**: HTML5, CSS3, JavaScript (ES6+)
- **Libraries**:
    - **TailwindCSS**: For utility-first styling.
    - **GSAP (GreenSock)**: For high-performance animations (ScrollTrigger).
    - **Lenis**: For smooth scrolling effects.
    - **Chart.js**: For visualizing stats (e.g., Policy MBTI).
- **Responsibility**: Renders UI, handles user interactions, and communicates with the backend via fetch/XHR.

### 2. Backend (Server)
- **Tech Stack**: Python 3.x, FastAPI
- **ORM**: SQLAlchemy
- **Responsibility**:
    - RESTful API endpoints.
    - Business logic (Swiping, filtering, recommendations).
    - Authentication and session management.

### 3. Database
- **Tech Stack**: PostgreSQL (v14+)
- **Connection**: Managed via `database.py` using `python-dotenv` to load credentials from `.env`.
- **Tables**: Users, Policies (`being_test`), User Actions (`users_action`).

### 4. Configuration
- **Environment Variables** (`.env`):
    - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database connection details.
    - `SECRET_KEY`: For security/JWT (if applicable).
