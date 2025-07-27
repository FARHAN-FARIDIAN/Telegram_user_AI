import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- HARDCODED CONFIGURATION ---
# All secrets are included in this file.

API_ID = 22752241
API_HASH = '75b38298c9d00ffb1ef725a03ba7241b'
N8N_WEBHOOK_URL = 'https://automation.easeflow.space/webhook/3b303ad9-53eb-4e36-b659-795696841edc'

# Your personal session string is hardcoded below.
SESSION_STRING = '1BJWap1wBu3K6cFY8GXRaXLFH6xtW8RCM4FdWjjULaBkjUqc6zkerOwyHjXzwiTjPttON3VezzCHq7ESGz5IQU0yC9ry8Dcl8mM4XcaeXEEI_20H4r0NeJTSi9chKCB5d4fIuvLIOuxxK8mR3MoMj7eFMWo31x7TxUe_BxpMXGhJRNt_n17hC4G3b5VkV5eUzVioE58sDlgPRd_Mmpmr-4EJZZqCRSbG9WZujPMZAOMCHzC9BashGlmy4cG0r8r24yEv0e5bzKsQKzS-Dt4ALUwOHYLEBfhv1AAeQe9yajO2SV3sgI7UpyfxA7eRzzYRTAoKbIH_loX8Fco9rxSRmItqbih_P6Ps='


# --- SCRIPT LOGIC ---

# Initialize the client with the hardcoded session string
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

print("Script starting...")

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    # We only care about private messages from other users
    if event.is_private:
        sender_id = event.sender_id
        message_text = event.raw_text

        try:
            sender = await event.get_sender()
            first_name = sender.first_name if sender else "Unknown"
            print(f"Received message: '{message_text}' from {first_name} (ID: {sender_id})")

            payload = {
                "message_text": message_text,
                "sender_id": sender_id
            }

            print("Sending to n8n webhook...")
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=90)
            response.raise_for_status()

            ai_response_data = response.json()
            ai_reply_text = ai_response_data.get('output')

            if ai_reply_text:
                print(f"AI response: '{ai_reply_text}'")
                await event.reply(ai_reply_text)
            else:
                print("Did not get a valid text reply from AI. Response was:", ai_response_data)

        except requests.exceptions.RequestException as e:
            print(f"Error calling n8n webhook: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

async def main():
    await client.start()
    print("Client connected successfully using session string!")
    print("Listening for messages...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())