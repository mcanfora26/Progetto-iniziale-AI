import uuid

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from config import MODEL
from tools import apri_ticket, cerca_faq, stato_ordine


SYSTEM_PROMPT = """Sei l'assistente clienti di un negozio online. Rispondi in italiano, in modo cortese e conciso.

Ti occupi di: domande su come funziona il negozio, stato degli ordini, segnalazione di problemi.
Se la richiesta non riguarda il negozio, spiega gentilmente che puoi aiutare solo su questi temi.

Regole:
- Le informazioni su ordini e policy del negozio devono venire solo dai tool: non inventarle mai.
- Per controllare un ordine serve il suo id: se l'utente non lo fornisce, chiediglielo.
- Se stato_ordine restituisce un errore, chiedi all'utente di verificare che l'id sia corretto.
- Prima di aprire un ticket, assicurati che il problema sia chiaro: se non lo è, chiedi più dettagli.
- Dopo aver aperto un ticket, comunica all'utente il numero del ticket."""

agent = create_agent(
    model=MODEL,
    tools=[cerca_faq, stato_ordine, apri_ticket],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver()
)


def chat():
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    print("HelpDesk pronto. Scrivi 'esci' per terminare.\n")
    while True:
        try:
            testo = input("Tu: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCiao!")
            break
        if not testo:
            continue
        if testo.lower() in {"esci", "exit", "quit"}:
            print("Ciao!")
            break
        risultato = agent.invoke({"messages": [{"role": "user", "content": testo}]}, config)
        print(f"HelpDesk: {risultato['messages'][-1].content}\n")


if __name__ == "__main__":
    chat()