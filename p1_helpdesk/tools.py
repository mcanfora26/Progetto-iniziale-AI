from typing import Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from pydantic import BaseModel, Field

from config import MODEL
from dati import FAQ, ORDINI, TICKET, Errore, Ordine

class TicketInfo(BaseModel):
    """Classificazione di un ticket di assistenza."""

    categoria: Literal["spedizione", "prodotto", "pagamento", "altro"] = Field(
        description="Area a cui appartiene il problema"
    )
    priorita: Literal["bassa", "media", "alta"] = Field(
        description="alta: prodotto rotto o soldi addebitati per errore; "
                    "media: ritardi o disservizi; bassa: tutto il resto"
    )
    riassunto: str = Field(description="Il problema in una frase breve")

class SceltaFAQ(BaseModel):
    """FAQ più pertinente alla domanda di un cliente."""

    argomento: Literal["Resi", "Acquisti", "Spedizioni", "Vedere i propri ordini", "nessuna"] = Field(
        description="La FAQ che risponde alla domanda. "
                    "Usa 'nessuna' se nessuna FAQ è pertinente."
    )


ARGOMENTI_FAQ = "\n".join(f"- {titolo}: {faq['copre']}" for titolo, faq in FAQ.items())

classificatore = create_agent(
    model=MODEL,
    tools=[],
    system_prompt="Classifica il problema descritto dal cliente di un negozio online.",
    response_format=ToolStrategy(TicketInfo),
)


classificatore_faq = create_agent(
    model=MODEL,
    tools=[],
    system_prompt=(
        "Sei il classificatore delle FAQ di un negozio online. "
        "Data la domanda di un cliente, scegli la FAQ che risponde. "
        "Se nessuna è pertinente, rispondi 'nessuna'.\n\n"
        f"FAQ disponibili:\n{ARGOMENTI_FAQ}"
    ),
    response_format=ToolStrategy(SceltaFAQ),
)

@tool
def cerca_faq(domanda: str) -> str:
    """Cerca nelle FAQ del negozio. Usalo quando l'utente chiede come funziona qualcosa del negozio
    (resi, acquisti, spedizioni, dove vedere i propri ordini).
    Non usarlo se l'utente chiede di un ordine specifico (es. "Dove si trova il mio ordine 1234?"): usa stato_ordine.
    Non usarlo se l'utente segnala un problema (es. "Il mio ordine è arrivato rotto"): usa apri_ticket."""
    if not domanda.strip():
        return "Errore: la domanda è vuota."

    risultato = classificatore_faq.invoke({"messages": [{"role": "user", "content": domanda}]})
    argomento = risultato["structured_response"].argomento

    if argomento == "nessuna":
        return f"Nessuna FAQ trovata per questa domanda. Argomenti disponibili: {', '.join(FAQ)}"
    return f"{argomento}: {FAQ[argomento]['risposta']}"


@tool
def stato_ordine(id_ordine: int) -> Ordine | Errore:
    """Controlla lo stato di un ordine tramite il suo id. Richiede l'id dell'ordine.
    Usalo quando l'utente chiede dove si trova o a che punto è un suo ordine.
    Non usarlo se l'utente segnala un problema (es. "Il mio ordine è arrivato rotto"): usa apri_ticket.
    Non usarlo se l'utente chiede come funziona qualcosa del negozio: usa cerca_faq."""

    if id_ordine <= 0:
        return {"errore": f"L'id {id_ordine} non è valido: gli id degli ordini sono numeri positivi."}

    ordine = ORDINI.get(id_ordine)
    if ordine is None:
        return {"errore": f"Non esiste un ordine con id {id_ordine}"}
    return ordine

@tool
def apri_ticket(descrizione: str) -> str:
    """Apre un ticket di assistenza quando l'utente segnala un problema da risolvere
    (es. "Il prodotto che mi è arrivato è rotto", "Mi hanno addebitato due volte").
    Nella descrizione riporta il problema con le parole dell'utente e tutti i dettagli utili.
    Non usarlo se l'utente chiede come funziona qualcosa del negozio: usa cerca_faq.
    Non usarlo se l'utente vuole solo sapere dov'è un ordine: usa stato_ordine."""

    descrizione = descrizione.strip()
    if not descrizione:
        return "Errore: la descrizione del problema è vuota. Chiedi all'utente di descrivere il problema."
    
    risultato = classificatore.invoke({"messages": [{"role": "user", "content": descrizione}]})
    info: TicketInfo = risultato["structured_response"]
    numero = len(TICKET) + 1
    TICKET.append({"numero": numero, **info.model_dump(), "descrizione": descrizione})
    return f"Ticket #{numero} aperto. {info.model_dump_json()}"
