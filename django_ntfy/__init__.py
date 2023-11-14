import typing

import requests
from django import dispatch
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend

topic_signal = dispatch.Signal()
# TODO ntfy_icon_signal = dispatch.Signal()
# TODO ntfy_actions_signal = dispatch.Signal()
# TODO ntfy_severity_signal = dispatch.Signal()
# TODO ntfy_tags_signal = dispatch.Signal()
# TODO ntfy_priority_signal = dispatch.Signal()
# TODO ntfy_click_signal = dispatch.Signal()
# TODO ntfy_icon_signal = dispatch.Signal()


def get_from_signal(signal: dispatch.Signal, message: EmailMessage, default):
    responses = signal.send(message)
    return responses[0][1] if responses else default


class NtfyBackend(BaseEmailBackend):
    def send_ntfy_message(
        self,
        title: str,
        message: str,
        topic: str,
    ) -> requests.Response:
        # TODO ntfy authentication
        url = settings.NTFY_BASE_URL

        resp = requests.post(
            url,
            json={
                "topic": topic,
                "title": title,
                "message": message,
            },
        )
        return resp

    def send_ntfy_file(
        self,
        title: str,
        data,
        filename: str,
        topic: str,
    ):
        # TODO ntfy authentication
        url = f"{settings.NTFY_BASE_URL}/{topic}"

        requests.put(
            url,
            data=data,
            headers={"Filename": filename},
        )

    def send_messages(self, email_messages: typing.List[EmailMessage]):
        count = 0
        for message in email_messages:
            topic = get_from_signal(topic_signal, message, settings.NTFY_DEFAULT_TOPIC)

            # Send message
            resp = self.send_ntfy_message(message.subject, message.body, topic)

            # Send attachments
            if getattr(settings, 'NTFY_SEND_ATTACHMENTS', False):
                for filename, content, mimetype in message.attachments:
                    self.send_ntfy_file(message.subject, content, filename, topic)

            count += 1 if resp.status_code / 100 == 2 else 0

        return count
