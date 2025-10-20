---
description: "Task list for feature implementation"
---

# Tasks: Interfaccia web Docker per CommonForms (Upload, Elaborazione, Download, Compressione)

**Input**: Design documents from /specs/002-crea-una-interfaccia/
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: The spec did not explicitly request tests; omit test tasks unless requested in clarifications.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: [ID] [P?] [Story] Description
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- Single project with a new web module at repository root: webapp/
  - webapp/src/ (application code)
  - webapp/templates/ (HTML templates)
  - webapp/static/ (static assets)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for the web interface

- [X] T001 Create project structure in webapp/ (folders: webapp/src, webapp/templates, webapp/static)
- [X] T002 Add .dockerignore at repo root and webapp/.dockerignore with standard Python/node ignores
- [X] T003 Create webapp/Dockerfile to run the web app with configurable PORT env var
- [X] T004 Add config module webapp/src/config.py (env vars: PORT, MAX_UPLOAD_MB=25, LANGUAGE='it', HF_HOME, CLEANUP_MINUTES=10)
- [X] T005 [P] Configure logging in webapp/src/logging_config.py (structured, level via env)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required before implementing any user story

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement server bootstrap webapp/src/app.py (web server setup, template engine, static files)
- [X] T007 [P] Add validation utilities webapp/src/utils/validation.py (MIME/ext=pdf, size limit from config)
- [X] T008 [P] Implement cleanup service webapp/src/services/cleanup.py (delete temp files older than TTL)
- [X] T009 Implement CommonForms adapter webapp/src/services/commonforms_adapter.py (wrap commonforms.prepare_form)
- [X] T010 [P] Add compression service stubs webapp/src/services/compression.py (placeholders for ZIP and PDF reduction)
- [X] T011 Create base template webapp/templates/index.html (upload form, status placeholder)

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 - Carica PDF e scarica modulo compilabile (Priority: P1) MVP

**Goal**: Upload singolo PDF, applica campi compilabili con CommonForms e consente il download del risultato

**Independent Test**: Caricare un PDF valido e scaricare un PDF con campi compilabili coerenti

### Implementation for User Story 1

- [X] T012 [US1] Implement upload route webapp/src/routes/upload.py (POST /upload): salva file tmp, valida, invoca adapter, persiste artefatto (id percorso)
- [X] T013 [US1] Implement download route webapp/src/routes/download.py (GET /download/{id}): restituisce PDF elaborato (content-disposition)
- [X] T014 [US1] Wire routes in webapp/src/app.py (monta router, configura template/index)
- [X] T015 [US1] Update webapp/templates/index.html (form multipart/form-data, messaggio "in elaborazione" → link download)
- [X] T016 [US1] Add error handling mapping (validazione, file non supportato) → messaggi utente

**Checkpoint**: User Story 1 completa e indipendentemente verificabile

---

## Phase 4: User Story 2 - Scelta compressione prima del download (Priority: P2)

**Goal**: Permettere all'utente di scegliere compressione (nessuna/ZIP/PDF) prima del download

**Independent Test**: Elaborare un PDF, selezionare l'opzione, scaricare il file conforme alla scelta

### Implementation for User Story 2

- [X] T017 [US2] Estendere UI in webapp/templates/index.html (radio: nessuna, ZIP, PDF)
- [X] T018 [US2] Implementare webapp/src/services/compression.py (funzioni zip_output(), compress_pdf())
- [X] T019 [US2] Integrare compressione nel download in webapp/src/routes/download.py (param opzione → esegui strategia)
- [X] T020 [US2] Mostrare dimensione file risultante nella UI (se disponibile)

**Checkpoint**: User Story 2 completa e indipendentemente verificabile

---

## Phase 5: User Story 3 - Gestione errori di upload/validazione (Priority: P3)

**Goal**: Messaggi chiari per PDF corrotti, troppo grandi o formati non supportati

**Independent Test**: Caricare file troppo grandi o corrotti e verificare messaggi e blocchi adeguati

### Implementation for User Story 3

- [X] T021 [US3] Validazioni: limite dimensione e tipo in webapp/src/utils/validation.py + mapping messaggi localizzati (IT/EN)
- [X] T022 [US3] Template errori webapp/templates/error.html per errori comuni (corruzione, tipo, dimensione)
- [X] T023 [US3] Gestione stato/progresso e timeout con messaggi utente ("in elaborazione"/"pronto")

**Checkpoint**: Tutte le storie utente sono indipendentemente funzionali

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Migliorie trasversali e documentazione

- [ ] T024 Documentazione webapp/README.md (variabili ambiente, run locale, Docker)
- [X] T025 Aggiungere docker-compose.yml (opzionale) per avvio rapido con porta mappata
- [ ] T026 [P] Security: sanitizzare nomi file, percorsi temporanei sicuri, prevenire path traversal
- [ ] T027 Parametrizzare CLEANUP_MINUTES e verificare pulizia post-consegna
- [ ] T028 [P] Quickstart: validare manualmente il flusso US1→US2→US3

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) → Foundational (Phase 2) → User Stories (Phase 3+)
- User stories procedono in ordine di priorità: P1 → P2 → P3

### User Story Dependencies

- US1 non dipende da altre storie
- US2 dipende da US1 (riutilizza output e flusso download)
- US3 indipendente per validazioni/UX (ma integra con routing esistente)

### Within Each User Story

- Moduli/servizi prima delle route
- Route prima dell'integrazione UI
- Messaggi/UX per ultimi

### Parallel Opportunities

- [P] T005, T007, T008, T010, T026, T028 possono procedere in parallelo

---

## Parallel Example: User Story 1

`ash
# Moduli paralleli
Task: "Implement validation utilities in webapp/src/utils/validation.py"
Task: "Implement CommonForms adapter in webapp/src/services/commonforms_adapter.py"

# Integrazione sequenziale
Task: "Implement upload route in webapp/src/routes/upload.py"
Task: "Implement download route in webapp/src/routes/download.py"
Task: "Wire routes in webapp/src/app.py and update index.html"
`

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks stories)
3. Complete Phase 3: User Story 1
4. STOP and VALIDATE: Verifica flusso upload → download
5. Deploy/demo se pronto

### Incremental Delivery

1. Foundation pronta → aggiungi US1 → valida → demo (MVP)
2. Aggiungi US2 → valida/dimostra la compressione
3. Aggiungi US3 → valida la gestione errori e UX

### Parallel Team Strategy

- Dev A: Validazioni e adapter (T007, T009)
- Dev B: Bootstrap e routing (T006, T012–T014)
- Dev C: Compressione e UI (T010, T017–T020)

---

## Notes

- Ogni storia deve essere consegnabile indipendentemente
- Evitare conflitti sullo stesso file; usare [P] quando i file differiscono
- Commit frequenti dopo ogni task o gruppo logico




