
# System Use Case Diagram

## Overview
This document illustrates the primary use cases for the **Being Geul Youth Policy Platform**, showing how different actors interact with the system's features.

## Actors
1. **Guest**: A visitor who has not logged in.
2. **User**: A focused, logged-in member seeking youth policies.
3. **Admin**: A system administrator managing the platform content.

## Use Case Diagram (Mermaid)

```mermaid
graph LR
    %% Styles
    classDef actor fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef usecase fill:#fff,stroke:#333,stroke-width:1px,stroke-dasharray: 0;

    %% Actors
    G[Guest]:::actor
    U[User]:::actor
    A[Admin]:::actor

    %% System Boundary
    subgraph System ["Being Geul Platform"]
        direction TB
        
        %% Guest Use Cases
        UC_ViewLanding([View Landing Page])
        UC_SignUp([Sign Up])
        UC_Login([Login])
        
        %% Main Discovery
        UC_ViewMain([View Main Recommendations])
        UC_Swipe([Swipe Policies Like/Pass])
        UC_ViewDetail([View Policy Details])
        
        %% Search & Filter
        UC_Search([Search Policies])
        UC_Filter([Filter by Region/Genre])
        
        %% My Page
        UC_MyPage([View My Page])
        UC_ManageLikes([Manage Liked Policies])
        UC_ViewMBTI([View Policy MBTI])
        UC_EditProfile([Edit Profile / Avatar])
        
        %% Admin
        UC_ManagePolicy([Manage Policy Data])
        UC_ViewStats([View User Stats])
    end

    %% Relationships - Guest
    G --> UC_ViewLanding
    G --> UC_SignUp
    G --> UC_Login

    %% Relationships - User
    U --> UC_ViewMain
    U --> UC_Swipe
    U --> UC_ViewDetail
    U --> UC_Search
    U --> UC_Filter
    U --> UC_MyPage
    U --> UC_ManageLikes
    U --> UC_ViewMBTI
    U --> UC_EditProfile

    %% Inheritance representation (User extends Guest behavior)
    G -.-> U

    %% Relationships - Admin
    A --> UC_Login
    A --> UC_ManagePolicy
    A --> UC_ViewStats
    
    %% Functional Relationships
    UC_Search -.->|include| UC_Filter
    UC_ViewMain -.->|extend| UC_ViewDetail
    UC_Swipe -.->|extend| UC_ViewDetail
```

## Key Workflows

### 1. Policy Discovery (Main Loop)
- **Actor**: User
- **Flow**: User logs in -> Views Main Page -> Swipes Cards (Like/Pass) -> Clicks for Detail -> System updates preferences.

### 2. Personalized Dashboard (My Page)
- **Actor**: User
- **Flow**: User accesses My Page -> Checks MBTI Type -> Reviews "Liked" Policies -> Updates Profile Avatar.
