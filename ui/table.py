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
        
        # Dynamic fix for the cards going off screen
        self.card_scale = 1.0
        self.base_card_width = 100
        self.base_card_height = 150

        self.bind("<Configure>", lambda e: self.refresh_ui())


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
        for w in self.opponents_frame.winfo_children():
            w.destroy()

        is_stud = (self.state.variant_name == "7-Card Stud")

        for i, hand in enumerate(opponents):
            pair_frame = tk.Frame(self.opponents_frame, bg="#0b3d0b")

            if is_stud:
                pair_frame.grid(row=i, column=0, pady=10)
            else:
                pair_frame.grid(row=0, column=i, padx=40)

            for j, card in enumerate(hand):
                img = sprites.get_card_image(card) if getattr(card, 'is_face_up', False) else sprites.get_card_back()

                if img:
                    img = self.scale_image(img)

                    # Shrink opponent cards to fit in Stud games
                    if is_stud:
                        img = img.subsample(2, 2)

                    self.card_images.append(img)
                    label = tk.Label(pair_frame, image=img, bg="#0b3d0b")
                    label.image = img
                else:
                    label = tk.Label(pair_frame, text=str(card))

                label.grid(row=0, column=j, padx=2)


    def render_community(self, cards):
        # Clear previous cards
        for w in self.community_frame.winfo_children():
            w.destroy()

        for i, card in enumerate(cards):
            img = sprites.get_card_image(card)
            if img:
                img = self.scale_image(img)
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

        #Added variation to the scaling for stud.
        is_stud = (self.state.variant_name == "7-Card Stud")

        if is_stud:
            # Scale so 7 cards fit exactly in the available width
            window_width = self.winfo_width()
            card_width = 100 
            spacing = 10

            needed = 7 * (card_width + spacing)

            # scale = how much we need to shrink to fit exactly
            scale = window_width / needed

            # Limit scale so cards stay readable
            self.card_scale = max(0.7, min(scale, 1.0))
        else:
            # Normal dynamic scaling for other variants
            self.card_scale = self.compute_tk_scale(len(cards))


        if not hasattr(self, 'selected_discards') or self.state.phase != "draw":
            self.selected_discards = set()

        for i, card in enumerate(cards):
            img = sprites.get_card_image(card)
            if img:
                img = self.scale_image(img)
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


    # Moved refresh UI to this file to handle scaling
    def refresh_ui(self):
        # Player hand
        player = self.state.players[0]
        self.card_scale = self.compute_tk_scale(len(player.hand.cards))
        self.render_player_hand(player.hand.cards)

        # Community cards
        self.card_scale = self.compute_tk_scale(len(self.state.community_cards))
        self.render_community(self.state.community_cards)

        # Opponents
        opponents = [p.hand.cards for p in self.state.players[1:]]
        max_cards = max((len(h) for h in opponents), default=0)
        self.card_scale = self.compute_tk_scale(max_cards)
        self.render_opponents(opponents)


    # Helper function that finds how small cards need to be
    def compute_tk_scale(self, num_cards):
        """
        I've come to learn that TKinter only scales with integers.
        This is a helper solution to scaling within this framework.
        """

        window_width = self.winfo_width()
        card_width = 10
        spacing = 20

        needed = num_cards * (card_width + spacing)

        if needed <= window_width:
            return 1.0

        scale = window_width / needed

        # Snap to Tkinter-friendly steps
        if scale >= 0.75:
            return 0.75
        elif scale >= 0.5:
            return 0.5
        elif scale >= 0.33:
            return 0.33
        else:
            return 0.25


    # Helper function that scales the card images
    def scale_image(self, img):

        is_stud = (self.state.variant_name == "7-Card Stud")

        if is_stud:
            # Smaller base size for 7-card stud
            base = img.subsample(10, 10)
        else:
            # Normal size for other games
            base = img.subsample(6, 6)

        scale = self.card_scale

        # Standard scaling for other games
        if scale == 1.0:
            return base
        elif scale == 0.75:
            return base.subsample(4, 3)
        elif scale == 0.5:
            return base.subsample(2, 2)
        elif scale == 0.33:
            return base.subsample(3, 3)
        else:  # 0.25
            return base.subsample(4, 4)


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
