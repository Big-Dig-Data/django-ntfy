# django-ntfy

Django's email backend which is used to send messages to ntfy.sh (or self-hosted instace) instead of actually sending an email.


# Installation

First you need to install the package:
```bash
pip install django-ntfy
```

You need to configure the NTFY url and topic `settings.py`:
```python
NTFY_BASE_URL = "https://ntfy.sh/"
NTFY_DEFAULT_TOPIC = "my-original-topic-name"
```

Now if you want use NTFY backend to propagate errors instead of ordinary EMAIL_BACKEND, you can set:
```python
LOGGING = {
    ...
    "handlers": {
        ...
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "email_backend": "django_ntfy.NtfyBackend",
        }
        ...
    }
    ...
}
```

Note the you may also want to set `EMAIL_BACKEND="django_ntfy.NtfyBackend"` directly, but be aware that once you do it, you won't be able to send any emails, because everything will published only to NTFY topic. (This still might be useful for some debugging purposes or staging servers).

# Backends

## NtfyBackend

Replacement of django's default EmailBackend. It is used to publish a topic to ntfy.sh instead of sending and email. Note the some fields may not be useful here such as recievers address.

Note ntfy message options options see [NFTY publish docs](https://docs.ntfy.sh/publish/).

### Variables
* `NTFY_BASE_URL` - type str, required, basic url on ntfy server
* `NTFY_DEFAULT_TOPIC` - type str, required, default topic when publishing a message
* `NTFY_MESSAGE_SIZE_LIMIT` - type int, default 1000, limits the body/message size (note that ntfy.sh discards long messages)
* `NTFY_SEND_ATTACHMENTS` - type bool, default False, sends attachments as extra messages into ntfy.sh (experimental)

* `NTFY_DEFAULT_ICON_URL` - type :str, default None, Url of custom icon used in the message
* `NTFY_DEFAULT_TAGS` - type list of str, default [], Tags of the message
* `NTFY_DEFAULT_PRIORITY` - 1 to 5, default None , Priority of the message

### Signals
Content of the message sent to NTFY server can be also altered using signals.

## topic_signal
Alters the topic of output messages.

```python
from django.core.mail import EmailMessage
from django_ntfy import topic_signal

def topic_handler(sender, message: EmailMessage) -> str:
    ...
    return "topic"

topic_signal.connect(topic_handler, dispatch_uid="ntfy_topic")
```

## icon_signal
Alters the icon of output messages.

```python
from django.core.mail import EmailMessage
from django_ntfy import icon_signal

def icon_handler(sender, message: EmailMessage) -> str:
    ...
    return "https://ntfy.sh/_site/images/favicon.ico"

icon_signal.connect(icon_handler, dispatch_uid="ntfy_icon")
```

## tags_signal
Alters the tags of output messages.

```python
from django.core.mail import EmailMessage
from django_ntfy import tags_signal

def tags_handler(sender, message: EmailMessage) -> list[str]:
    ...
    return ["warning", "skull"]

tags_signal.connect(tags_handler, dispatch_uid="ntfy_tags")
```

## actions_signal
Alters the actions of output messages.

```python
from django.core.mail import EmailMessage
from django_ntfy import actions_signal

def actions_handler(sender, message: EmailMessage) -> list[dict]:
    ...
    return [
        {
            "action": "view",
            "label": "Ok",
            "url": "https://example.com/ok",
        },
        {
            "action": "http",
            "label": "Cancel",
            "url": "https://example.com/cancel",
            "body": json.dumps({"a": "b"}),
            "clear": True,
        },
    ]

actions_signal.connect(actions_handler, dispatch_uid="ntfy_actions")
```

## priority_signal
Alters the priority of output messages.

```python
from django.core.mail import EmailMessage
from django_ntfy import priority_signal

def priority_handler(sender, message: EmailMessage) -> int:
    ...
    return 5

priority_signal.connect(tags_handler, dispatch_uid="ntfy_priority")
```


## ExponentialRateLimitBackends
This backend can be used to group multiple email backends together (e.g. `NtfyBackend` and `EmailBackend`). It also provides some bacis Rate limit support so that your emailbox / topic is not flooded with same messages.

To set it you can simply do it like this:
```python
EMAIL_EXPONENTIAL_RATE_LIMIT_BACKENDS = [
    "django.core.mail.backends.smtp.EmailBackend",
    "django_ntfy.NtfyBackend",
]
```

If you want to disable RateLimit functionality you configure it via
```python
EMAIL_EXPONENTIAL_RATE_LIMIT_TIMEOUT = 0
```
