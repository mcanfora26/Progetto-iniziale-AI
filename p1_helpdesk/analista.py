from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from config import MODEL

CARTELLA_ANALISI = Path(__file__).parent / "analisi"

CRITIC = {
    "name": "critic",
    "description": "Rilegge /report_settimanale.md e restituisce le correzioni da fare. "
                   "Usalo dopo aver scritto il report.",
    "system_prompt": """Sei un revisore. Leggi /report_settimanale.md e confrontalo con i ticket in /ticket/.
Controlla che i conteggi siano giusti, che nessun ticket manchi e che non ci siano informazioni inventate.
Non modificare nessun file: rispondi solo con un elenco puntato di correzioni, oppure 'OK' se il report va bene.""",
}

SYSTEM_PROMPT = """Sei un analista dell'assistenza clienti di un negozio online.
Devi leggere tutti i ticket in /ticket/ e scrivere /report_settimanale.md.

Procedi così:
1. Prima di iniziare pianifica il lavoro con write_todos e aggiorna i todo man mano.
2. Leggi ogni ticket.
3. Scrivi il report con: ticket per categoria e per priorità, problemi ricorrenti,
   ticket urgenti da gestire subito, 2-3 suggerimenti.
4. Fai rileggere il report al subagente critic e applica le sue correzioni con edit_file.
Usa solo informazioni presenti nei ticket."""

agent = create_deep_agent(
    model=MODEL,
    system_prompt=SYSTEM_PROMPT,
    subagents=[CRITIC],
    backend=FilesystemBackend(root_dir=CARTELLA_ANALISI, virtual_mode=True),
)


if __name__ == "__main__":
    risultato = agent.invoke(
        {"messages": [{"role": "user", "content": "Prepara il report settimanale dei ticket."}]}
    )
    for todo in risultato.get("todos", []):
        print(f"[{todo['status']}] {todo['content']}")
    print(risultato["messages"][-1].content)