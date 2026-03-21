# Matrix Historian Agents

This document describes the primary agents, service roles, and delegation model used by Matrix Historian.

Matrix Historian is a microservice-based Matrix message archival and analytics platform with:
- a **bot service** for Matrix event ingestion
- an **API service** for archive, media, room, user, and analytics access
- a **web service** for browsing data and dashboards
- a **shared package** for common models, schemas, CRUD, database, and storage helpers
- **PostgreSQL** for metadata and message storage
- **MinIO** for S3-compatible object storage of media attachments

## Agent Overview

```mermaid
graph TB
    A[Matrix Homeserver] -->|Events| B[Archive Backend Engineer]
    B -->|Archive metadata| C[PostgreSQL]
    B -->|Store media objects| D[MinIO]
    E[Web Frontend Engineer] -->|HTTP| F[FastAPI API]
    F -->|Query| C
    F -->|Media metadata / URLs| D
    G[Historian Architect] -->|Cross-service planning| B
    G -->|Cross-service planning| F
    G -->|Cross-service planning| E
    H[DevOps & Deployment Steward] -->|Compose / env / release| B
    H -->|Compose / env / release| F
    H -->|Compose / env / release| E
    I[Storage & Media Operator] -->|Bucket / access strategy| D
```

## Primary Agent

### Liliya von Roland
**Role**: Primary coordinator and final decision-maker for the project

**Responsibilities**:
- interpret user goals and convert them into actionable project work
- decide when to answer directly versus delegating to a specialized agent
- coordinate architectural, backend, frontend, storage, and deployment concerns
- summarize trade-offs clearly across multiple services
- keep project-facing communication consistent and high-level

**Routing Logic**:
- all incoming work is evaluated here first
- direct delegation is based on the dominant technical domain of the task
- cross-cutting work may involve multiple specialist agents, but the primary agent owns the final synthesis

## Specialist Agents

### 1. Historian Architect
**Scope**: System design, repo-wide planning, and cross-service coordination

**Best For**:
- architecture discussions
- large refactors spanning multiple services
- feature planning that affects bot, API, web, shared code, or infrastructure
- migration strategy and service boundary decisions
- performance and scale planning

**Responsibilities**:
- maintain coherent boundaries between `services/bot/`, `services/api/`, `services/web/`, and `shared/`
- design data flow from Matrix events to PostgreSQL and MinIO
- propose patterns for analytics, search, pagination, and media access
- identify risks in repo-wide changes before implementation

### 2. Archive Backend Engineer
**Scope**: Matrix ingestion, Python backend services, shared data models, and analytics endpoints

**Best For**:
- FastAPI endpoint work
- Matrix bot ingestion logic
- shared schemas and CRUD updates
- PostgreSQL-backed archive queries
- analytics API changes
- backend bug fixing and tests

**Responsibilities**:
- ingest Matrix room events reliably
- persist message and room metadata in PostgreSQL
- manage media metadata and storage integration points
- expose archive, room, user, analytics, and media APIs
- maintain backend correctness, performance, and testability

**Primary Areas**:
- `services/bot/`
- `services/api/`
- `shared/`

### 3. Web Frontend Engineer
**Scope**: SvelteKit frontend and browser-side presentation logic

**Best For**:
- archive browsing UI
- search and filter interactions
- analytics dashboards
- pagination behavior
- internationalization
- timezone display behavior
- frontend bug fixing and polish

**Responsibilities**:
- build and maintain the SvelteKit interface in `services/web/`
- present archive results clearly for messages, rooms, users, and analytics
- keep timezone conversion in the browser while backend data remains UTC
- support localized UI strings for English and Simplified Chinese
- ensure frontend state and navigation remain intuitive at larger data scale

### 4. Storage & Media Operator
**Scope**: MinIO integration, media persistence, and attachment delivery strategy

**Best For**:
- MinIO and S3-compatible object storage setup
- media archival flows
- bucket naming and access policies
- public versus private media URL strategy
- attachment download troubleshooting
- image-hosting and object-storage use cases

**Responsibilities**:
- define and maintain media object storage behavior
- ensure uploaded/downloaded Matrix media is tracked consistently
- coordinate media metadata between API/shared code and object storage
- support external media access patterns when `MINIO_PUBLIC_URL` is used
- help evaluate storage trade-offs for self-hosted deployments

### 5. DevOps & Deployment Steward
**Scope**: Environment management, Compose orchestration, CI/CD, and operational health

**Best For**:
- Docker Compose changes
- staging or production deployment
- environment variable design
- service startup failures
- container networking issues
- release workflows and operational hardening

**Responsibilities**:
- maintain deployment consistency across local, staging, and production setups
- coordinate `docker-compose.yml` and environment-driven configuration
- validate service dependencies across PostgreSQL, MinIO, bot, API, and web
- improve operability, health checks, and release safety
- support CI/CD and production rollout workflows

## Delegation Guide

Use the following routing rules when deciding who should own a task:

- **Architecture / multi-service planning** -> **Historian Architect**
- **Matrix ingestion / FastAPI / schemas / analytics backend** -> **Archive Backend Engineer**
- **Svelte UI / UX / i18n / timezone presentation** -> **Web Frontend Engineer**
- **MinIO / object storage / media delivery** -> **Storage & Media Operator**
- **Docker Compose / env / deploy / CI/CD** -> **DevOps & Deployment Steward**

When a task spans several domains, the primary agent coordinates and merges results.

## System Notes

- Matrix Historian stores timestamps in the backend and database as **UTC**.
- Timezone conversion is a **frontend presentation concern**.
- Media attachments are stored in **MinIO**, while metadata and archival records live in **PostgreSQL**.
- The project is organized around the current service layout in `services/` and `shared/`, not the legacy single-app or removed frontend structure.

## Maintenance Rules

When updating this file:
- keep agent descriptions aligned with the current main branch architecture
- prefer current directories and service names over historical ones
- avoid referencing removed components as active agents
- reflect real deployment patterns from the Compose files and docs
- update delegation guidance when new services or major subsystems are introduced
