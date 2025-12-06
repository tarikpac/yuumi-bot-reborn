from base64 import b64encode
from time import sleep
from typing import List, Dict, Optional

from requests import Response

from common.request_api import RequestAPI
from common.constants import LobbyTypes, Positions, ChampionIds, SummonerSpells
from common.utils import wait_for_condition


class LobbyNotReady(Exception):
    def __init__(self, message="Unexpected lobby state. Can't start"):
        super().__init__(message)


class ClientAPI(RequestAPI):
    """Client LCU API"""

    def __init__(self, protocol: str, domain: str, port: str, password: str):
        super().__init__(protocol=protocol, domain=domain, port=port)
        self.username = "riot"
        self.password = password
        self.headers = {
            "Authorization":
                f"Basic {b64encode(bytes(f'{self.username}:{self.password}', 'utf-8')).decode('ascii')}"
        }

    def connect(self, timeout: int = 60, delay: int = 5) -> None:
        """
        Attempts to connect to Client. Logs out after close
        :param timeout: time to wait for connection to succeed
        :param delay: delay between retries
        """
        self.logger.info("Connecting to Client")
        wait_for_condition(
            condition_callback=lambda: self.get_with_retries("/lol-login/v1/session").json()["state"] == "SUCCEEDED",
            timeout=timeout,
            delay=delay
        )
        self.logger.info("Connection to Client Successful")
        self.post("/lol-login/v1/delete-rso-on-close")  # ensures self.logout after close

    def get_phase(self) -> str:
        """Requests the League Client phase"""
        sleep(3)  # To avoid spam and give time to update phase
        phase = self.get_with_retries("/lol-gameflow/v1/gameflow-phase")
        self.logger.info(f"Current phase: {phase.json()}")
        return phase.json()

    def create_lobby(self, lobby_type: LobbyTypes) -> Response:
        """
        Creates a lobby for given lobby ID
        :param lobby_type: Lobby type to create
        """
        self.logger.info(f"Creating lobby {lobby_type.name}")
        data = {'queueId': lobby_type.value}
        response = self.post("/lol-lobby/v2/lobby", data=data)
        self.logger.info(f"Create Lobby Response: {response.status_code} - {response.text}")
        return response

    def select_positions(self, primary: Positions, secondary: Positions) -> None:
        """
        Selects preferred positions
        :param primary: primary position
        :param secondary: secondary position
        """
        self.logger.info("Selecting Positions")
        self.put(url="/lol-lobby/v2/lobby/members/localMember/position-preferences",
                 data={"firstPreference": primary.value, "secondPreference": secondary.value})

    def lobby_can_start(self) -> bool:
        """"
        Check whether lobby can start
        :return: True if yes, False otherwise
        """
        return self.get_with_retries("/lol-lobby/v2/lobby").json()["canStartActivity"]

    def wait_dodge_timer(self) -> None:
        """"Checks whether there is a dodge penalty and waits it out"""
        response = self.get_with_retries("/lol-lobby/v2/lobby/matchmaking/search-state")
        if response.json()["errors"]:
            dodge_timer = int(response.json()["errors"][0]["penaltyTimeRemaining"])
            self.logger.info(f"Dodge Timer. Time Remaining: {dodge_timer}")
            sleep(dodge_timer)

    def start_queue(self) -> None:
        """Starts queue"""
        self.logger.info("Starting queue")
        self.wait_dodge_timer()
        if not self.lobby_can_start():
            raise LobbyNotReady()
        self.post("/lol-lobby/v2/lobby/matchmaking/search")

    def accept_match(self) -> None:
        """Accepts the Ready Check"""
        self.logger.info("Accepting match")
        self.post("/lol-matchmaking/v1/ready-check/accept")

    def get_champ_select_info(self) -> Dict:
        """"Get all information about current champion select"""
        return self.get_with_retries("/lol-champ-select/v1/session").json()

    def is_champ_pickable(self, champ: ChampionIds) -> bool:
        """"
        Validate if champion is available to pick
        :param champ: Champion to check if available to pick
        :return: True if pickable, False otherwise
        """
        return champ.value in self.get_with_retries("/lol-champ-select/v1/pickable-champion-ids").json()

    def is_champ_bannable(self, champ: ChampionIds) -> bool:
        """"
        Validate if champion is available to pick
        :param champ: Champion to check if available to ban
        :return: True if bannable, False otherwise
        """
        return champ.value in self.get_with_retries("/lol-champ-select/v1/bannable-champion-ids").json()

    def confirm_champion(self, phase_id: int) -> None:
        """"
        Completes champion action(pick, ban) on already selected champion
        :param phase_id: id of the current champion select phase
        """
        self.post(f"/lol-champ-select/v1/session/actions/{phase_id}/complete")

    def select_summoner_spells(self, spell1: SummonerSpells, spell2: SummonerSpells) -> None:
        """
        Selects summoner spells
        :param spell1: left summoner spell
        :param spell2: right summoner spell
        """
        self.logger.info(f"Summoner spells {spell1.name}, {spell2.name}")
        data = {
            "spell1Id": spell1.value,
            "spell2Id": spell2.value,
        }
        self.patch(url="/lol-champ-select/v1/session/my-selection", data=data)
        self.post(url="/lol-champ-select/v1/session/my-selection/reroll")

    def ban_champion(self, champs: Optional[List[ChampionIds]] = None) -> bool:
        """
        Select champions to ban by given ids
        :param champs: champions to ban in order of priority
        :return: True if champion banned, False otherwise
        """
        champ_id = next((champ.value for champ in champs if self.is_champ_bannable(champ=champ)), None)
        if not champ_id:
            return True  # If champion not bannable will ignore ban phase
        champ_select = self.get_champ_select_info()
        data = {"championId": champ_id}
        for action in champ_select["actions"]:
            for action_cell in action:
                if action_cell["actorCellId"] == champ_select['localPlayerCellId'] and not action_cell["completed"] \
                        and action_cell["type"] == "ban":  # Will ban only if player's turn
                    self.logger.info(f"Banning {ChampionIds(champ_id).name}")
                    self.patch(url=f"/lol-champ-select/v1/session/actions/{action_cell["id"]}", data=data)
                    self.confirm_champion(phase_id=action_cell["id"])
                    return True
        return False

    def pick_champion(self, champs: List[ChampionIds]) -> None:
        """
        Select champions to pick by given ids. Will dodge if champions unavailable
        :param champs: champions to pick in order of priority
        """
        champ_id = next((champ.value for champ in champs if self.is_champ_pickable(champ=champ)), None)
        if not champ_id:
            self.logger.info("Dodging Champion select. Desired champion unavailable")
            return
        champ_select = self.get_champ_select_info()
        data = {"championId": champ_id}
        for action in champ_select["actions"]:
            for action_cell in action:
                if action_cell["actorCellId"] == champ_select['localPlayerCellId'] and not action_cell["completed"] \
                        and action_cell["type"] == "pick":  # Will pick only if player's turn
                    self.logger.info(f"Picking {ChampionIds(champ_id).name}")
                    self.patch(url=f"/lol-champ-select/v1/session/actions/{action_cell["id"]}", data=data)
                    self.confirm_champion(phase_id=action_cell["id"])

    def skip_honor(self) -> None:
        """Skip honor screen"""
        self.logger.info("Skipping Honor Screen...")
        resp_vote = self.post("/lol-honor-v2/v1/vote", data={"honorCategory": "OPT_OUT", "summonerId": 0})
        self.logger.info(f"Honor Vote Response: {resp_vote.status_code} - {resp_vote.text}")
        
        resp_ack = self.post("/lol-honor-v2/v1/ballot/ack")
        self.logger.info(f"Honor Ack Response: {resp_ack.status_code} - {resp_ack.text}")

    def skip_end_of_game(self) -> None:
        """Skip end of game screen"""
        self.logger.info("Skipping End of Game Stats...")
        resp = self.post(url="/lol-end-of-game/v1/state/dismiss-stats")
        self.logger.info(f"Dismiss Stats Response: {resp.status_code} - {resp.text}")

    def reconnect(self) -> None:
        """Reconnect to game if disconnected"""
        self.post_with_retries(url="/lol-gameflow/v1/reconnect")

    def get_champ_select_conversation_id(self) -> Optional[str]:
        """Get the conversation ID for the champion select chat"""
        conversations = self.get_with_retries("/lol-chat/v1/conversations").json()
        for conv in conversations:
            if conv.get("type") == "championSelect":
                return conv.get("id")
        return None

    def send_chat_message(self, conversation_id: str, message: str) -> None:
        """Send a message to a specific conversation"""
        self.post(f"/lol-chat/v1/conversations/{conversation_id}/messages", data={"body": message, "type": "chat"})

    def get_my_position(self) -> Optional[str]:
        """Get the current player's assigned position in champion select"""
        session = self.get_champ_select_info()
        local_cell_id = session.get("localPlayerCellId")
        for player in session.get("myTeam", []):
            if player.get("cellId") == local_cell_id:
                return player.get("assignedPosition")
        return None

    def get_teammate_cell_id_by_position(self, position: str) -> Optional[int]:
        """Get the cellId of a teammate with a specific position"""
        session = self.get_champ_select_info()
        for player in session.get("myTeam", []):
            if player.get("assignedPosition", "").upper() == position.upper():
                return player.get("cellId")
        return None

    def initiate_position_swap(self, cell_id: int) -> None:
        """Initiate a position (role) swap with a teammate"""
        self.logger.info(f"Initiating position swap with cellId: {cell_id}")
        self.post(f"/lol-champ-select/v1/session/position-swaps/{cell_id}/request")

    def get_ongoing_position_swap(self) -> Optional[dict]:
        """Get details of the currently ongoing position swap"""
        # Try the specific ongoing endpoint first
        response = self.get("/lol-champ-select/v1/ongoing-position-swap")
        if response.status_code == 200:
            data = response.json()
            if data and data.get("id", 0) > 0:
                return data
        
        # Fallback to checking the list of all swaps
        response = self.get("/lol-champ-select/v1/session/position-swaps")
        if response.status_code == 200:
            swaps = response.json()
            if swaps:
                for swap in swaps:
                    # Only return if it's a valid swap request directed at us (usually has an ID > 0)
                    if swap.get("id", 0) > 0:
                        return swap
        return None

    def accept_position_swap(self, swap_id: int) -> None:
        """Accept a position swap"""
        self.logger.info(f"Accepting position swap with id: {swap_id}")
        self.post(f"/lol-champ-select/v1/session/position-swaps/{swap_id}/accept")
