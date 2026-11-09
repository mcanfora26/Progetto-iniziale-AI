from typing import TypedDict

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
RIMBORSI: list[dict] = []

FAQ: dict[str, dict] = {
    "Resi": {
        "copre": "resi, restituzioni, rimborsi",
        "risposta": "Puoi fare il reso entro 30 giorni dalla consegna dalla sezione 'I miei ordini'. Il rimborso arriva in 5-7 giorni lavorativi.",
    },
    "Acquisti": {
        "copre": "come comprare, uso del carrello, procedura di pagamento",
        "risposta": "Aggiungi il prodotto al carrello, poi clicca su 'Procedi al pagamento' e inserisci indirizzo e metodo di pagamento.",
    },
    "Spedizioni": {
        "copre": "tempi e costi di spedizione in generale (non lo stato di un ordine specifico)",
        "risposta": "Le spedizioni in Italia arrivano in 2-4 giorni lavorativi. Sopra i 50 euro la spedizione è gratuita.",
    },
    "Vedere i propri ordini": {
        "copre": "dove trovare lo storico e l'elenco dei propri ordini",
        "risposta": "Trovi tutti i tuoi ordini nella sezione 'I miei ordini' del tuo profilo.",
    },
}
