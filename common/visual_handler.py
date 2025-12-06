import pyautogui
import logging
from pathlib import Path
from time import sleep
import mouse

class VisualHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.assets_path = Path("assets")

    def click_image(self, image_name: str, confidence: float = 0.9) -> bool:
        """
        Locates an image on screen and clicks it.
        :param image_name: filename of the image in assets folder
        :param confidence: matching confidence
        :return: True if clicked, False if not found
        """
        image_path = self.assets_path / image_name
        if not image_path.exists():
            self.logger.warning(f"Image asset not found: {image_path}")
            return False

        try:
            location = pyautogui.locateOnScreen(str(image_path), confidence=confidence)
            if location:
                self.logger.info(f"Image {image_name} found. Clicking...")
                center = pyautogui.center(location)
                mouse.move(center.x, center.y, absolute=True, duration=0.2)
                sleep(0.1)
                mouse.click(button='left')
                return True
        except Exception as e:
            self.logger.error(f"Error searching for image {image_name}: {e}")
        
        return False
