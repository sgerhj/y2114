import logging
import time
from utils import (
    LEAGUE_GAME_CLIENT_WINNAME,
    exists,
    click,
    press,
    attack_move_click
)
from connection import Connection

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("game.log"), logging.StreamHandler()])

class Game:
    def __init__(self):
        self.conn = Connection()

    def play_game(self):
        logging.debug("Starting game...")

        try:
            self.conn.connect_lcu()
        except Exception as e:
            logging.error(f"Failed to connect to LCU: {e}")
            return False

        # Example of clicking on the "Play" button in the game
        if exists(LEAGUE_GAME_CLIENT_WINNAME):
            click((0.5, 0.5), LEAGUE_GAME_CLIENT_WINNAME)
            logging.debug("Clicked on Play button")
        else:
            logging.error("Game client window not found")
            return False

        # Add more game interactions and logic here
        # This is just a placeholder to simulate gameplay
        time.sleep(2)
        
        # Example of pressing a key
        press('enter', LEAGUE_GAME_CLIENT_WINNAME)
        logging.debug("Pressed Enter key")
        
        # Example of performing an attack move click
        attack_move_click((0.5, 0.5))
        logging.debug("Performed attack move click")
        
        return True

def main():
    logging.debug("Starting main function")
    game = Game()
    success = game.play_game()
    if success:
        logging.info("Game completed successfully")
    else:
        logging.error("Game encountered an error")

if __name__ == "__main__":
    main()
