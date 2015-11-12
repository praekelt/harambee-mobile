from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from my_auth.models import Harambee
from core.models import Page
from content.models import Journey, Module, JourneyModuleRel, Level, LevelQuestion, LevelQuestionOption
from datetime import datetime


class GeneralTests(TestCase):

    def create_harambee(self, mobile, username, candidate_id, lps=0, **kwargs):
        return Harambee.objects.create(mobile=mobile, username=username, candidate_id=candidate_id, lps=lps, **kwargs)

    def create_journey(self, name, slug, title, start_date=datetime.now(), **kwargs):
        return Journey.objects.create(name=name, slug=slug, title=title, start_date=start_date, **kwargs)

    def create_module(self, name, slug, title, minimum_questions, minimum_percentage, **kwargs):
        return Module.objects.create(name=name, slug=slug, title=title, minimum_questions=minimum_questions,
                                     minimum_percentage=minimum_percentage, **kwargs)

    def add_module_to_journey(self, journey, module):
        return JourneyModuleRel.objects.create(journey=journey, module=module)

    def create_level(self, name, module, order, **kwargs):
        return Level.objects.create(name=name, module=module, order=order, **kwargs)

    def create_question(self, name, level, order, question_content='Question', **kwargs):
        return LevelQuestion.objects.create(name=name, level=level, order=order, question_content=question_content,
                                            **kwargs)

    def create_question_option(self, name, question, content='Answer', correct=True):
        return LevelQuestionOption.objects.create(name=name, question=question, content=content, correct=correct)

    def setUp(self):
        self.harambee = self.create_harambee('0701234567', '1234567890123', '1234567890', first_name="Jamal",
                                             last_name="Lyon")
        self.password = '1234'
        self.harambee.set_password(self.password)
        self.harambee.save()

        self.journey = self.create_journey('Sales', 'sales', 'Sales')
        self.module = self.create_module('Customer Service', 'customer-service', 'Customer Service', 1,
                                         Module.PERCENT_50)
        self.add_module_to_journey(self.journey, self.module)

        self.level = self.create_level('Level 1', self.module, 1)
        self.question = self.create_question('Level 1 - Question 1', self.level, 1)
        self.correct_question_option = self.create_question_option('Level 1 - Question 1 - Correct Option',
                                                                   self.question)
        self.incorrect_question_option = self.create_question_option('Level 1 - Question 1 - Incorrect Option',
                                                                     self.question, correct=True)

    client = Client()

    def test_welcome(self):
        resp = self.client.get("/welcome", follow=True)
        page = Page.objects.get(slug="welcome")
        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

    def test_why_id(self):
        resp = self.client.get("/why_id", follow=True)
        page = Page.objects.get(slug="why_id")
        self.assertContains(resp, page.heading.upper())
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
        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        Harambee.objects.get(username=self.harambee.username)

        #INVALID FORM
        resp = self.client.post(
            reverse('auth.login'),
            data={},
            follow=True
        )
        self.assertContains(resp, "This field is required.", 2)

        #INCORRECT CREDENTIALS
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': "9999999999999",
                'password': '0000'},
            follow=True
        )
        self.assertContains(resp, 'Incorrect ID/PIN.')

        #INTRO PAGE
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "Welcome, %s" % self.harambee.first_name)

        #HOMEPAGE
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "Hello %s" % self.harambee.first_name)

    def test_forgot_pin(self):
        resp = self.client.get(reverse("auth.forgot_pin"))
        page = Page.objects.get(slug="forgot_pin")
        self.assertContains(resp, page.heading.upper())
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
        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(
            reverse('auth.join'),
            data={},
            follow=True
        )

        self.assertContains(resp, "JOIN")

        username = "0000000000000"
        password = "1234"

        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True)

        page = Page.objects.get(slug="intro")
        user = Harambee.objects.get(username=username)
        self.assertContains(resp, "Welcome, %s" % user.first_name)

    def test_profile(self):
        resp = self.client.get(reverse("auth.profile"), follow=True)
        page = Page.objects.get(slug="login")
        self.assertContains(resp, page.heading.upper())
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
        self.assertContains(resp, page.heading.upper())
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
        self.assertContains(resp, page.heading.upper())
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

        # self.client.post(
        #     reverse('auth.change_number'),
        #     data={
        #         'mobile': '0123456789'},
        #     follow=True)
        #
        # user = Harambee.objects.get(username=username)
        # self.assertEqual(user.mobile, '0123456789')

    def test_menu(self):
        resp = self.client.get(reverse("misc.menu"), follow=True)
        page = Page.objects.get(slug="login")
        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        username = "0000000000000"
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
        self.assertContains(resp, "LOG OUT")
        self.assertContains(resp, "MY PROFILE")
        self.assertContains(resp, "HOME")
        self.assertContains(resp, "SEARCH")
        self.assertContains(resp, "HELP")
        self.assertContains(resp, "ABOUT")
        self.assertEquals(resp.status_code, 200)

