from time import sleep

from bot.base_bot import BaseBot
from common.constants import ClientPhases, LobbyTypes, Positions, ChampSelectPhases, SummonerSpells, ChampionIds, Items
from common.utils import is_process_running, run_process


class YuumiBot(BaseBot):
    """Class contains all bot behaviour for DiscoNunu"""

    def __init__(self):
        super().__init__()
        from bot.recovery import InjectorRecovery
        self.recovery = InjectorRecovery()
        self.build_path = (Items.World_Atlas, Items.Faerie_Charm, Items.Amplifying_Tome, Items.Moonstone_Renewer,
                           Items.Amplifying_Tome, Items.Ardent_Censer, Items.Amplifying_Tome,
                           Items.Staff_of_Flowing_Water, Items.Morellonomicon)
        self.best_friend = "f5"
        self.message_sent = False

    # ... (is_attached method remains unchanged) ...

    def handle_gameplay(self):
        """Handles gameplay once inside a summoners rift game"""
        print("DEBUG: Entered handle_gameplay")
        # Reset message flag at start of new game handle
        self.message_sent = False
        
        while True:
            # ... (existing loop code) ...
            
            # Update data first to check if game is live
            self.player_champion.update_player_data()
            
            # ... (debug prints and game_in_progress fallback logic) ...

            # Send chat message at 35 seconds
            if self.player_champion.game_in_progress and not self.message_sent:
                try:
                    game_time = self.player_champion.get_game_time()
                    if game_time > 35:
                        print("DEBUG: Sending 35s chat message...")
                        self.player_champion.write_in_chat("sry lag internet really bad")
                        self.message_sent = True
                except Exception as e:
                    print(f"DEBUG: Error sending chat message: {e}")

            self.player_champion.lock_on_ally(self.best_friend)
            # ... (rest of gameplay logic) ...

    def is_attached(self) -> bool:
        """
        Check whether Yuumi is attached
        :return: True if attached, False otherwise
        """
        if self.player_champion.is_alive and self.player_champion.side and self.player_champion.game_in_progress:
            abilities = self.player_champion.get_player_abilities()
            if abilities and "W" in abilities and "displayName" in abilities["W"]:
                return abilities["W"]["displayName"] == "Change of Plan"
        return False

    def handle_client(self) -> None:
        """Handles lobby creation, searching for game, accepting match and reconnect to game"""
        from common.visual_handler import VisualHandler
        
        visual = VisualHandler()
        
        self.is_banned = False
        while True:
            # Check for injection error and recover if needed
            self.recovery.check_and_recover()
            
            phase = self.client.get_phase()
            print(f"DEBUG: Current Phase: {phase}")
            
            if phase == ClientPhases.NONE.value:
                print("DEBUG: Creating Lobby...")
                self.client.create_lobby(lobby_type=LobbyTypes.DRAFT_PICK)
            elif phase == ClientPhases.LOBBY.value:
                self.client.start_queue()
            elif phase == ClientPhases.READY_CHECK.value:
                self.client.accept_match()
            elif phase == ClientPhases.PRE_END_OF_GAME.value:
                self.client.skip_honor()
                visual.click_image("skip_honor.png")
                visual.click_image("ok_button.png")
            elif phase == ClientPhases.END_OF_GAME.value:
                self.client.skip_honor()
                self.client.skip_end_of_game()
                visual.click_image("skip_honor.png")
                visual.click_image("ok_button.png")
                # self.recovery.open_injector_process()
            elif phase == ClientPhases.RECONNECT.value:
                self.client.reconnect()
            else:
                return

    def handle_champion_select(self) -> None:
        """Handles champion select - Logic disabled but accepts swaps"""
        from common.visual_handler import VisualHandler
        visual = VisualHandler()
        
        # Open injector at start of champ select
        # self.recovery.open_injector_process()
        
        # Wait a bit for session data to load
        sleep(2)
        
        is_support = False
        try:
            position = self.client.get_my_position()
            print(f"DEBUG: Assigned Position: {position}")
            
            # Debug: Print all team positions
            session = self.client.get_champ_select_info()
            if session:
                print("DEBUG: Team Composition:")
                for p in session.get("myTeam", []):
                    print(f"  - CellId: {p.get('cellId')}, Position: {p.get('assignedPosition')}, SummonerId: {p.get('summonerId')}")

            if position and position.upper() in ["UTILITY", "SUPPORT"]:
                is_support = True
                print("DEBUG: I am Support. No need to swap.")
            else:
                print(f"DEBUG: Assigned {position} (Not Support), asking for swap...")
                
                # Try to swap via API
                try:
                    # Try UTILITY first, then SUPPORT
                    support_cell_id = self.client.get_teammate_cell_id_by_position("UTILITY")
                    if not support_cell_id:
                         support_cell_id = self.client.get_teammate_cell_id_by_position("SUPPORT")
                    
                    if support_cell_id:
                        print(f"DEBUG: Found Support cellId: {support_cell_id}. Sending swap request...")
                        self.client.initiate_position_swap(support_cell_id)
                    else:
                        print("DEBUG: Could not find Support player (UTILITY/SUPPORT).")
                except Exception as e:
                    print(f"DEBUG: Failed to initiate swap via API: {e}")

                # Also send chat messages as backup
                chat_id = self.client.get_champ_select_conversation_id()
                if chat_id:
                    self.client.send_chat_message(chat_id, "can i supp pls?")
                    self.client.send_chat_message(chat_id, "swap?")
        except Exception as e:
            print(f"DEBUG: Error checking position: {e}")

        while self.client.get_phase() == ClientPhases.CHAMP_SELECT.value:
            # Re-check position occasionally to see if we became support
            try:
                current_pos = self.client.get_my_position()
                if current_pos and current_pos.upper() in ["UTILITY", "SUPPORT"]:
                    if not is_support:
                        print("DEBUG: Role swap successful! I am now Support.")
                    is_support = True
            except:
                pass

            # Only try to accept swaps if we are NOT support
            if not is_support:
                # Check for visual popup
                visual.click_image("accept_swap.png")
                
                # Check for API swap request
                try:
                    swap = self.client.get_ongoing_position_swap()
                    if swap:
                        swap_state = swap.get("state")
                        swap_id = swap.get("id")
                        # Only accept if it's strictly AVAILABLE or RECEIVED (meaning incoming request)
                        if swap_id and swap_state in ["AVAILABLE", "RECEIVED"]:
                            print(f"DEBUG: Found incoming swap {swap_id} with state {swap_state}. Accepting...")
                            self.client.accept_position_swap(swap_id)
                except Exception:
                    pass
                
            sleep(1)

    def handle_gameplay(self):
        """Handles gameplay once inside a summoners rift game"""
        # print("DEBUG: Entered handle_gameplay")
        # self.message_sent = False
        
        # while True:
        #     phase = self.client.get_phase()
        #     proc_running = is_process_running(self.player_champion.process_name)
            
        #     # If not in game and process not running, break loop
        #     if (phase == ClientPhases.PRE_END_OF_GAME.value or 
        #         phase == ClientPhases.END_OF_GAME.value or
        #         (phase != ClientPhases.IN_GAME.value and not proc_running)):
        #         print(f"DEBUG: Exiting gameplay loop. Phase: {phase}, Process: {proc_running}")
        #         # Only kill if process is still running and we are truly done
        #         if proc_running:
        #             run_process(process_name="taskkill", args=f'/IM "{self.player_champion.process_name}" /F')
        #         self.player_champion.release_ally(self.best_friend)
        #         break
            
        #     try:
        #         # Update data first to check if game is live
        #         self.player_champion.update_player_data()
        #     except Exception as e:
        #         print(f"DEBUG: Error updating player data (Game likely closed): {e}")
        #         sleep(2)
        #         continue
            
        #     # Debug Player State
        #     print(f"DEBUG: State -> InProgress: {self.player_champion.game_in_progress}, "
        #           f"Name: {self.player_champion.summoner_name}, Side: {self.player_champion.side}, "
        #           f"Alive: {self.player_champion.is_alive}")

        #     if not self.player_champion.game_in_progress:
        #         print("DEBUG: Waiting for GameStart event (game_in_progress is False)...")
        #         if self.player_champion.summoner_name:
        #             print("DEBUG: Force enabling game_in_progress because we have summoner name.")
        #             self.player_champion.game_in_progress = True
        #         else:
        #             sleep(2)
        #             continue

        #      # Send chat message at 35 seconds
        #     if self.player_champion.game_in_progress and not self.message_sent:
        #         try:
        #             game_time = self.player_champion.get_game_time()
        #             if game_time > 35:
        #                 print("DEBUG: Sending 35s chat message...")
        #                 self.player_champion.write_in_chat("sry lag internet really bad")
        #                 self.message_sent = True
        #         except Exception as e:
        #             # Ignore error if get_game_time fails (e.g. API not ready)
        #             pass

        #     self.player_champion.lock_on_ally(self.best_friend)
            
        #     if not self.is_attached():
        #         self.player_champion.tactical_retreat(0.7)
        #         for _ in range(2):  # Can buy multiple items if enough gold
        #             self.player_champion.buy_items(self.build_path)

        #         self.player_champion.lock_on_ally(self.best_friend)
        #         self.player_champion.go_to_center()
        #         
        #         if not self.is_attached():  # Ensures Yuumi doesn't detach because game remembers w presses
        #             self.player_champion.use_spell("w")
        #         
        #         self.player_champion.use_spell("f")
        #     else:
        #         self.player_champion.use_spell("e")
        #         self.player_champion.use_spell("r")
        #         self.player_champion.use_spell("d")
            
        #     self.player_champion.upgrade_ability("r")
        #     self.player_champion.upgrade_ability("e")
        #     self.player_champion.upgrade_ability("w")
        #     self.player_champion.upgrade_ability("q")
            
        #     sleep(1)

        # Restored simple loop logic
        while self.client.get_phase() == ClientPhases.IN_GAME.value:
            sleep(1)
