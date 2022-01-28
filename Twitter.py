from twython import Twython
import Tokens
import requests



class Twitter:
    def authenticate(self):
        # Get OAuth verifier and tokens
        twitter = Twython(Tokens.API_KEY, Tokens.API_KEY_SECRET)
        auth = twitter.get_authentication_tokens()
        self.OAUTH_TOKEN = auth['oauth_token']
        self.OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
        self.oauth_verifier_url = auth['auth_url']
        self.oauth_verifier = requests.get(self.oauth_verifier_url)
        print("Verifier URL is:" + self.oauth_verifier_url)
        print("OAUTH_TOKEN is:" + self.OAUTH_TOKEN)
        print("OAUTH TOKEN SECRET is:" + self.OAUTH_TOKEN_SECRET)

    def generateToken(self):
        # Use OAuth verifier to get account specific tokens
        twitter = Twython(Tokens.API_KEY, Tokens.API_KEY_SECRET, Tokens.AUTH_TOKEN, Tokens.AUTH_SECRET)
        final_step = twitter.get_authorized_tokens(Tokens.AUTH_CODE)
        self.token = final_step['oauth_token']
        self.secret = final_step['oauth_token_secret']
        print("Token: " + self.token)
        print("Secret: "+ self.secret)

    def getTimeline(self):
        # Get most recent tweet
        twitter = Twython(Tokens.API_KEY, Tokens.API_KEY_SECRET, Tokens.TOKEN, Tokens.SECRET)
        return twitter.get_user_timeline(screen_name="RoverGifs", count=1)

    def post(self, photoPath, title):
        # Post image
        twitter = Twython(Tokens.API_KEY, Tokens.API_KEY_SECRET, Tokens.TOKEN, Tokens.SECRET)
        gif = open(photoPath, 'rb')
        response = twitter.upload_media(media=gif)
        twitter.update_status(status=title, media_ids=[response['media_id']])

