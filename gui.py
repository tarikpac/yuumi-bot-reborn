"""
Yuumi Bot GUI
A graphical interface for controlling the Yuumi Bot.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import sys
import io
from contextlib import redirect_stdout, redirect_stderr


class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Yuumi Bot Controller")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Configure dark theme colors
        self.bg_color = "#1a1a2e"
        self.fg_color = "#eaeaea"
        self.accent_color = "#4a4e69"
        self.button_color = "#7b2cbf"
        self.button_hover = "#9d4edd"
        self.success_color = "#2ecc71"
        self.danger_color = "#e74c3c"
        
        self.root.configure(bg=self.bg_color)
        
        # Bot thread reference
        self.bot_thread = None
        self.bot_running = False
        self.stop_event = threading.Event()
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Title
        title_label = tk.Label(
            self.root,
            text="🐱 Yuumi Bot Controller",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        title_label.pack(pady=15)
        
        # Options Frame
        options_frame = tk.Frame(self.root, bg=self.bg_color)
        options_frame.pack(pady=10, padx=20, fill="x")
        
        # Game Mode Selection
        mode_label = tk.Label(
            options_frame,
            text="Modo de Operação:",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.fg_color
        )
        mode_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.mode_var = tk.StringVar(value="autoqueue")
        
        mode_frame = tk.Frame(options_frame, bg=self.bg_color)
        mode_frame.grid(row=0, column=1, sticky="w", padx=10)
        
        autoqueue_radio = tk.Radiobutton(
            mode_frame,
            text="Somente Auto-Fila",
            variable=self.mode_var,
            value="autoqueue",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.accent_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        autoqueue_radio.pack(side="left", padx=5)
        
        yuumi_radio = tk.Radiobutton(
            mode_frame,
            text="Yuumi In-Game Completo",
            variable=self.mode_var,
            value="yuumi_full",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.accent_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        yuumi_radio.pack(side="left", padx=5)
        
        # Queue Type Selection
        queue_label = tk.Label(
            options_frame,
            text="Tipo de Fila:",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.fg_color
        )
        queue_label.grid(row=1, column=0, sticky="w", pady=10)
        
        self.queue_var = tk.StringVar(value="DRAFT_PICK")
        queue_options = [
            ("Draft Pick", "DRAFT_PICK"),
            ("Intermediate Bot", "INTERMEDIATE"),
            ("Beginner Bot", "BEGINNER"),
            ("Intro Bot", "INTRO"),
            ("Quick Play", "QUICK_PLAY"),
        ]
        
        queue_combo = ttk.Combobox(
            options_frame,
            textvariable=self.queue_var,
            values=[opt[0] for opt in queue_options],
            state="readonly",
            width=25
        )
        queue_combo.grid(row=1, column=1, sticky="w", padx=10)
        queue_combo.current(0)
        
        # Map display name to enum name
        self.queue_map = {opt[0]: opt[1] for opt in queue_options}
        
        # Buttons Frame
        buttons_frame = tk.Frame(self.root, bg=self.bg_color)
        buttons_frame.pack(pady=15)
        
        self.start_button = tk.Button(
            buttons_frame,
            text="▶ INICIAR BOT",
            font=("Segoe UI", 12, "bold"),
            bg=self.success_color,
            fg="white",
            width=15,
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.start_bot
        )
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = tk.Button(
            buttons_frame,
            text="■ PARAR BOT",
            font=("Segoe UI", 12, "bold"),
            bg=self.danger_color,
            fg="white",
            width=15,
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.stop_bot,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)
        
        # Status Label
        self.status_var = tk.StringVar(value="Status: Parado")
        status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.fg_color
        )
        status_label.pack(pady=5)
        
        # Log Frame
        log_frame = tk.Frame(self.root, bg=self.bg_color)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        log_label = tk.Label(
            log_frame,
            text="📋 Log de Eventos:",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor="w"
        )
        log_label.pack(fill="x")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            font=("Consolas", 9),
            bg="#0d0d1a",
            fg="#00ff88",
            insertbackground=self.fg_color,
            relief="flat",
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, pady=5)
        self.log_text.configure(state="disabled")
        
        # Clear Log Button
        clear_button = tk.Button(
            log_frame,
            text="Limpar Log",
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg=self.fg_color,
            relief="flat",
            cursor="hand2",
            command=self.clear_log
        )
        clear_button.pack(anchor="e", pady=2)
        
    def log(self, message):
        """Append a message to the log text widget"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        
    def clear_log(self):
        """Clear all log messages"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        
    def start_bot(self):
        """Start the bot in a separate thread"""
        if self.bot_running:
            return
            
        self.bot_running = True
        self.stop_event.clear()
        
        # Get selected options
        mode = self.mode_var.get()
        queue_display = self.queue_var.get()
        queue_type = self.queue_map.get(queue_display, "DRAFT_PICK")
        
        self.log(f"[INFO] Iniciando bot...")
        self.log(f"[INFO] Modo: {mode}")
        self.log(f"[INFO] Fila: {queue_display} ({queue_type})")
        
        # Update UI
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_var.set("Status: Executando...")
        
        # Start bot thread
        self.bot_thread = threading.Thread(
            target=self._run_bot,
            args=(mode, queue_type),
            daemon=True
        )
        self.bot_thread.start()
        
    def _run_bot(self, mode, queue_type):
        """Run the bot logic (called in a separate thread)"""
        try:
            # Import here to avoid circular imports and to allow GUI to load quickly
            from bot.yuumi import YuumiBot
            from common.constants import LobbyTypes
            
            # Configure lobby type
            lobby_type_enum = getattr(LobbyTypes, queue_type, LobbyTypes.DRAFT_PICK)
            
            self.root.after(0, lambda: self.log(f"[INFO] Criando instância do bot..."))
            
            bot = YuumiBot()
            
            # Inject settings into bot
            bot.selected_lobby_type = lobby_type_enum
            bot.yuumi_mode = (mode == "yuumi_full")
            
            self.root.after(0, lambda: self.log(f"[INFO] Bot iniciado. Entrando no loop principal..."))
            
            # Run main loop with stop check
            while not self.stop_event.is_set():
                try:
                    # Custom main loop that checks for stop
                    phase = bot.client.get_phase()
                    self.root.after(0, lambda p=phase: self.log(f"[PHASE] {p}"))
                    
                    # Handle different phases
                    from common.constants import ClientPhases
                    
                    if phase == ClientPhases.NONE.value:
                        bot.client.create_lobby(lobby_type=lobby_type_enum)
                    elif phase == ClientPhases.LOBBY.value:
                        bot.client.start_queue()
                    elif phase == ClientPhases.READY_CHECK.value:
                        bot.client.accept_match()
                    elif phase == ClientPhases.CHAMP_SELECT.value:
                        bot.handle_champion_select()
                    elif phase == ClientPhases.IN_GAME.value:
                        if mode == "yuumi_full":
                            # Full yuumi gameplay (if implemented)
                            self.root.after(0, lambda: self.log("[GAME] Yuumi gameplay ativo"))
                        else:
                            self.root.after(0, lambda: self.log("[GAME] Apenas aguardando fim da partida..."))
                        # Simple wait loop for game
                        import time
                        while bot.client.get_phase() == ClientPhases.IN_GAME.value and not self.stop_event.is_set():
                            time.sleep(2)
                    elif phase in [ClientPhases.PRE_END_OF_GAME.value, ClientPhases.END_OF_GAME.value]:
                        bot.client.skip_honor()
                        bot.client.skip_end_of_game()
                    elif phase == ClientPhases.RECONNECT.value:
                        bot.client.reconnect()
                    
                    import time
                    time.sleep(3)
                    
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.log(f"[ERROR] {err}"))
                    import time
                    time.sleep(5)
                    
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.log(f"[FATAL] {err}"))
        finally:
            self.root.after(0, self._on_bot_stopped)
            
    def _on_bot_stopped(self):
        """Called when bot stops (on main thread)"""
        self.bot_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_var.set("Status: Parado")
        self.log("[INFO] Bot parado.")
        
    def stop_bot(self):
        """Stop the running bot"""
        if not self.bot_running:
            return
            
        self.log("[INFO] Parando bot...")
        self.stop_event.set()
        self.status_var.set("Status: Parando...")


def main():
    root = tk.Tk()
    app = BotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
