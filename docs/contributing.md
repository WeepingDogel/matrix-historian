# Contributing Guide

This guide explains how to contribute changes to Matrix Historian without getting lost across services.

It is written for both human contributors and coding agents.

## Before you start

First identify which part of the system your change belongs to.

Matrix Historian is not a single-process app. It is a multi-service repository with clear boundaries:

- `services/bot/` -> Matrix ingestion and archival
- `services/api/` -> FastAPI endpoints and backend behavior
- `services/web/` -> SvelteKit frontend and browser UX
- `shared/` -> common models, schemas, CRUD, DB, and storage helpers
- `docs/` -> project documentation
- `tests/` -> Python test coverage

A good contribution usually changes the smallest number of layers necessary.

## Where to make changes

### `services/bot/`

Change this area when the task involves:
- Matrix event ingestion
- bot login / room sync behavior
- media download from Matrix
- archival of events into storage
- avatar fetching or backfill behavior
- event-type handling for messages, files, audio, video, and images

Typical examples:
- support a new Matrix event shape
- improve media ingestion reliability
- adjust how message/archive records are created
- fix bot-side logging or error handling

### `services/api/`

Change this area when the task involves:
- API routes
- request/response behavior
- archive filtering and pagination
- media endpoints
- analytics endpoints
- API-side error handling

Typical examples:
- add a new endpoint under `/api/v1`
- change filtering options for messages or media
- expose new analytics data
- improve download behavior for archived attachments

### `services/web/`

Change this area when the task involves:
- Svelte pages and components
- frontend navigation and UX
- archive browsing behavior
- analytics dashboards
- pagination controls
- language switching
- timezone display formatting
- browser-side rendering of API data

Typical examples:
- improve room/user/message filters
- change layout or UI copy
- add dashboard widgets
- update media gallery behavior

### `shared/`

Change this area when the task involves shared backend foundations:
- SQLAlchemy models
- Pydantic schemas
- CRUD helpers
- DB access
- shared storage helpers
- logic used by more than one Python service

Typical examples:
- add a new database field
- change shared response schema definitions
- add storage helper behavior used by bot and API
- update reusable query logic

Important: changes in `shared/` often affect both `services/bot/` and `services/api/`.

## Common contribution patterns

### Pattern 1: frontend-only change

Files usually touched:
- `services/web/...`
- optionally docs

Avoid changing backend code unless the UI truly needs new API behavior.

### Pattern 2: API feature change

Files usually touched:
- `services/api/...`
- possibly `shared/schemas/...`
- possibly `shared/crud/...`
- tests and docs

### Pattern 3: ingestion/storage change

Files usually touched:
- `services/bot/...`
- often `shared/models/...`
- often `shared/crud/...`
- possibly `services/api/...` if the surfaced data changes
- docs if behavior changes

### Pattern 4: schema/model change

Files usually touched:
- `shared/models/...`
- `shared/schemas/...`
- `shared/crud/...`
- any affected service code in `bot` or `api`
- tests
- migration notes or migration scripts where applicable

This is the easiest place to accidentally break multiple services. Be deliberate.

## Boundary rules

To keep the repo maintainable, prefer these boundaries.

### Bot responsibilities
- receive and process Matrix events
- download media from Matrix
- archive raw message/media information
- avoid accumulating UI-specific logic here

### API responsibilities
- expose stable HTTP behavior
- shape data for clients
- coordinate database and storage access
- avoid placing browser presentation logic here

### Web responsibilities
- present data to humans
- handle locale/timezone display
- manage browser-side interaction and layout
- avoid duplicating backend business rules unless necessary for UX

### Shared responsibilities
- reusable backend code only
- canonical data structures and DB logic
- avoid turning `shared/` into a dumping ground for unrelated helpers

## Timezone and i18n rules

These are easy to get wrong.

### Time handling
- backend and database timestamps are stored as **UTC**
- frontend may present timestamps in **Local** or **UTC**
- timezone conversion for display belongs in the frontend

Do not move browser presentation concerns into the DB schema unless there is a real architectural reason.

### Internationalization
- frontend language support currently includes `en` and `zh-CN`
- user-facing web copy should stay localizable
- backend/API docs can remain concise and technical, but should not contradict frontend terminology

## Media storage rules

Matrix Historian uses:
- **PostgreSQL** for metadata
- **MinIO** for media objects

When changing media behavior, check whether your change affects:
- bot upload flow
- stored metadata fields
- API download behavior
- public/private URL expectations
- `MINIO_PUBLIC_URL` usage

If a change alters how archived media is exposed, update docs as well.

## How to validate your change

Use the smallest useful validation set for the type of work you changed.

### For Python/backend changes

Run:

```bash
pytest
```

If your change affects local services, also consider checking logs with Docker Compose.

### For frontend changes

Run:

```bash
cd services/web
npm install
npm run check
```

If the change is substantial, also test manually with:

```bash
npm run dev
```

### For full-stack behavior changes

Use Docker Compose when practical:

```bash
docker-compose up -d --build
docker-compose ps
docker-compose logs -f api
docker-compose logs -f bot
docker-compose logs -f web
```

## Pre-PR checklist

Before opening a PR, check the following:

- the change is made in the correct service or shared layer
- user-facing behavior is documented if it changed
- new environment variables are documented in README/docs
- timezone behavior still follows the UTC-in-backend rule
- i18n-sensitive frontend text remains localizable
- media/storage changes still match PostgreSQL + MinIO responsibilities
- Python tests pass when backend/shared logic changed
- `npm run check` passes when frontend files changed
- no obvious leftover debug code, dead comments, or temporary hacks remain

## Documentation expectations

Update documentation when you change:
- service layout assumptions
- environment variables
- ports
- API behavior
- media access behavior
- frontend language/timezone behavior
- contributor workflow or architecture expectations

In general:
- user-visible behavior change -> update docs
- deployment/config change -> update docs
- architecture change -> update docs

## PR guidelines

A good PR for this repo is usually:
- focused
- architecture-aware
- explicit about which service(s) changed
- honest about trade-offs

Recommended PR summary structure:
- what changed
- which service(s) changed
- why the change was needed
- what was validated

If your change spans multiple services, explain the flow end to end.

## Suggested PR scope

Prefer smaller PRs when possible.

Good:
- one frontend improvement
- one API behavior adjustment
- one bot/media ingestion fix
- one documentation topic cleanup

Riskier:
- mixed schema, API, frontend, and deployment changes in one PR without a clear reason

When a larger change is necessary, call out the affected layers explicitly.

## Notes for coding agents

If you are an agent working in this repo:
- identify the owning layer before editing files
- avoid modifying unrelated services “just in case”
- prefer current architecture and current docs over historical assumptions
- treat `shared/` changes as cross-service changes
- keep docs in sync with behavior changes
- mention validation performed in the PR description

## Related docs

- [Overview](./overview.md)
- [Get Started](./get-started.md)
- [Deployment](./deployment.md)
- [Development](./development.md)
- [Media Storage](./media-storage.md)
