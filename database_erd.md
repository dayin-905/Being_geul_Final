
# Entity Relationship Diagram (ERD)

## Overview
This document describes the database schema for the **Being Geul** application. The database is **PostgreSQL**, and the connection settings are managed via the `.env` file (referenced by `database.py`).

## Database Connection
The application uses **SQLAlchemy** to connect to the database. The connection URL is constructed using environment variables:
`postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}`

## ER Diagram (Mermaid)

```mermaid
erDiagram
    %% Entities
    users {
        int id PK
        string email UK "Not Null, Unique Index"
        string name "Not Null"
        string password "Nullable"
        string region "Nullable"
        string provider "Default: local"
        string subscription_level "Default: free"
        string profile_icon "Default: avatar_1"
    }

    being_test {
        int id PK "Auto Increment"
        text title "Not Null"
        text summary
        text period
        text link
        text genre
        text region
        text original_id
        datetime created_at
        date end_date
        int view_count "Default: 0"
        boolean is_active "Default: True"
    }

    users_action {
        int id PK "Auto Increment"
        string user_email FK "Ref: users.email"
        int policy_id FK "Ref: being_test.id"
        string type "Not Null (e.g. like, pass)"
        datetime created_at "Default: Now"
    }

    %% Relationships
    users ||--o{ users_action : "performs"
    being_test ||--o{ users_action : "is target of"

```

## Table Descriptions

### 1. `users`
Stores user account information.
- **Key Fields**: `email` (Unique Identifier), `provider` (Login method), `subscription_level` (User tier).
- **Relations**: Referenced by `users_action` via `email`.

### 2. `being_test` (Policies)
The main table storing youth policy information.
- **Key Fields**: `category` (genre), `region`, `end_date`.
- **Relations**: Referenced by `users_action` via `id`.

### 3. `users_action`
A log of user interactions with policies.
- **Purpose**: Tracks 'likes' (swipes right) or 'passes' (swipes left).
- **Logic**: Used for building the "My Liked Policies" list and recommendation logic.
