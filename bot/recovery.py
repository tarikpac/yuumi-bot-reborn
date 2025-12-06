import logging
import subprocess
import mouse
import keyboard
from time import sleep
from pathlib import Path
from common.visual_handler import VisualHandler
from config import BotConfig

class InjectorRecovery:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = BotConfig()
        self.visual = VisualHandler()
        self.has_failed_once = False

    def check_and_recover(self):
        """Checks for error popup and performs injection if needed"""
        # Check for the specific error popup
        if self.visual.click_image("error_ok.png", confidence=0.9):
            self.logger.info("Injection error detected! Starting recovery sequence...")
            self.has_failed_once = True
            self.perform_injection()
            return True
        
        # If we already failed once in this session, we might need to inject proactively
        # But usually the error appears again if we don't inject. 
        # So we can just wait for the error to appear again or inject blindly?
        # The user said: "toda partida que iniciarmos depois de dado esse erro, vai precisar injetar dessa forma"
        # This implies we should probably inject when the game starts loading.
        return False

    def perform_injection(self):
        self.logger.info("Opening Extreme Injector...")
        
        # Open Injector
        try:
            subprocess.Popen(str(self.config.injector_path), cwd=str(self.config.injector_path.parent))
        except Exception as e:
            self.logger.error(f"Failed to open injector: {e}")
            return

        sleep(3) # Wait for it to open

        # Try to find the window and bring to front (optional, subprocess usually does it)
        
        # Click Select Process (needs image)
        if self.visual.click_image("injector_select.png"):
            sleep(1)
            # Type process name
            keyboard.write("League of Legends")
            sleep(0.5)
            keyboard.press_and_release('enter')
            sleep(1)
        else:
            self.logger.warning("Could not find 'Select' button on injector. Assuming process is already selected or UI is different.")

        # Add DLL if needed (assuming it might be saved, but let's try to be safe)
        # This is tricky without knowing if it's already there. 
        # Let's assume the user sets it up once and we just click Inject.
        
        # Click Inject
        if self.visual.click_image("injector_inject_btn.png"):
            self.logger.info("Clicked Inject!")
            sleep(5) # Wait for injection
            # Close injector?
            # keyboard.press_and_release('alt+f4')
        else:
            self.logger.error("Could not find 'Inject' button!")

    def open_injector_process(self):
        """Opens the injector executable if not already running"""
        injector_name = self.config.injector_path.name
        from common.utils import is_process_running
        
        if is_process_running(injector_name):
            self.logger.info(f"{injector_name} is already running.")
            return

        self.logger.info(f"Opening {injector_name}...")
        try:
            subprocess.Popen(str(self.config.injector_path), cwd=str(self.config.injector_path.parent))
        except Exception as e:
            self.logger.error(f"Failed to open injector: {e}")

