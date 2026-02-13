# ♠️ Python Poker Trainer (GTO & Math)

Un simulatore interattivo di Texas Hold'em No Limit da riga di comando (CLI) scritto in Python. Questo tool è progettato per allenare i giocatori sulle dinamiche Pre-Flop (basate su range GTO/Tabellari) e sulla matematica Post-Flop (Pot Odds, Equity, Regola del 4 e del 2).

---

## 🚀 Funzionalità

- Simulazione Tavolo: Genera casualmente tavoli da 2 a 8 giocatori con posizioni reali (BTN, SB, BB, UTG, CO, ecc.).

- Gestione Stack: Simula stack Deep (>50BB), Medium e Short (<20BB) modificando la strategia suggerita.

- Trainer Pre-Flop:

  - Analizza la tua mano iniziale e la tua posizione.

  - Ti chiede di scegliere un'azione (Fold, Call, Raise).

  - Fornisce feedback immediato basato su range ottimali (Deep vs Short stack).

- Trainer Post-Flop:

  - Simula Flop, Turn e River.

  - Genera puntate avversarie realistiche (C-bet, Overbet, All-in).

  - Ti allena a contare gli Outs manualmente.

  - Calcola automaticamente Equity (Regola del 4/2) vs Pot Odds.

  -Ti dice se il tuo Call/Fold era matematicamente corretto (+EV).

- Analizzatore Punti: Riconosce automaticamente il punto che hai in mano (es. "Doppia Coppia", "Progetto di Colore") per aiutarti nella lettura del board.

- Valuta Reale: Mostra le puntate sia in Big Blind (BB) che in Dollari ($) per maggior realismo.
