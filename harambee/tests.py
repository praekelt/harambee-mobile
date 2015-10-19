from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from my_auth.models import Harambee
from core.models import Page


class GeneralTests(TestCase):

    client = Client()

    def test_welcome(self):
        resp = self.client.get("/welcome", follow=True)
        page = Page.objects.get(slug="welcome")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

    def test_why_id(self):
        resp = self.client.get("/why_id", follow=True)
        page = Page.objects.get(slug="why_id")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

    def test_no_match(self):
        resp = self.client.get("/no_match", follow=True)
        page = Page.objects.get(slug="no_match")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

    def test_send_pin(self):
        resp = self.client.get("/send_pin", follow=True)
        page = Page.objects.get(slug="send_pin")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

    def test_login(self):
        resp = self.client.get(reverse("auth.login"))
        page = Page.objects.get(slug="login")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(
            reverse('auth.login'),
            data={},
            follow=True
        )

        self.assertContains(resp, "This field is required.")

        username = "0123456789123"
        password = "1234"

        user = Harambee.objects.create(username=username,
                                       first_name="Tester",
                                       last_name="McTest",
                                       mobile="0123456789",
                                       lps=10)
        user.set_password(raw_password=password)
        user.save()

        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': username,
                'password': password},
            follow=True)

        self.assertContains(resp, "Welcome, %s" % user.first_name)

        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': username,
                'password': password},
            follow=True)

        self.assertContains(resp, "Hello, %s" % user.first_name)

        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': "1234567890123",
                'password': password},
            follow=True
        )

        self.assertContains(resp, "User does not exist")

        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': username,
                'password': "1233"},
            follow=True
        )

        self.assertContains(resp, "Password is invalid")

    def test_forgot_pin(self):
        resp = self.client.get(reverse("auth.forgot_pin"))
        page = Page.objects.get(slug="forgot_pin")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(
            reverse('auth.forgot_pin'),
            data={},
            follow=True
        )

        self.assertContains(resp, "This field is required")

        username = "0123456789123"

        Harambee.objects.create(username=username,
                                first_name="Tester",
                                last_name="McTest",
                                mobile="0123456789",
                                lps=10)

        resp = self.client.post(
            reverse('auth.forgot_pin'),
            data={'username': username},
            follow=True)

        page = Page.objects.get(slug="send_pin")
        user = Harambee.objects.get(username=username)
        self.assertContains(resp, page.heading)
        self.assertEquals(user.password, "0000")

        resp = self.client.post(
            reverse('auth.forgot_pin'),
            data={'username': "1234567890123"},
            follow=True)

        self.assertContains(resp, "User does not exist")

    def test_join(self):
        resp = self.client.get(reverse("auth.join"))
        page = Page.objects.get(slug="join")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(
            reverse('auth.join'),
            data={},
            follow=True
        )

        self.assertContains(resp, "Join")

        username = "0123456789123"
        password = "1234"

        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True)

        page = Page.objects.get(slug="no_match")
        self.assertContains(resp, page.heading)

    def test_profile(self):
        resp = self.client.get(reverse("auth.profile"), follow=True)
        page = Page.objects.get(slug="login")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

        username = "0123456789123"
        password = "1234"

        user = Harambee.objects.create(username=username,
                                       first_name="Tester",
                                       last_name="McTest",
                                       mobile="0123456789",
                                       lps=10)
        user.set_password(raw_password=password)
        user.save()

        self.client.post(
            reverse('auth.login'),
            data={
                'username': username,
                'password': password},
            follow=True)

        resp = self.client.get(reverse("auth.profile"), follow=True)
        self.assertContains(resp, user.first_name + " " + user.last_name)

    def test_change_pin(self):
        resp = self.client.get(reverse("auth.change_pin"), follow=True)
        page = Page.objects.get(slug="login")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

        username = "0123456789123"
        password = "1234"

        user = Harambee.objects.create(username=username,
                                       first_name="Tester",
                                       last_name="McTest",
                                       mobile="0123456789",
                                       lps=10)
        user.set_password(raw_password=password)
        user.save()

        new_password = "1111"

        self.client.post(
            reverse('auth.login'),
            data={
                'username': username,
                'password': password},
            follow=True)

        resp = self.client.post(
            reverse('auth.change_pin'),
            data={},
            follow=True)

        self.assertContains(resp, "This field is required")

        resp = self.client.post(
            reverse('auth.change_pin'),
            data={
                'existingPIN': "0000",
                'newPIN': new_password,
                'newPIN2': new_password},
            follow=True)

        self.assertContains(resp, "Existing PIN incorrect")

        resp = self.client.post(
            reverse('auth.change_pin'),
            data={
                'existingPIN': password,
                'newPIN': "0000",
                'newPIN2': new_password},
            follow=True)

        self.assertContains(resp, "PINs do not match")

        self.client.post(
            reverse('auth.change_pin'),
            data={
                'existingPIN': password,
                'newPIN': new_password,
                'newPIN2': new_password},
            follow=True)

        user = Harambee.objects.get(username=username)
        self.assertEqual(user.password, new_password)

    def test_change_number(self):
        resp = self.client.get(reverse("auth.change_number"), follow=True)
        page = Page.objects.get(slug="login")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

        username = "0123456789123"
        password = "1234"

        user = Harambee.objects.create(username=username,
                                       first_name="Tester",
                                       last_name="McTest",
                                       mobile="0123456789",
                                       lps=10)
        user.set_password(raw_password=password)
        user.save()

        self.client.post(
            reverse('auth.login'),
            data={
                'username': username,
                'password': password},
            follow=True)

        resp = self.client.post(
            reverse('auth.change_number'),
            data={},
            follow=True)

        self.assertContains(resp, "This field is required")

        resp = self.client.post(
            reverse('auth.change_number'),
            data={
                'mobile': '00123456789'},
            follow=True)

        self.assertContains(resp, "Phone number to long")

        resp = self.client.post(
            reverse('auth.change_number'),
            data={
                'mobile': '123456789'},
            follow=True)

        self.assertContains(resp, "Phone number to short")

        self.client.post(
            reverse('auth.change_number'),
            data={
                'mobile': '0123456789'},
            follow=True)

        user = Harambee.objects.get(username=username)
        self.assertEqual(user.mobile, '0123456789')

    def test_menu(self):
        resp = self.client.get(reverse("misc.menu"), follow=True)
        page = Page.objects.get(slug="login")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)

        username = "0123456789123"
        password = "1234"

        user = Harambee.objects.create(username=username,
                                       first_name="Tester",
                                       last_name="McTest",
                                       mobile="0123456789",
                                       lps=10)
        user.set_password(raw_password=password)
        user.save()

        self.client.post(
            reverse('auth.login'),
            data={
                'username': username,
                'password': password},
            follow=True)

        resp = self.client.get(reverse("misc.menu"), follow=True)
        page = Page.objects.get(slug="menu")
        self.assertContains(resp, page.heading)
        self.assertEquals(resp.status_code, 200)