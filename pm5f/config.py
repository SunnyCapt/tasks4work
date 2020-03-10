class web:
    oauth_url = "http://<YOUR DOMAIN>/oauth"


class vk:
    appid = 0000000
    appsecret = "<CLIENT SECRET>"
    oauth_url = "http://oauth.vk.com/authorize?" \
                f"client_id={appid}&redirect_uri=" \
                f"{web.oauth_url}&display=popup&" \
                "scope=friends,offline&response_type=code&v=5.101"
    token_url = "http://oauth.vk.com/access_token?" \
                f"client_id={appid}&client_secret={appsecret}&" \
                f"redirect_uri={web.oauth_url}&code="
    friends_get = "http://api.vk.com/method/friends.get?" \
                  "v=5.73&count=5&access_token="
    names_get = "http://api.vk.com/method/users.get?" \
                "v=5.73&access_token="
