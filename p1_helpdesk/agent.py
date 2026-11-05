import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from typing import Literal, TypedDict
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
MODEL = os.getenv("MODEL", "openai:gpt-5.4")


class Ordine(TypedDict):
    stato: str
    luogo: str
    consegna_prevista: str

class Errore(TypedDict):
    errore: str

ORDINI: dict[int, Ordine] = {
    1234: {"stato": "spedito", "luogo": "Milano", "consegna_prevista": "giovedì"},
    5678: {"stato": "in preparazione", "luogo": "magazzino", "consegna_prevista": "lunedì"},
    9012: {"stato": "consegnato", "luogo": "Napoli", "consegna_prevista": "già consegnato"},
}

TICKET: list[dict] = []

FAQ: dict[str, dict] = {
    "Resi": {
        "parole_chiave": ["reso", "resi", "restituire", "rimborso", "rimandare"],
        "risposta": "Puoi fare il reso entro 30 giorni dalla consegna dalla sezione 'I miei ordini'. Il rimborso arriva in 5-7 giorni lavorativi.",
    },
    "Acquisti": {
        "parole_chiave": ["acquistare", "comprare", "acquisto", "carrello"],
        "risposta": "Aggiungi il prodotto al carrello, poi clicca su 'Procedi al pagamento' e inserisci indirizzo e metodo di pagamento.",
    },
    "Spedizioni": {
        "parole_chiave": ["spedizione", "spedire", "consegna", "corriere", "tempi"],
        "risposta": "Le spedizioni in Italia arrivano in 2-4 giorni lavorativi. Sopra i 50 euro la spedizione è gratuita.",
    },
    "Vedere i propri ordini": {
        "parole_chiave": ["vedere", "storico", "i miei ordini", "dove trovo"],
        "risposta": "Trovi tutti i tuoi ordini nella sezione 'I miei ordini' del tuo profilo.",
    },
}

@tool
def cerca_faq(domanda: str) -> str:
    """Cerca nelle FAQ del negozio. Usalo quando l'utente chiede come funziona qualcosa del negozio. 
    Non usarlo se l'utente chiede di un ordine specifico(Dove si trova il mio ordine 1234?)questo va in stato_ordine , o se ti chiede per esempio(Il mio ordine è rotto) questo va in apri_ticket"""
    testo = domanda.lower()
    for titolo, faq in FAQ.items():
        if any(parola in testo for parola in faq["parole_chiave"]):
            return f"{titolo}: {faq['risposta']}"
    argomenti = ", ".join(FAQ)
    return f"Nessuna FAQ trovata per questa domanda. Argomenti disponibili: {argomenti}"


@tool
def stato_ordine(id_ordine: int) -> Ordine | Errore:
    """Controlla lo stato di un ordine tramite l'id.
    Usalo quando un utente chiede di controllare lo stato di un suo ordine. 
    Non devi usarlo quando l'utente dice(Il mio ordine è rotto) va in apri_ticket, oppure quando chiede come funziona qualcosa nel negozio che va invece in cerca_faq. 
    Non usarlo se l'utente non ti fornisce l'id, nel caso in cui non te lo dia chiediglielo. 
    Se il tool restituisce un errore, chiedere all'utente se id che ha scritto è corretto"""

    ordine = ORDINI.get(id_ordine)
    if ordine is None:
        return {"errore": f"Non esiste un ordine con id {id_ordine}"}
    return ordine

@tool
def apri_ticket(
    categoria: Literal["spedizione", "prodotto", "pagamento", "altro"],
    priorita: Literal["bassa", "media", "alta"],
    descrizione: str,
) -> str:
    """Apre un ticket di assistenza quando l'utente segnala un problema da risolvere
    (es. "Il prodotto che mi è arrivato è rotto", "Mi hanno addebitato due volte").
    Scegli la priorità così: alta se il prodotto è rotto o ci sono soldi addebitati per errore,
    media per ritardi o disservizi, bassa per tutto il resto.
    Non usarlo se l'utente chiede come funziona qualcosa del negozio: in quel caso usa cerca_faq.
    Non usarlo se l'utente vuole solo sapere dov'è un ordine: in quel caso usa stato_ordine.
    Se la descrizione del problema non è chiara, chiedi più dettagli all'utente prima di aprire il ticket.
    Dopo averlo aperto, comunica all'utente il numero del ticket."""
    numero = len(TICKET) + 1
    TICKET.append({
        "numero": numero,
        "categoria": categoria,
        "priorita": priorita,
        "descrizione": descrizione,
    })
    return f"Ticket #{numero} aperto (categoria: {categoria}, priorità: {priorita})."

agent = create_agent(
    model=MODEL,
    tools=[cerca_faq, stato_ordine, apri_ticket],
    checkpointer=InMemorySaver()
)

ordine = {"configurable": {"thread_id": "ordine"}}
r = agent.invoke({"messages": [{"role": "user", "content": "Dove si trova il mio ordine 1234"}]}, ordine)
print(r["messages"][-1].content)