# Feature Specification: Interfaccia web Docker per CommonForms (Upload, Elaborazione, Download, Compressione)

**Feature Branch**: $branch  
**Created**: 2025-10-20  
**Status**: Draft  
**Input**: User description: "Crea una interfaccia web da ospitare tramite docker che permette di caricare file pdf. utilizza commonforms per applicare campi compilabili. Fa scaricare il pdf. Eventualmente chiede se si vuole comprimere prima del download."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carica PDF e scarica modulo compilabile (Priority: P1)

L'utente carica un file PDF tramite interfaccia web; il sistema applica i campi
compilabili usando CommonForms e permette di scaricare il PDF risultante.

**Why this priority**: È il flusso principale che genera valore immediato.

**Independent Test**: Caricare un PDF valido e verificare che il download produca
un PDF con campi compilabili coerenti.

**Acceptance Scenarios**:

1. Given un PDF valido, When viene caricato, Then il sistema restituisce un PDF con campi compilabili.
2. Given un PDF con campi esistenti, When è impostato "mantieni campi esistenti", Then i campi originali sono preservati.

---

### User Story 2 - Scelta compressione prima del download (Priority: P2)

Dopo l'elaborazione, l'utente può scegliere se scaricare il PDF così com'è oppure
scaricare una versione compressa.

**Why this priority**: Migliora l'esperienza per file pesanti o per invii via email.

**Independent Test**: Eseguire l'elaborazione, selezionare l'opzione di compressione,
verificare che il file scaricato rispetti l'opzione scelta.

**Acceptance Scenarios**:

1. Given un PDF elaborato, When l'utente seleziona "Scarica compresso", Then il sistema fornisce il file compresso.
2. Given nessuna selezione, When l'utente procede, Then il sistema scarica il PDF non compresso.

---

### User Story 3 - Gestione errori di upload/validazione (Priority: P3)

L'utente riceve messaggi chiari per PDF corrotti, troppo grandi o formati non supportati.

**Why this priority**: Evita frustrazione e riduce richieste di supporto.

**Independent Test**: Caricare file troppo grandi o corrotti e verificare messaggi e blocchi adeguati.

**Acceptance Scenarios**:

1. Given un file > limite dimensione, When viene caricato, Then l'upload è rifiutato con messaggio esplicativo.
2. Given un file non-PDF, When viene caricato, Then il sistema blocca l'operazione e informa l'utente.

### Edge Cases

- File PDF con molte pagine (>300) e immagini ad alta risoluzione.
- PDF protetti da password o con restrizioni di modifica.
- Interruzione della connessione durante l'upload o il download.
- Doppio invio della stessa richiesta (debounce/idempotenza scarico).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Il sistema MUST offrire un'interfaccia web per caricare un singolo file PDF per richiesta.
- **FR-002**: Il sistema MUST elaborare il PDF utilizzando CommonForms per applicare campi compilabili.
- **FR-003**: L'utente MUST poter scaricare il PDF elaborato al termine del processo.
- **FR-004**: Il sistema MUST offrire un'opzione di download compresso prima del download finale.
- **FR-005**: Il sistema MUST validare tipo MIME ed estensione e rifiutare file non PDF con messaggi chiari.
- **FR-006**: Il sistema MUST imporre un limite dimensionale all'upload (default 25 MB) con messaggio esplicativo.
- **FR-007**: Il sistema MUST mostrare stato/progresso (almeno “in elaborazione” vs “pronto per il download”).
- **FR-008**: Il sistema MUST essere avviabile in container e configurabile tramite variabili d'ambiente standard (porta, limiti dimensione, lingua UI).
- **FR-009**: Il sistema MUST non conservare i file oltre la sessione di elaborazione (eliminazione dopo la consegna o timeout).
- **FR-010**: Il sistema SHOULD offrire localizzazione minima (IT/EN) per messaggi principali.

- **FR-011**: Modalità di compressione per il download via [NEEDS CLARIFICATION: preferisci ZIP dell'output oppure compressione del PDF (riduzione dimensione)?]
- **FR-012**: Ambito upload [NEEDS CLARIFICATION: singolo file per richiesta oppure multi-file con coda e archivio di output?]
- **FR-013**: Accesso [NEEDS CLARIFICATION: interfaccia pubblica senza autenticazione oppure accesso protetto (es. rete interna)?]

### Key Entities *(include if feature involves data)*

- **Upload**: rappresenta una richiesta di elaborazione, con attributi: nome file, dimensione, stato, esito, messaggio errore.
- **ProcessedArtifact**: rappresenta l'output disponibile (PDF elaborato oppure pacchetto compresso), con tipo e dimensione.
- **CompressionOption**: rappresenta la scelta di compressione (nessuna, ZIP, riduzione PDF) e i relativi parametri.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Gli utenti completano il flusso upload→download in < 2 minuti nel 95% dei casi.
- **SC-002**: Tasso di successo elaborazioni ≥ 98% per PDF validi ≤ 25 MB.
- **SC-003**: Per download con compressione, riduzione dimensionale ≥ 20% nel 80% dei casi (se compressione PDF) oppure archivio consegnato entro 5 s (se ZIP).
- **SC-004**: 0 file residui oltre 10 minuti dopo la consegna (verificabile con ispezione storage temporaneo).

### Assumptions

- Il servizio è esposto dietro reverse proxy esterno per HTTPS/HTTP/2 e limiti di banda.
- Il limite dimensionale predefinito è 25 MB, configurabile via variabile d'ambiente.
- I modelli CommonForms sono disponibili in cache locale; nessun download in runtime di produzione.
