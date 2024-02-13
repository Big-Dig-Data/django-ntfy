import responses
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from responses import matchers


def test_exponential_rate_limit(
    settings, use_exponential_ratelimit_backends, monkeypatch, clear_cache
):
    settings.EMAIL_EXPONENTIAL_RATE_LIMIT_BACKENDS = [
        'django.core.mail.backends.smtp.EmailBackend',
        'django_ntfy.NtfyBackend',
    ]

    def check(sent: bool, subject_suffix: str):
        tmp = {"called": False}

        def hook(self, email_messages):
            assert len(email_messages) == 1
            assert email_messages[0].subject == "Sub" + subject_suffix
            tmp["called"] = True
            return 1

        if sent:
            with monkeypatch.context() as m, responses.RequestsMock() as rsps:
                m.setattr(EmailBackend, 'send_messages', hook)

                rsps.post(
                    settings.NTFY_BASE_URL,
                    status=200,
                    match=[
                        matchers.json_params_matcher(
                            {
                                "message": "Body",
                                "title": "Sub" + subject_suffix,
                                "topic": "django-ntfy",
                            }
                        ),
                    ],
                )
                assert mail.send_mail("Sub", "Body", "from@example.com", ["to@example.com"]) == 2
                assert tmp["called"] is True
        else:
            with monkeypatch.context() as m:
                assert mail.send_mail("Sub", "Body", "from@example.com", ["to@example.com"]) == 0
                assert tmp["called"] is False

    check(True, '')
    check(True, '')
    check(False, '')
    check(True, ' (2)')
    check(False, '')
    check(False, '')
    check(False, '')
    check(True, ' (4)')
    check(False, '')
    check(False, '')
    check(False, '')
    check(False, '')
    check(False, '')
    check(False, '')
    check(False, '')
    check(True, ' (8)')


def test_no_exponential_rate_limit(
    settings, use_exponential_ratelimit_backends, monkeypatch, clear_cache
):
    settings.EMAIL_EXPONENTIAL_RATE_LIMIT_TIMEOUT = 0
    settings.EMAIL_EXPONENTIAL_RATE_LIMIT_BACKENDS = [
        'django.core.mail.backends.smtp.EmailBackend',
        'django_ntfy.NtfyBackend',
    ]

    for _i in range(20):
        tmp = {"called": False}

        def hook(self, email_messages):
            assert len(email_messages) == 1
            assert email_messages[0].subject == "Sub"
            tmp["called"] = True
            return 1

        with monkeypatch.context() as m, responses.RequestsMock() as rsps:
            m.setattr(EmailBackend, 'send_messages', hook)
            rsps.post(
                settings.NTFY_BASE_URL,
                status=200,
                match=[
                    matchers.json_params_matcher(
                        {
                            "message": "Body",
                            "title": "Sub",
                            "topic": "django-ntfy",
                        }
                    ),
                ],
            )
            assert mail.send_mail("Sub", "Body", "from@example.com", ["to@example.com"]) == 2
            assert tmp["called"] is True
