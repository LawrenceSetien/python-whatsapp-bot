
# Instructions and useful commands

## Running the app in localhost
### 1. Update Meta token
- Quick link: https://developers.facebook.com/apps/1473333179967707/whatsapp-business/wa-dev-console/?business_id=3702414430076299
- Go to Meta for Developers and open the wsp-chatbot-one app
- Click on WhatsApp -> API Config
- Copy the temporary token
- Update in .env file

### 2. Start Ngork
```sh
ngrok http 8000 --domain=winning-discrete-ladybird.ngrok-free.app
```

### 3. Start the app
```sh
cd lambda

python run_localhost.py
```

