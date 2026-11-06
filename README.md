# Progetti settimanali - HelpDesk Agent

Un unico agente che cresce settimana dopo settimana, attraversando tutto il ciclo
Build -> Test -> Deploy -> Monitor, esattamente come i domini dell'esame.

## Installazione

Requisiti: Python 3.11 o superiore.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # poi inserisci le tue chiavi in .env
```

## Avvio

```bash
cd p1_helpdesk
python main.py
```

Scrivi `esci` per terminare la chat.

## P1 - HelpDesk v1 (settimana 1, ~3 ore)  -> cartella p1_helpdesk
- `create_agent` con 3 tool: `cerca_faq(domanda)` (cerca in un dizionario o in un file .md di FAQ),
  `stato_ordine(id_ordine)` (finto database), `apri_ticket(categoria, priorita, descrizione)`
- memoria per conversazione (checkpointer + thread_id) e un ciclo di chat da terminale
- output strutturato `TicketInfo` quando l'utente chiede di aprire un ticket
- tracing LangSmith attivo da subito: guarda ogni conversazione nella UI
- Fatto quando: 5 conversazioni di prova funzionano e vedi le tracce in LangSmith

## P2 - HelpDesk v2 + Deep Agent (settimana 2, ~4 ore)
- HumanInTheLoopMiddleware su un nuovo tool `rimborsa(id_ordine, importo)`
- SummarizationMiddleware per le chat lunghe; prova un middleware custom con `@before_model`
  che conta le chiamate al modello
- un deep agent `analista` che legge una cartella di ticket (FilesystemBackend), pianifica con la
  todo list e scrive `report_settimanale.md`, con un subagente `critic` che lo rilegge
- Fatto quando: un rimborso si ferma in attesa di approvazione e il report viene generato

## P3 - Suite di valutazione (settimana 3, ~4 ore)
- dataset LangSmith di 20 esempi (domande FAQ, ordini, ticket, casi limite)
- evaluator: categoria corretta (codice), correttezza con LLM-as-judge (openevals),
  traiettoria (agentevals, mode superset)
- due esperimenti: prompt v1 contro prompt v2, confrontati nella UI (anche pairwise)
- Fatto quando: sai dire con i numeri quale versione e' migliore e perche'

## P4 - Deploy (settimana 4, ~4 ore)
- `langgraph.json` con due grafi (helpdesk e analista), `langgraph dev`, prova in Studio
- client con LangGraph SDK: thread, run in streaming, lettura dello stato del thread
- due assistant dallo stesso grafo con configurazioni diverse (es. modello o tono)
- se il tuo piano LangSmith lo consente: `langgraph deploy` su LangSmith Cloud e un cron job
- Fatto quando: un client esterno parla con l'agente via API e ritrova la conversazione

## P5 - Monitoraggio (settimana 5, ~4 ore)
- script che genera 50 conversazioni con metadati (user_id, piano, versione) e feedback finti
- dashboard personalizzato: costo, latenza P50/P99, tasso di errore, feedback medio
- online evaluator (LLM-as-judge) con campionamento al 20%
- regola di automazione: tracce con feedback negativo -> annotation queue -> dataset del P3
- Fatto quando: sai rispondere a "quale utente costa di piu'?" e "dove sbaglia l'agente?" dalla UI
