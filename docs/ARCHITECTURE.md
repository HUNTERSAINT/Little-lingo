# Architecture

```mermaid
flowchart TD
    UI[Browser: HTML, CSS, JavaScript] --> API[FastAPI endpoint]
    API --> V[Pydantic request validation]
    V --> R[Dialogue router]
    R --> S[Safety phrase check]
    R --> F[Feeling and mode rules]
    R --> L[Lesson answer matcher]
    L --> P[Level and streak update]
    S --> OUT[Response model]
    F --> OUT
    P --> OUT
    OUT --> UI
```

The browser is a thin client. FastAPI validates each message, routes it to a dialogue mode, checks curated lesson answers, and returns updated session progress. No external model or transcript database is used in this version.
