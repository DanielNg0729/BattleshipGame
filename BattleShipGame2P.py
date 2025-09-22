import tkinter as tk
from tkinter import messagebox, simpledialog
import tkinter.font as tkFont

class BattleshipGUI:
    def __init__(self):
        self.board_size = 10
        self.root = tk.Tk()
        self.root.title("Battleship Game")
        self.root.geometry("800x900")
        self.root.configure(bg='#2c3e50')
        
        # Game state
        self.board = [[0 for j in range(self.board_size)] for i in range(self.board_size)]
        self.ships = {
            "Carrier": {"length": 5, "symbol": "C"},
            "Submarine": {"length": 3, "symbol": "S"}
        }
        self.ships_cells = {}
        self.ships_sunk = set()
        self.game_phase = "setup"  # "setup" or "playing"
        self.current_ship_index = 0
        self.ship_names = list(self.ships.keys())
        
        # GUI elements
        self.buttons = []
        self.info_label = None
        self.status_label = None
        
        self.setup_gui()
        self.start_ship_placement()
        
    def setup_gui(self):
        # Title
        title_font = tkFont.Font(family="Arial", size=20, weight="bold")
        title_label = tk.Label(self.root, text="🚢 BATTLESHIP 🚢", 
                              font=title_font, bg='#2c3e50', fg='white')
        title_label.pack(pady=10)
        
        # Info label for instructions
        self.info_label = tk.Label(self.root, text="", 
                                  font=("Arial", 12), bg='#2c3e50', fg='#ecf0f1',
                                  wraplength=700, justify='center')
        self.info_label.pack(pady=5)
        
        # Game board frame
        board_frame = tk.Frame(self.root, bg='#34495e', relief='raised', bd=2)
        board_frame.pack(pady=20, padx=20)
        
        # Create grid of buttons
        for i in range(self.board_size):
            button_row = []
            for j in range(self.board_size):
                btn = tk.Button(board_frame, text='~', width=4, height=2,
                               font=("Arial", 10, "bold"),
                               bg='#3498db', fg='white',
                               activebackground='#2980b9',
                               command=lambda r=i, c=j: self.cell_clicked(r, c))
                btn.grid(row=i, column=j, padx=1, pady=1)
                button_row.append(btn)
            self.buttons.append(button_row)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Ships remaining: 2", 
                                   font=("Arial", 12, "bold"), bg='#2c3e50', fg='#e74c3c')
        self.status_label.pack(pady=5)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=10)
        
        # Reset button
        reset_btn = tk.Button(control_frame, text="New Game", 
                            command=self.reset_game,
                            bg='#e74c3c', fg='white', font=("Arial", 10, "bold"),
                            padx=20, pady=5)
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        # Quit button
        quit_btn = tk.Button(control_frame, text="Quit", 
                           command=self.root.quit,
                           bg='#95a5a6', fg='white', font=("Arial", 10, "bold"),
                           padx=20, pady=5)
        quit_btn.pack(side=tk.LEFT, padx=10)
    
    def start_ship_placement(self):
        self.game_phase = "setup"
        self.current_ship_index = 0
        if self.current_ship_index < len(self.ship_names):
            ship_name = self.ship_names[self.current_ship_index]
            length = self.ships[ship_name]["length"]
            self.info_label.config(text=f"Place your {ship_name} (length: {length})\nClick on the starting position, ship will be placed horizontally")
    
    def cell_clicked(self, row, col):
        if self.game_phase == "setup":
            self.place_ship_at(row, col)
        elif self.game_phase == "playing":
            self.attack_cell(row, col)
    
    def place_ship_at(self, row, col):
        if self.current_ship_index >= len(self.ship_names):
            return
            
        ship_name = self.ship_names[self.current_ship_index]
        length = self.ships[ship_name]["length"]
        symbol = self.ships[ship_name]["symbol"]
        
        # Check if ship can be placed horizontally from this position
        if col + length > self.board_size:
            messagebox.showerror("Invalid Position", 
                               f"Cannot place {ship_name} here - goes off the board!")
            return
        
        # Check if positions are free
        for i in range(length):
            if self.board[row][col + i] != 0:
                messagebox.showerror("Invalid Position", 
                                   f"Cannot place {ship_name} here - position already occupied!")
                return
        
        # Place the ship (only in internal board, not visually during setup)
        positions = []
        for i in range(length):
            self.board[row][col + i] = symbol
            positions.append((row, col + i))
            # During setup, temporarily show ship placement with different color
            if symbol == "C":
                self.buttons[row][col + i].config(bg='#e74c3c', text='C')  # Red for Carrier
            else:
                self.buttons[row][col + i].config(bg='#f39c12', text='S')  # Orange for Submarine
        
        self.ships_cells[ship_name] = positions
        self.current_ship_index += 1
        
        # Check if all ships are placed
        if self.current_ship_index >= len(self.ship_names):
            # Hide all ships after placement
            self.hide_ships()
            self.game_phase = "playing"
            self.info_label.config(text="All ships placed and hidden! Give the game to your friend.\nYour friend should click on cells to attack.\nX = Hit, O = Miss")
            self.update_status()
        else:
            # Move to next ship
            next_ship = self.ship_names[self.current_ship_index]
            next_length = self.ships[next_ship]["length"]
            self.info_label.config(text=f"Place your {next_ship} (length: {next_length})\nClick on the starting position, ship will be placed horizontally")
    
    def hide_ships(self):
        """Hide all ships by resetting button appearance to water"""
        for i in range(self.board_size):
            for j in range(self.board_size):
                # Only reset cells that contain ships (not already attacked)
                if self.board[i][j] in ["C", "S"]:
                    self.buttons[i][j].config(bg='#3498db', text='~', fg='white')
    
    def attack_cell(self, row, col):
        # Check bounds
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return
        
        cell = self.board[row][col]
        button = self.buttons[row][col]
        
        # Check if already attacked
        if button.cget('text') in ['X', 'O']:
            messagebox.showinfo("Invalid Attack", "You already attacked this position!")
            return
        
        # Process attack
        if cell in ["C", "S"]:
            # Hit!
            button.config(bg='#c0392b', text='X', fg='white')
            self.board[row][col] = "X"
            
            # Check which ship was hit and if it's sunk
            for ship_name, cells in self.ships_cells.items():
                if (row, col) in cells:
                    cells.remove((row, col))
                    if not cells and ship_name not in self.ships_sunk:
                        self.ships_sunk.add(ship_name)
                        messagebox.showinfo("Ship Sunk!", f"You sunk the {ship_name}!")
                    break
            
            # Check win condition
            if self.all_ships_sunk():
                messagebox.showinfo("Victory!", "Congratulations! You sunk all ships!")
                self.game_phase = "finished"
                
        else:
            # Miss
            button.config(bg='#7f8c8d', text='O', fg='white')
            self.board[row][col] = "o"
        
        self.update_status()
    
    def all_ships_sunk(self):
        return all(len(cells) == 0 for cells in self.ships_cells.values())
    
    def update_status(self):
        ships_remaining = len([ship for ship, cells in self.ships_cells.items() 
                              if len(cells) > 0])
        self.status_label.config(text=f"Ships remaining: {ships_remaining}")
    
    def reset_game(self):
        # Reset game state
        self.board = [[0 for j in range(self.board_size)] for i in range(self.board_size)]
        self.ships_cells = {}
        self.ships_sunk = set()
        self.game_phase = "setup"
        self.current_ship_index = 0
        
        # Reset all buttons
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.buttons[i][j].config(bg='#3498db', text='~', fg='white')
        
        # Reset labels
        self.status_label.config(text="Ships remaining: 2")
        
        # Start ship placement again
        self.start_ship_placement()
    
    def run(self):
        self.root.mainloop()

def main():
    game = BattleshipGUI()
    game.run()

if __name__ == "__main__":
    main()