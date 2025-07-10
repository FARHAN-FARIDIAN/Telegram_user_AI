import os
import requests
from telethon import TelegramClient, events

# --- CONFIGURATION ---
API_ID = '22752241'
API_HASH = '75b38298c9d00ffb1ef725a03ba7241b'
PHONE_NUMBER = '+989204001127'
N8N_WEBHOOK_URL = 'https://automation.easeflow.space/webhook/3b303ad9-53eb-4e36-b659-795696841edc'

client = TelegramClient('telegram_session', API_ID, API_HASH)

print("Script started. Listening for messages...")

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    if event.is_private:
        sender_id = event.sender_id # The unique ID of the user sending the message
        message_text = event.message.text

        sender = await event.get_sender()
        print(f"Received message: '{message_text}' from {sender.first_name} (ID: {sender_id})")

        try:
            # The data we are sending to the webhook
            payload = {
                "message_text": message_text,
                "sender_id": sender_id  # <-- CHANGE 1: Send the sender's ID
            }

            print("Sending to n8n webhook...")
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=90)
            response.raise_for_status()

            ai_response_data = response.json()

            # <-- CHANGE 2: The AI Agent's response is in a key named 'output'
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
    await client.start(phone=PHONE_NUMBER)
    print("Client connected successfully!")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())