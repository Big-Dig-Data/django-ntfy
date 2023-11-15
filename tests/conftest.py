import json

import pytest


@pytest.fixture
def use_ntfy_backend(settings):
    # we need to explicitly override it here
    settings.EMAIL_BACKEND = 'django_ntfy.NtfyBackend'


@pytest.fixture
def use_smtp_exponential_ratelimit_backend(settings):
    # we need to explicitly override it here
    settings.EMAIL_BACKEND = 'django_ntfy.SmtpExponentialRateLimitEmailBackend'


@pytest.fixture
def use_ntfy_exponential_ratelimit_backend(settings):
    # we need to explicitly override it here
    settings.EMAIL_BACKEND = 'django_ntfy.NtfyBackendExponentialRateLimitBackend'


@pytest.fixture
def use_exponential_ratelimit_backends(settings):
    # we need to explicitly override it here
    settings.EMAIL_BACKEND = 'django_ntfy.ExponentialRateLimitBackends'


@pytest.fixture
def topic_signal():
    topic = "altered-topic"

    def handler(*args, **kwargs):
        return topic

    from django_ntfy import topic_signal

    topic_signal.connect(handler, dispatch_uid="test_topic")

    yield topic

    topic_signal.disconnect(dispatch_uid="test_topic")


@pytest.fixture
def icon_signal():
    icon = "https://example.com/favicon.ico"

    from django_ntfy import icon_signal

    def handler(*args, **kwargs):
        return icon

    icon_signal.connect(handler, dispatch_uid="test_icon")

    yield icon

    icon_signal.disconnect(dispatch_uid="test_icon")


@pytest.fixture
def tags_signal():
    tags = ["skull", "warning"]

    from django_ntfy import tags_signal

    def handler(*args, **kwargs):
        return tags

    tags_signal.connect(handler, dispatch_uid="test_tags")

    yield tags

    tags_signal.disconnect(dispatch_uid="test_tags")


@pytest.fixture
def actions_signal():
    actions = [
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

    from django_ntfy import actions_signal

    def handler(*args, **kwargs):
        return actions

    actions_signal.connect(handler, dispatch_uid="test_actions")

    yield actions

    actions_signal.disconnect(dispatch_uid="test_actions")


@pytest.fixture
def priority_signal():
    priority = 5

    from django_ntfy import priority_signal

    def handler(*args, **kwargs):
        return priority

    priority_signal.connect(handler, dispatch_uid="test_icon")

    yield priority

    priority_signal.disconnect(dispatch_uid="test_icon")


@pytest.fixture
def clear_cache():
    from django.core.cache import cache

    cache.clear()
