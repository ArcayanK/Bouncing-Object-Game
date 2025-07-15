This is a game program designed to promote engagement. It has 2 Primary Functgions:
Function 1: Twitch Bit and Cheer Recognition and Acknowledgement Function
Function 2: Bouncing Object Game

Function 1: Twitch Bit and Cheer Recognition and Awknowledgement Function
1. Run ngrok
    a. C:\Program Files\ngrok\ngrok.exe
    b. use command "ngrok http 8080"
2. update .env
    a. CALLBACK_URL=____Foreward URL____/eventsub
3. run eventsub_server.py
    a. python eventsub_server.py
4. Revieve challenge, this confirms the connection 
    OR revieve a subscription response 409 error (this is fine and it confirms the connection)

*** From here you should be able to revieve notifications of channel point rewards and bits

or

1. Run main_app.py
    a. python main_app.py


Function 2: Bouncing Object Game
1. Open "bouncer.html"
2. Run websocket_trigger.py
    a. python websocket_trigger.py
        * you should see "✅ WebSocket server running on ws://localhost:8765" in terminal
2. Trigger:
    a. Manual Trigger
    b. Automated Trigger: X Bits or Cheers


Future Updates:
    1. Activate on Specific Channel Reward/Cheer (Corner Wars: Challenge)
    2. Have multiple instances of the moving object run at the same time.