from django.core import mail

from django_ntfy import EmailBackend


def test_exponential_rate_limit(
    settings, use_exponential_ratelimit_backend, monkeypatch, clear_cache
):
    def check(sent: bool, subject_suffix: str):
        tmp = {"called": False}

        def hook(self, email_messages):
            assert len(email_messages) == 1
            assert email_messages[0].subject == "Sub" + subject_suffix
            tmp["called"] = True
            return 1

        with monkeypatch.context() as m:
            m.setattr(EmailBackend, 'send_messages', hook)

            if sent:
                assert mail.send_mail("Sub", "Body", "from@example.com", ["to@example.com"]) == 1
                assert tmp["called"] is True
            else:
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
