from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from hc.api.models import Check
from hc import settings


class LoginTestCase(TestCase):

    def test_it_sends_link(self):
        total_users_before = User.objects.count()
        check = Check()
        check.save()

        session = self.client.session
        session["welcome_code"] = str(check.code)
        session.save()

        form = {"email": "alice@example.org"}

        r = self.client.post("/accounts/login/", form)
        assert r.status_code == 302

        ### Assert that a user was created
        total_users_after = User.objects.count()
        self.assertEqual(total_users_after, total_users_before + 1)

        # And email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Log in to healthchecks.io')
        ### Assert contents of the email body
        self.assertIn("To log into healthchecks.io, please open the link below:". format(settings.SITE_ROOT), mail.outbox[0].body)
        ### Assert that check is associated with the new user
        check.refresh_from_db()
        author = User.objects.get(email="alice@example.org")
        self.assertEqual(check.user.id, author.id)

    def test_it_pops_bad_link_from_session(self):
        self.client.session["bad_link"] = True
        self.client.get("/accounts/login/")
        assert "bad_link" not in self.client.session

        ### Any other tests?

