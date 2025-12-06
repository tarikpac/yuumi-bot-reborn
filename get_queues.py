from api.client import ClientAPI
from config import BotConfig
import json

def main():
    config = BotConfig()
    client = ClientAPI(config.protocol, "127.0.0.1", config.port, config.password)
    client.connect()
    
    print("Fetching available queues...")
    # Get all queues
    queues = client.get_with_retries("/lol-game-queues/v1/queues").json()
    
    available_queues = []
    for queue in queues:
        # Check if queue is available (usually has 'queueAvailability': 'Available')
        if queue.get('queueAvailability') == 'Available':
            available_queues.append(queue)
            print(f"ID: {queue['id']}, Name: {queue.get('name')}, Map: {queue.get('map')}, Description: {queue.get('description')}")

    # Also try to see if we can get current lobby config if one exists (though we are likely not in one)
    
if __name__ == "__main__":
    main()
