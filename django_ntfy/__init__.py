import math
import typing

import requests
from django import dispatch
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.module_loading import import_string
from django.utils.text import slugify

topic_signal = dispatch.Signal()
icon_signal = dispatch.Signal()
tags_signal = dispatch.Signal()
actions_signal = dispatch.Signal()
priority_signal = dispatch.Signal()
# TODO ntfy_click_signal = dispatch.Signal()


def get_from_signal(signal: dispatch.Signal, message: EmailMessage, default):
    responses = signal.send(message)
    return responses[0][1] if responses else default


class ExponentialRateLimitMixin:
    def get_aggregated_count(self, count):
        if count < 1:
            return 0

        times = int(math.log(count, 2))
        return 2 ** (times - 1)

    def cache_key(self, message: EmailMessage):
        cls = type(self)
        return slugify(
            f"{cls.__module__}-{cls.__name__}-{message.subject}-"
            f"{message.from_email}-{'_'.join(message.to)}"
        )

    def send_messages(self, email_messages: typing.List[EmailMessage]):
        sent_count = 0
        cache_timenout = getattr(
            settings,
            "EMAIL_EXPONENTIAL_RATE_LIMIT_TIMEOUT",
            24 * 60 * 60,  # cache will timeout in a day
        )

        for message in email_messages:
            # get from cache
            key = self.cache_key(message)
            count = cache.get(key, 1)

            # calculate aggregations
            times = math.log(count, 2)

            # Check whether message should be sent
            if times.is_integer():
                aggregated = self.get_aggregated_count(count)

                if aggregated > 1:
                    message.subject += f" ({aggregated})"

                if new_sent := super().send_messages(email_messages):  # noqa
                    sent_count += new_sent
                    cache.set(key, count + 1, timeout=cache_timenout)

                # remove aggreated from subjects
                if aggregated > 1:
                    message.subject = message.subject[: len(f" ({aggregated})") - 1]
            else:
                cache.set(key, count + 1, timeout=cache_timenout)

        return sent_count


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


class ExponentialRateLimitBackends(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        backend_strings = getattr(
            settings,
            "EMAIL_EXPONENTIAL_RATE_LIMIT_BACKENDS",
        )
        backend_classes = [import_string(e) for e in backend_strings]
        limited_backend_classes = [
            type(f"ExponentialRateLimit{e.__name__}", (ExponentialRateLimitMixin, e), {})
            for e in backend_classes
        ]

        self.backends = [cls(*args, **kwargs) for cls in limited_backend_classes]

    def open(self):
        for backend in self.backends:
            backend.open()

    def close(self):
        for backend in self.backends:
            backend.close()

    def send_messages(self, email_messages):
        return sum(e.send_messages(email_messages) for e in self.backends)
