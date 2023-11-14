import pytest


@pytest.fixture
def use_ntfy_email_backend(settings):
    # we need to explicitly override it here
    settings.EMAIL_BACKEND = 'django_ntfy.NtfyBackend'


@pytest.fixture
def topic_signal():
    topic = "altered-topic"

    def handler(*args, **kwargs):
        return topic

    from django_ntfy import topic_signal

    topic_signal.connect(handler, dispatch_uid="test_topic")

    yield topic

    topic_signal.disconnect(dispatch_uid="test_topic")
