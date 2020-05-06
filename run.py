import os, json
from config import SECRETS_FILE
from client import BotClient


def create_secrets_file():
    print("Creating new secrets file {}...".format(SECRETS_FILE))
    print("Please enter your Discord bot's token:")
    token = input()
    secrets_json = {'token': token}
    with open(SECRETS_FILE, 'w') as f:
        f.write(json.dumps(secrets_json))


def get_discord_token():
    if os.path.exists(SECRETS_FILE):
        f = open(SECRETS_FILE, 'r')
        try:
            data = json.load(f)
        except Exception as e:
            print("[ERROR]",type(e).__name__)
            print("[ERROR] Secrets file {} is invalid.".format(SECRETS_FILE))
            f.close()
            create_secrets_file()
            f = open(SECRETS_FILE, 'r')
            data = json.load(f)
        f.close()
        return data['token']
    else:
        print("[ERROR] File {} does not exist.".format(SECRETS_FILE))
        create_secrets_file()
        return get_discord_token()


if __name__ == "__main__":
    print("[INFO] Starting the bot...")

    DISCORD_TOKEN = get_discord_token()

    client = BotClient()
    client.run(DISCORD_TOKEN)