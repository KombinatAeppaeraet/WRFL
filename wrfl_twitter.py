# -*- coding: UTF-8 -*-

#http://kinocksebastian.blogspot.de/2015/04/how-to-get-access-token-using-tweepy-in.html

import tweepy

def tweet(text):
    consumerKey=''
    consumerSecret=''
    accessToken=''
    accessSecret=''

    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessSecret)

    # Twitter to https://twitter.com/KombinatApparat
    api = tweepy.API(auth)

    image = '/opt/wrfl/img/w.jpg'
    api.update_with_media(image, text)

