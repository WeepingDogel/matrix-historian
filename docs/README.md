# Matrix Historian Documentation

This documentation covers the current main-branch architecture of Matrix Historian: a Matrix archiver with backend services, PostgreSQL + MinIO storage, and a Svelte web frontend.

## Documentation map

- **[Overview](./overview.md)**
  - Architecture and main components
  - Core capabilities
  - Current project status

- **[Get Started](./get-started.md)**
  - Local setup with Docker Compose
  - Required environment variables
  - First-run verification

- **[Deployment](./deployment.md)**
  - Service layout
  - Docker deployment notes
  - Environment and operations guidance

- **[Development](./development.md)**
  - Backend and frontend development flow
  - Local run commands
  - Testing and contribution notes

- **[API Reference](./reference/api-reference.md)**
  - API groups and usage notes
  - Reminder to treat API timestamps as UTC

## Important current behavior

### Web frontend exists

The current project includes a web frontend in `services/web/`.

### Time handling

- backend/database timestamps are stored in **UTC**
- frontend presentation can display either **Local** (browser timezone) or **UTC**
- timezone conversion is a **frontend concern**, not a DB/backend schema concern

### Internationalization

The web UI currently supports:
- `en`
- `zh-CN`

Language and timezone preferences are handled client-side.

## Primary entrypoints

- **Web UI**: http://localhost:3000
- **API**: http://localhost:8500
- **Swagger**: http://localhost:8500/docs
- **MinIO Console**: http://localhost:9001

## Notes about older docs

If you see references elsewhere to SQLite, a removed frontend, or old ports/endpoints, treat them as historical and prefer the docs in this directory plus the root README.
