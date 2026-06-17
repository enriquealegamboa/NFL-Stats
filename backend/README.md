# backend

NFL Stats REST API. Java + Spring Boot, deployed on [Railway](https://railway.app/), data from [Supabase](https://supabase.com/).

## Local development

Requires a JDK 21 on your PATH (e.g. `winget install Microsoft.OpenJDK.21`). Maven itself is
not required — the project ships the Maven Wrapper (`mvnw`), which downloads the right Maven
version on first use.

```bash
cp .env.example .env   # optional until you add DB access (see below)
./mvnw spring-boot:run
```

On Windows PowerShell use `.\mvnw.cmd spring-boot:run`.

Server runs on `http://localhost:8080`. Health check at `/health`.

## Commands

- `./mvnw spring-boot:run` — run the app locally (watch/restart with the `spring-boot-devtools` profile if added)
- `./mvnw test` — run the test suite
- `./mvnw clean package` — compile, run tests, and produce `target/app.jar`
- `java -jar target/app.jar` — run the packaged jar (this is what Railway runs)

## Deploying to Railway

Railway auto-detects the Maven project (via `pom.xml`) and uses `railway.json` for
build/start/healthcheck. The start command runs the packaged jar: `java -jar target/app.jar`.

1. Create a new Railway project and link this folder (or set the service root to `backend/`).
2. Set env vars: `CORS_ORIGIN` (your Vercel URL), and — once you enable DB access —
   `SUPABASE_DB_URL`, `SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD`.
3. Push to the connected branch.

## Layout

```
pom.xml                                  # Maven build + dependencies
src/main/java/com/nflstats/backend/
  BackendApplication.java                # Spring Boot entry point
  controller/
    RootController.java                  # GET /
    HealthController.java                # GET /health, POST /health/echo
  dto/
    EchoRequest.java                     # request body + Bean Validation constraints
    EchoResponse.java
  error/
    ErrorCode.java                       # VALIDATION_FAILED / NOT_FOUND / INTERNAL_ERROR
    ErrorEnvelope.java                   # the { error: { code, message, details? } } shape
    AppException.java                    # base client-facing error (code + status + details)
    NotFoundException.java               # 404 helper
    GlobalExceptionHandler.java          # @RestControllerAdvice — maps errors to the envelope
  config/
    CorsConfig.java                      # CORS, reads CORS_ORIGIN
src/main/resources/application.properties
src/test/java/com/nflstats/backend/HealthContractTest.java
```

## Database access (Spring Data JPA)

The Spring Data JPA + PostgreSQL dependencies are on the classpath, but database
auto-configuration is **disabled** in `application.properties` so the app boots without a
database (matching the previous behavior and keeping the Railway health check green).

To enable it when you build the first stats endpoint:

1. Add a JPA `@Entity` (and a `Repository`) mapping one of the tables in `database/migrations/`.
2. Set `SUPABASE_DB_URL`, `SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD` (JDBC connection from the
   Supabase dashboard: Project Settings → Database → Connection string → JDBC).
3. Delete the `spring.autoconfigure.exclude=...` line in `application.properties`.

`spring.jpa.hibernate.ddl-auto=none` is set so Hibernate never creates or alters tables — the
schema is owned by the SQL migrations in `database/`.

## Error format

Every error response uses the same envelope:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": { "issues": [ { "path": "body.message", "message": "size must be between 1 and 280", "code": "Size" } ] }
  }
}
```

- `code` — stable string constant. Current codes: `VALIDATION_FAILED` (400), `NOT_FOUND` (404), `INTERNAL_ERROR` (500).
- `message` — human-readable summary. Safe to surface to end users.
- `details` — optional, code-specific payload. For `VALIDATION_FAILED`, an `issues[]` array with `path` / `message` / `code` per failed field constraint.

Unhandled errors are logged server-side and returned as an opaque `INTERNAL_ERROR` 500 — stack traces are never sent in the response body.

### Smoke test

```bash
# Success
curl -s -X POST http://localhost:8080/health/echo \
  -H 'content-type: application/json' \
  -d '{"message":"hello"}'
# -> {"echoed":"hello"}

# Validation failure
curl -s -X POST http://localhost:8080/health/echo \
  -H 'content-type: application/json' \
  -d '{}'
# -> {"error":{"code":"VALIDATION_FAILED", ...}}
```
