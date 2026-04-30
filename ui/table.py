"""
**************************************************************************

table.py is for:

the visual of our playing surface

**************************************************************************
"""

import tkinter as tk
from ui.widgets import StyledButton, StyledLabel
from ui.sprites import sprites


class TableScreen(tk.Frame):
    # Slots: 1(self), 2(master), 3(manager), 4(lobby_callback), 5(state), 6(username)
    def __init__(self, master, manager, lobby_callback, state, username):
        super().__init__(master, bg="#0b3d0b")
        self.master = master
        self.manager = manager
        self.lobby_callback = lobby_callback
        self.state = state
        self.username = username
        
        self.card_images = []
        self.build()
        

    def build(self):
        # ---------- TOP SECTION (POT DISPLAY) ----------
        top = tk.Frame(self, bg="#0b3d0b")
        top.pack(pady=10)

        self.pot_label = StyledLabel(top, f"Pot: ${self.state.pot}", size=16, bold=True)
        self.pot_label.pack(pady=10)

        # ---------- OPPONENT AREA ----------
        self.opponents_frame = tk.Frame(self, bg="#0b3d0b")
        self.opponents_frame.pack(pady=20)

        # ---------- COMMUNITY CARDS ----------
        self.community_frame = tk.Frame(self, bg="#0b3d0b")
        self.community_frame.pack(pady=20)

        # ---------- BOTTOM SECTION ----------
        bottom = tk.Frame(self, bg="#0b3d0b")
        bottom.pack(side="bottom", fill="x", pady=20)

        # Left side: player actions
        self.actions_frame = tk.Frame(bottom, bg="#0b3d0b")
        self.actions_frame.pack(side="left", padx=20)

        self.check_call_btn = StyledButton(self.actions_frame, "Check", self.check_call)
        self.check_call_btn.pack(pady=5)

        StyledButton(self.actions_frame, "Raise", self.raise_bet).pack(pady=5)
        StyledButton(self.actions_frame, "Fold", self.fold).pack(pady=5)

        # Center: player hand
        self.player_frame = tk.Frame(bottom, bg="#0b3d0b")
        self.player_frame.pack(side="left", expand=True)

        # Right side: menu options
        self.menu_frame = tk.Frame(bottom, bg="#0b3d0b")
        self.menu_frame.pack(side="right", padx=20)

        StyledButton(self.menu_frame, "Pause", self.pause).pack(pady=5)
        StyledButton(self.menu_frame, "Exit", self.exit_game).pack(pady=5)


    def render_opponents(self, opponents):
        # Clear previous opponent widgets
        for w in self.opponents_frame.winfo_children():
            w.destroy()

        #self.card_images.clear()

        # Render each opponent's hand
        for i, hand in enumerate(opponents):
            pair_frame = tk.Frame(self.opponents_frame, bg="#0b3d0b")
            pair_frame.grid(row=0, column=i, padx=40)

            for j, card in enumerate(hand):
                if getattr(card, 'is_face_up', False):
                    img = sprites.get_card_image(card)
                else:
                    img = sprites.get_card_back()

                if img:
                    # Resize image to fit UI
                    img = img.subsample(5, 5)
                    self.card_images.append(img)

                    label = tk.Label(pair_frame, image=img, bg="#0b3d0b")
                    label.image = img
                else:
                    # Fallback if image missing
                    label = tk.Label(pair_frame, text=str(card))

                label.grid(row=0, column=j, padx=2)


    def render_community(self, cards):
        # Clear previous cards
        for w in self.community_frame.winfo_children():
            w.destroy()

        for i, card in enumerate(cards):
            img = sprites.get_card_image(card)
            if img:
                img = img.subsample(5, 5)
                self.card_images.append(img)
                label = tk.Label(self.community_frame, image=img, bg="#0b3d0b")
                label.image = img
            else:
                label = tk.Label(self.community_frame, text=str(card))

            label.grid(row=0, column=i, padx=5)


    def render_player_hand(self, cards):
        # Clear previous hand
        for w in self.player_frame.winfo_children():
            w.destroy()

        self.player_card_labels = []

        if not hasattr(self, 'selected_discards') or self.state.phase != "draw":
            self.selected_discards = set()

        for i, card in enumerate(cards):
            img = sprites.get_card_image(card)
            if img:
                img = img.subsample(5, 5)
                self.card_images.append(img)
                bg_color = "red" if i in self.selected_discards else "#0b3d0b"
                label = tk.Label(self.player_frame, image=img, bg=bg_color, bd=2)
                label.image = img
            else:
                label = tk.Label(self.player_frame, text=str(card), bg="#0b3d0b", bd=2)

            label.grid(row=0, column=i, padx=5)

            label.bind("<Button-1>", lambda event, idx=i: self.toggle_discard(idx))
            self.player_card_labels.append(label)
    

    def toggle_discard(self, index):
        # Only allow selecting cards by clicking during the draw phase
        if self.state.phase != "draw":
            return

        if index in self.selected_discards:
            # Deselect the card
            self.selected_discards.remove(index)
            self.player_card_labels[index].config(bg="#0b3d0b") # Reset to table color
        else:
            # Limit discards to 3 (matching the rules in draw.py)
            if len(self.selected_discards) >= 3:
                print("You can only discard up to 3 cards.")
                return
                
            # Select the card
            self.selected_discards.add(index)
            self.player_card_labels[index].config(bg="red")

        if len(self.selected_discards) > 0:
            self.check_call_btn.config(text="Discard Selected")
        else:
            self.check_call_btn.config(text="Stand Pat (Keep All)")


    def update_pot(self, amount):
        # Updates pot value display
        self.pot_amount = amount
        self.pot_label.config(text=f"Pot: ${amount}")


    def update_check_call(self, to_call):
        # Dynamically switches button label based on game state
        if to_call > 0:
            self.check_call_btn.config(text="Call")
        else:
            self.check_call_btn.config(text="Check")


    def check_call(self):
        self.manager.process_player_action({
            "player_name": self.state.players[0].name,
            "action": "call",
             "amount": 0 
             })


    def raise_bet(self):
        self.manager.process_player_action({
            "player_name": self.state.players[0].name,
            "action": "raise",
             "amount": 50 })        # might need to make this a variable later ***********


    def fold(self):
        self.manager.process_player_action({
            "player_name": self.state.players[0].name,
            "action": "fold", 
            "amount": 0
            })


    def pause(self):
        self.master.process_player_action({
            "action": "pause", 
            "player_name": self.username
            })


    def exit_game(self):
        # Switch back to the lobby screen
        self.lobby_callback()


    """def test_layout(self):
        # Temporary method to populate UI with sample data
        from core.cards import Deck

        deck = Deck()
        deck.shuffle()

        opponents = [deck.draw(2), deck.draw(2), deck.draw(2)]
        self.render_opponents(opponents)

        self.render_community(deck.draw(5))
        self.render_player_hand(deck.draw(2))

        self.update_pot(150)"""
