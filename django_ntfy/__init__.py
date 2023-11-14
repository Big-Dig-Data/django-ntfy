import typing

import requests
from django import dispatch
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend

topic_signal = dispatch.Signal()
icon_signal = dispatch.Signal()
tags_signal = dispatch.Signal()
actions_signal = dispatch.Signal()
priority_signal = dispatch.Signal()
# TODO ntfy_click_signal = dispatch.Signal()


def get_from_signal(signal: dispatch.Signal, message: EmailMessage, default):
    responses = signal.send(message)
    return responses[0][1] if responses else default


class NtfyBackend(BaseEmailBackend):
    def get_extra(self, message: EmailMessage):
        extra = {}

        if icon := get_from_signal(
            icon_signal, message, getattr(settings, "NTFY_DEFAULT_ICON_URL", None)
        ):
            extra["icon"] = icon

        if tags := get_from_signal(
            tags_signal, message, getattr(settings, "NTFY_DEFAULT_TAGS", None)
        ):
            extra["tags"] = tags

        if actions := get_from_signal(actions_signal, message, None):
            extra["actions"] = actions

        if priority := get_from_signal(
            priority_signal, message, getattr(settings, "NTFY_DEFAULT_PRIORITY", None)
        ):
            extra["priority"] = priority

        return extra

    def send_ntfy_message(self, message: EmailMessage) -> requests.Response:
        # TODO ntfy authentication
        url = settings.NTFY_BASE_URL
        title = message.subject
        topic = get_from_signal(topic_signal, message, settings.NTFY_DEFAULT_TOPIC)
        body = message.body

        resp = requests.post(
            url,
            json={
                "topic": topic,
                "title": title,
                "message": body[: getattr(settings, "NTFY_MESSAGE_SIZE_LIMIT", 1000)],
                **self.get_extra(message),
            },
        )
        return resp

    def send_ntfy_file(
        self,
        message,
        data,
        filename: str,
    ):
        # TODO ntfy authentication
        topic = get_from_signal(topic_signal, message, settings.NTFY_DEFAULT_TOPIC)
        url = f"{settings.NTFY_BASE_URL}/{topic}"

        requests.put(
            url,
            data=data,
            headers={"Filename": filename},
        )

    def send_messages(self, email_messages: typing.List[EmailMessage]):
        count = 0
        for message in email_messages:
            # Send message
            resp = self.send_ntfy_message(message)

            # Send attachments
            if getattr(settings, 'NTFY_SEND_ATTACHMENTS', False):
                for filename, content, mimetype in message.attachments:
                    self.send_ntfy_file(message, content, filename)

            count += 1 if resp.status_code / 100 == 2 else 0

        return count
