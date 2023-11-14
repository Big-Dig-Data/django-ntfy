import responses
from django.core import mail
from responses import matchers


def test_basic(settings, use_ntfy_email_backend):
    with responses.RequestsMock() as rsps:
        rsps.post(
            settings.NTFY_BASE_URL,
            status=200,
            match=[
                matchers.json_params_matcher(
                    {
                        "message": "Body",
                        "title": "Sub",
                        "topic": "django-ntfy",  # Default topic from settings
                    }
                ),
            ],
        )
        assert mail.send_mail("Sub", "Body", "from@example.com", ["to@example.com"]) == 1


def test_custom_topic(settings, use_ntfy_email_backend, topic_signal):
    with responses.RequestsMock() as rsps:
        rsps.post(
            settings.NTFY_BASE_URL,
            status=200,
            match=[
                matchers.json_params_matcher(
                    {
                        "message": "Body",
                        "title": "Sub",
                        "topic": "altered-topic",  # Default topic from settings
                    }
                ),
            ],
        )
        assert mail.send_mail("Sub", "Body", "from@example.com", ["to@example.com"]) == 1


def test_attachments(settings, use_ntfy_email_backend):
    settings.NTFY_SEND_ATTACHMENTS = True

    with mail.get_connection() as connection, responses.RequestsMock() as rsps:
        rsps.post(
            settings.NTFY_BASE_URL,
            status=200,
            match=[
                matchers.json_params_matcher(
                    {
                        "message": "Body1",
                        "title": "Subject1",
                        "topic": "django-ntfy",  # Default topic from settings
                    }
                ),
            ],
        )

        rsps.put(
            f"{settings.NTFY_BASE_URL}/django-ntfy",
            status=200,
            match=[
                matchers.header_matcher(
                    {"Filename": "File1.txt"},
                )
            ],
        )

        rsps.put(
            f"{settings.NTFY_BASE_URL}/django-ntfy",
            status=200,
            match=[
                matchers.header_matcher(
                    {"Filename": "File2.txt"},
                )
            ],
        )

        message = mail.EmailMessage(
            subject="Subject1",
            body="Body1",
            from_email="from@example.com",
            to=["to@example.com"],
            connection=connection,
        )
        message.attach("File1.txt", "Content1", "text/plain")
        message.attach("File2.txt", "Content1", "text/plain")
        message.send()
