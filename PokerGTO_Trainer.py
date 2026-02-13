import random
from collections import Counter

class PokerTrainerUltimate:
    def __init__(self):
        self.suits = ['♥', '♦', '♣', '♠']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.val_map = {r: i for i, r in enumerate(self.ranks, 2)}
        self.bb_value_usd = 2.0 # 1 BB = $2
        self.reset_deck()

    def reset_deck(self):
        self.deck = [r + s for r in self.ranks for s in self.suits]
        random.shuffle(self.deck)

    def draw(self, num=1):
        cards = []
        for _ in range(num):
            if self.deck: cards.append(self.deck.pop())
        return cards

    def fmt(self, bb_amount):
        """Formatta in Dollari e BB"""
        usd = bb_amount * self.bb_value_usd
        return f"${usd:.0f} ({bb_amount:.1f} BB)"

    # --- ANALIZZATORE PUNTO (FLOP/TURN/RIVER) ---
    def evaluate_hand(self, hole_cards, board):
        cards = hole_cards + board
        if not cards: return ""
        
        values = sorted([self.val_map[c[0]] for c in cards], reverse=True)
        suits = [c[1] for c in cards]
        counts = Counter(values)
        suit_counts = Counter(suits)
        
        message = ""
        is_strong = False

        # 1. Check Colore
        for s, count in suit_counts.items():
            if count >= 5: return f"💎 COLORE a {s}!"
            elif count == 4 and len(board) < 5: message += f" [Progetto Colore a {s}]"

        # 2. Check Scala (Semplificato)
        unique_vals = sorted(list(set(values)))
        consecutive = 0
        for i in range(len(unique_vals) - 1):
            if unique_vals[i+1] == unique_vals[i] + 1: consecutive += 1
            else: consecutive = 0
            if consecutive >= 4: return "📏 SCALA!"
        
        # 3. Check Coppie/Tris
        pair_counts = Counter(counts.values())
        if 4 in counts.values(): return "💣 POKER!"
        if 3 in counts.values() and 2 in counts.values(): return "🏠 FULL HOUSE!"
        if 3 in counts.values(): return "🔥 TRIS!"
        if pair_counts[2] >= 2: return "✨ DOPPIA COPPIA"
        if pair_counts[2] == 1:
            val = [k for k,v in counts.items() if v == 2][0]
            r_char = self.ranks[val-2]
            return f"🔸 COPPIA DI {r_char}" + message
            
        return "🔹 Carta Alta" + message

    # --- LOGICA STRATEGIA PRE-FLOP (REINSERITA) ---
    def check_preflop_strategy(self, hand_fmt, position, stack, action):
        """Restituisce feedback sulla giocata Pre-Flop"""
        is_short = stack < 20
        pos_type = "Late" if any(x in position for x in ["BTN", "CO", "SB"]) else "Early"
        advice = "Fold"
        reason = ""

        # Parsing mano
        is_pair = len(hand_fmt) == 2
        is_suited = 's' in hand_fmt
        val1 = self.val_map[hand_fmt[0]]
        
        # --- REGOLE GENERALI (Basate sul tuo PDF) ---
        if is_short:
            # Short Stack Strategy (Push/Fold)
            if is_pair or (val1 >= 13) or (val1 >= 10 and is_suited):
                advice = "Raise/All-in"
                reason = "Sei Short Stack (<20BB): Aggredisci con carte alte o coppie!"
            else:
                advice = "Fold"
        else:
            # Deep Stack Strategy
            if pos_type == "Early": # UTG, MP
                if is_pair and val1 >= 8: advice = "Raise" # 88+
                elif hand_fmt in ["AKs", "AQs", "AKo", "AQo"]: advice = "Raise"
                elif is_pair: advice = "Fold (o Set Mining se cheap)"
                else: advice = "Fold"
                reason = "In Early Position gioca solo mani molto forti (88+, AQ+)."
            else: # Late (BTN, CO)
                if is_pair: advice = "Raise" # Tutte le coppie
                elif is_suited and val1 >= 10: advice = "Raise" # Broadways suited
                elif is_suited and val1 >= 5 and (self.val_map[hand_fmt[1]] == val1 - 1): advice = "Raise" # Suited Connectors
                elif val1 >= 12: advice = "Raise" # QJ+
                else: advice = "Fold"
                reason = "In Late Position puoi rubare i bui con un range ampio."

        print(f"\n🧠 TRAINER FEEDBACK:")
        
        # Valutazione Azione Utente
        good_move = False
        if "Raise" in advice and action == 'raise': good_move = True
        elif "Fold" in advice and action == 'fold': good_move = True
        elif "Call" in advice and action == 'call': good_move = True
        
        # Eccezioni (es. Foldare AA è sempre errore)
        if hand_fmt in ["AA", "KK", "QQ", "AKs"] and action == 'fold':
            print(f"❌ ERRORE GRAVE! Hai foldato una mano Premium ({hand_fmt}).")
        elif good_move:
            print(f"✅ OTTIMO! La strategia suggerisce: {advice}")
        else:
            print(f"⚠️ ATTENZIONE. Con {hand_fmt} in {position}, meglio: {advice}.")
            print(f"   Motivo: {reason}")

    # --- SETUP UTILS ---
    def setup_table(self):
        self.n_players = random.randint(2, 8)
        seats = ["BTN", "SB", "BB", "CO", "UTG", "MP", "HJ", "UTG+1"]
        self.hero_position = seats[random.randint(0, min(self.n_players-1, len(seats)-1))]
        return self.n_players, self.hero_position

    def get_hand_strength_fmt(self, hand):
        c1, c2 = hand[0], hand[1]
        r1, r2 = c1[0], c2[0]
        s1, s2 = c1[1], c2[1]
        if self.val_map[r1] < self.val_map[r2]: r1, r2 = r2, r1; s1, s2 = s2, s1   
        if r1 == r2: return r1 + r2
        if s1 == s2: return r1 + r2 + 's'
        return r1 + r2 + 'o'

    def get_villain_bet(self, pot, stack, situation="preflop"):
        if situation == "preflop":
            options = [1.0, 2.0, 2.5, 3.0, 4.0, stack]
            return random.choice([o for o in options if o <= stack])
        else:
            pct = random.choice([0.33, 0.50, 0.66, 0.75, 1.0])
            return min(round(pot * pct, 1), stack)

    def calculate_pot_odds(self, to_call, pot_total):
        if to_call <= 0: return 0.0
        return (to_call / (pot_total + to_call)) * 100

    # --- MENU AZIONI ---
    def get_user_action(self, current_bet, pot, stack, street):
        print(f"\n--- TOCCA A TE ({street}) ---")
        print(f"💰 Piatto: {self.fmt(pot)}")
        if current_bet > 0: print(f"💸 Devi chiamare: {self.fmt(current_bet)}")
        else: print(f"✅ Nessuna puntata (Check).")

        while True:
            options = "(F)old, (C)heck/Call, (R)aise"
            choice = input(f"Scegli azione [{options}]: ").lower().strip()
            
            if choice == 'f': return 'fold', 0
            if choice == 'c': return 'call', min(current_bet, stack)
            if choice == 'r':
                print("\n   >>> RAISE MENU <<<")
                print(f"   1. Min-Raise ({self.fmt(current_bet*2 if current_bet>0 else 2)})")
                print(f"   2. Mezzo Piatto ({self.fmt(pot*0.5)})")
                print(f"   3. Piatto Intero ({self.fmt(pot)})")
                print(f"   4. All-In ({self.fmt(stack)})")
                try:
                    r = input("   Quanto rilanci? ")
                    if r == '1': amt = current_bet * 2 if current_bet > 0 else 2
                    elif r == '2': amt = pot * 0.5
                    elif r == '3': amt = pot
                    elif r == '4': amt = stack
                    else: continue
                    return 'raise', min(max(amt, 2), stack)
                except: continue
            print("Scelta non valida.")

    def analyze_postflop(self, action, user_outs, pot_total, bet_faced, street):
        multiplier = 4 if street == "FLOP" else 2
        equity = user_outs * multiplier
        if user_outs > 8 and street == "FLOP": equity -= 1
        if user_outs > 8 and street == "TURN": equity += 1
        
        odds = self.calculate_pot_odds(bet_faced, pot_total) if bet_faced > 0 else 0

        print(f"\n📊 REPORT ANALISI {street}:")
        print(f"   Equity stimata: {equity}%")
        if bet_faced > 0:
            print(f"   Pot Odds Reali: {odds:.1f}%")
            if action == 'fold' and equity >= odds: print(f"❌ FOLD TROPPO TIMIDO! Avevi le odds.")
            elif action == 'call' and equity < odds:
                diff = odds - equity
                if diff < 10: print("⚠️ CALL MARGINALE (Richiede Implied Odds)")
                else: print("❌ CALL ERRATO (-EV)")
            elif action == 'call': print("✅ CALL CORRETTO (+EV)")

    # --- MOTORE DI GIOCO PRINCIPALE ---
    def play_hand(self):
        self.reset_deck()
        self.setup_table()
        stack = random.randint(15, 100)
        pot = 1.5
        stack -= 1.0 
        
        hero_hand = self.draw(2)
        hand_fmt = self.get_hand_strength_fmt(hero_hand)
        
        print("\n" + "="*60)
        print(f"🃏 {self.n_players} Player | TU SEI: {self.hero_position}")
        print(f"💰 STACK: {self.fmt(stack)}")
        print(f"🂡 MANO: {hero_hand} [{hand_fmt}]")
        
        # PRE-FLOP
        if hand_fmt[0] == hand_fmt[1]: print(f"💡 Info: Coppia servita!")
        
        opp_bet = self.get_villain_bet(pot, stack) if random.random() > 0.5 else 0
        if opp_bet > 0: 
            print(f"⚠️ AVVERSARIO RILANCIA: {self.fmt(opp_bet)}")
            pot += opp_bet
        else: print("ℹ️ Piatto limpato.")
            
        action, amt = self.get_user_action(opp_bet, pot, stack, "PRE-FLOP")
        
        # --- QUI C'È IL TRAINER PRE-FLOP REINSERITO ---
        self.check_preflop_strategy(hand_fmt, self.hero_position, stack, action)
        # ----------------------------------------------

        if action == 'fold': return
        if action == 'call': stack -= amt; pot += amt
        elif action == 'raise': stack -= amt; pot += amt * 2

        # FLOP
        board = self.draw(3)
        print(f"\n🎴 FLOP: {board}")
        print(f"👀 PUNTO: {self.evaluate_hand(hero_hand, board)}")

        opp_bet = self.get_villain_bet(pot, stack, "post") if random.random() > 0.4 else 0
        if opp_bet > 0: print(f"⚠️ OPPONENT BET: {self.fmt(opp_bet)}")
        else: print("ℹ️ Check.")

        try: user_outs = int(input("👀 Quanti OUTS hai? "))
        except: user_outs = 0
        
        action, amt = self.get_user_action(opp_bet, pot + opp_bet, stack, "FLOP")
        self.analyze_postflop(action, user_outs, pot + opp_bet, opp_bet, "FLOP")
        if action == 'fold': return

        pot += opp_bet
        if action == 'call': stack -= amt; pot += amt
        elif action == 'raise': stack -= amt; pot += amt * 2

        # TURN
        input("\nPremi [Invio] per il TURN...")
        board += self.draw(1)
        print(f"\n🎴 TURN: {board}")
        print(f"👀 PUNTO: {self.evaluate_hand(hero_hand, board)}")
        
        opp_bet = self.get_villain_bet(pot, stack, "post") if random.random() > 0.5 else 0
        if opp_bet > 0: print(f"⚠️ OPPONENT BET: {self.fmt(opp_bet)}")
        
        try: user_outs = int(input("👀 Outs al Turn? "))
        except: user_outs = 0
        
        action, amt = self.get_user_action(opp_bet, pot + opp_bet, stack, "TURN")
        self.analyze_postflop(action, user_outs, pot + opp_bet, opp_bet, "TURN")
        
        if action == 'fold':
            # Se foldi al Turn, mostriamo comunque il river per curiosità
            print(f"\n💤 Hai foldato. Vediamo cosa sarebbe uscito...")
            river = self.draw(1)
            print(f"🎴 RIVER FANTASMA: {board + river}")
            return

        pot += opp_bet
        if action == 'call': stack -= amt; pot += amt
        elif action == 'raise': stack -= amt; pot += amt * 2

        # --- RIVER (NUOVO!) ---
        input("\nPremi [Invio] per il RIVER...")
        board += self.draw(1)
        print(f"\n🎴 RIVER: {board}")
        
        final_point = self.evaluate_hand(hero_hand, board)
        print(f"🏁 PUNTO FINALE: {final_point}")
        
        print("\n🎉 Mano conclusa allo Showdown!")

if __name__ == "__main__":
    game = PokerTrainerUltimate()
    while True:
        game.play_hand()
        if input("\nAltra mano? (Invio/q): ") == 'q': break