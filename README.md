# Group3_Project6

# Architecture Snapshot – Financial Performance System

## High-Level Overview

Client (JMeter / UI)
        |
        v
FastAPI (HTTP / REST)
        |
        v
Service Layer
        |
        v
Database (SQLite )

## Key Design Decisions

- FastAPI used to simplify REST routing and OpenAPI generation
- Clear separation between:
  - API layer (routes & HTTP concerns)
  - Service layer (business logic & computation)
  - Data layer (DB – to be implemented)
- Designed specifically to support performance and load testing
- Includes intentionally heavy endpoints (CPU & payload)

## Load & Stress Strategy

- CPU-heavy endpoints controlled via query params
- Large payload endpoints to stress network and memory
- DB hooks left unoptimized for later performance improvements

## Team Ownership

- Dona: API, HTTP protocol, architecture
- Nikhil: Database schema & queries
- Meera: JMeter & Docker
- Brooks: Documentation
