# Generic example:
WhateverYouLike = { # you can select your own custom name for an applet instance
    'applet':'rssfeed', # which applet to use for this instance (necessary)
    'interval':60, # interval of updates in minutes (default: set by applet)
    'debug':True, # traceback output (default: True)
    'notify':True, # desktop notifications (default: True)
    'enabled':False, # (default: True)
    'visible':True, # visibility of the icon (default: True)
    'icon':{'new':'myicon.png'} # dictionary of your custom icons (default: set by applet)
}

# There are 4 icon types by default (idle, new, updating, error), but applet may
# use its own icon types. You can change those too. GNAF searches in these
# folders for icons (as ordered):
#  - ~/.gnaf/applet-name
#  - ~/.gnaf
#  - /gnaf-path/applets/applet-name/icons
#  - /gnaf-path/applets/applet-name
#  - /gnaf-path/applets


# Example of instance using rssfeed applet:
PhilosophyFeed = {
    'applet':'rssfeed',
    'interval':30,
    'url':'http://philosophy.stackexchange.com/feeds',
    'entries-num':5,
    'max-title-length':75,
    'notify':False
}

# Example of instance using mail applet:
Gmail = {
    'applet':'mail',
    'interval':15,
    'icon':{
        'idle':'gmail_idle.png',
        'updating':'gmail_updating.png',
        'new':'gmail_new.png',
        'error':'gmail_error.png'
    },
    'username':'my.username',
    'password':'PaSsWoRd',
    'host':'imap.gmail.com',
    'port':'auto',
    'ssl':True,
    'mailboxes':[
        'Inbox',
        'AntiSocial',
        'Development',
        'Friends',
        'Philosophy',
        'University'
    ],
    'url':'http://mail.google.com/'
}
