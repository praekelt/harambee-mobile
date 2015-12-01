from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from my_auth.models import Harambee
from core.models import Page
from content.models import Journey, Module, JourneyModuleRel, Level, LevelQuestion, LevelQuestionOption,\
    HarambeeJourneyModuleRel, HarambeeJourneyModuleLevelRel, HarambeeQuestionAnswer
from datetime import datetime
from mock import patch
from views import ForgotPinView
from harambee.metrics import create_json_stats


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
                                                                     self.question, correct=False)

    @patch('harambee.views.get_harambee_by_id')
    @patch('harambee.views.get_lps')
    def test_join(self, get_lps_mock, get_harambee_by_id_mock):
        resp = self.client.get(reverse("auth.join"))
        page = Page.objects.get(slug="join")

        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        #NO DATA
        resp = self.client.post(
            reverse('auth.join'),
            data={},
            follow=True
        )
        self.assertContains(resp, 'JOIN')
        self.assertContains(resp, 'This field is required', 2)

        username = '9876543210123'
        password = '5555'

        #EXCEPTION
        get_harambee_by_id_mock.side_effect = ValueError
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertRedirects(resp, '/no_match/')

        #NO MATCH
        get_harambee_by_id_mock.side_effect = None
        get_harambee_by_id_mock.return_value = None
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertRedirects(resp, '/no_match/')

        harambee = dict()
        harambee['name'] = 'Tom'
        harambee['surname'] = 'Riddle'
        harambee['candidateId'] = '147258369'
        harambee['emailAddr'] = 'tomriddle@hogwarts.com'
        harambee['contactNo'] = '0801234567'

        get_lps_mock.return_value = 5

        #MATCH
        get_harambee_by_id_mock.return_value = harambee
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertContains(resp, "WELCOME, %s" % harambee['name'].upper())
        self.assertRedirects(resp, '/intro/')

        #LOGOUT
        resp = self.client.get(reverse('auth.logout'), follow=True)
        page = Page.objects.get(slug="welcome")
        self.assertRedirects(resp, '/%s/' % page.slug)
        self.assertContains(resp, page.title)

        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertRedirects(resp, '/login/')

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
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        #LOGOUT
        resp = self.client.get(reverse('auth.logout'), follow=True)
        page = Page.objects.get(slug="welcome")
        self.assertRedirects(resp, '/%s/' % page.slug)
        self.assertContains(resp, page.title)

        #HOMEPAGE
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "HELLO %s" % self.harambee.first_name.upper())

    @patch('harambee.views.ForgotPinView.generate_random_pin')
    def test_forgot_pin(self, generate_random_pin_mock):
        resp = self.client.get(reverse("auth.forgot_pin"))
        page = Page.objects.get(slug="forgot_pin")
        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        #NO DATA
        resp = self.client.post(
            reverse('auth.forgot_pin'),
            data={}
        )
        self.assertContains(resp, "This field is required")

        #INVALID ID
        resp = self.client.post(
            reverse('auth.forgot_pin'),
            data={'username': '9999999999999'}
        )
        self.assertContains(resp, "User does not exist")

        #REGISTERED ID
        new_pin = '9876'
        generate_random_pin_mock.return_value = new_pin
        resp = self.client.post(
            reverse('auth.forgot_pin'),
            data={'username': self.harambee.username},
            follow=True
        )
        page = Page.objects.get(slug="send_pin")
        self.assertContains(resp, page.heading.upper())
        self.assertRedirects(resp, '/send_pin/')

        #LOGIN WITH NEW PIN
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': new_pin },
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

    def test_send_pin(self):
        resp = self.client.get("/send_pin", follow=True)
        page = Page.objects.get(slug="send_pin")

        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

    def test_generate_random_pin(self):
        resp = ForgotPinView.generate_random_pin()
        self.assertEquals(len(resp), 4)

    def test_menu(self):
        resp = self.client.get(reverse("misc.menu"), follow=True)
        page = Page.objects.get(slug="login")

        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)

        resp = self.client.get(reverse("misc.menu"), follow=True)
        self.assertContains(resp, "LOG OUT")
        self.assertContains(resp, "MY PROFILE")
        self.assertContains(resp, "HOME")
        self.assertContains(resp, "SEARCH")
        self.assertContains(resp, "HELP")
        self.assertContains(resp, "ABOUT")
        self.assertEquals(resp.status_code, 200)

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

    def test_profile(self):
        resp = self.client.get(reverse("auth.profile"), follow=True)
        page = Page.objects.get(slug="login")

        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)

        resp = self.client.get(reverse("auth.profile"), follow=True)
        self.assertContains(resp, self.harambee.first_name + " " + self.harambee.last_name)
        self.assertContains(resp, self.harambee.mobile)

    def test_change_pin(self):
        resp = self.client.get(reverse("auth.change_pin"), follow=True)
        page = Page.objects.get(slug="login")

        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        new_password = "1111"

        self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
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
                'existingPIN': self.password,
                'newPIN': "0000",
                'newPIN2': new_password},
            follow=True)
        self.assertContains(resp, "PINs do not match")

        resp = self.client.post(
            reverse('auth.change_pin'),
            data={
                'existingPIN': self.password,
                'newPIN': new_password,
                'newPIN2': new_password},
            follow=True)
        self.assertRedirects(resp, '/successful_pin_change/')
        page = Page.objects.get(slug='successful_pin_change')
        self.assertContains(resp, page.heading.upper())

        resp = self.client.get(reverse('auth.logout'), follow=True)
        page = Page.objects.get(slug="welcome")
        self.assertRedirects(resp, '/%s/' % page.slug)

        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': new_password},
            follow=True)
        self.assertContains(resp, "HELLO %s" % self.harambee.first_name.upper())

    def test_change_number(self):
        resp = self.client.get(reverse("auth.change_number"), follow=True)
        page = Page.objects.get(slug="login")

        self.assertContains(resp, page.heading.upper())
        self.assertEquals(resp.status_code, 200)

        self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
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

        with patch('harambee.views.update_mobile_number'):
            new_number = '0791234567'
            resp = self.client.post(
                reverse('auth.change_number'),
                data={
                    'mobile': new_number},
                follow=True)
            self.assertRedirects(resp, '/successful_mobile_change/')
            page = Page.objects.get(slug='successful_mobile_change')
            self.assertContains(resp, page.heading.upper())

            user = Harambee.objects.get(username=self.harambee.username)
            self.assertEqual(user.mobile, new_number)

    def test_search(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        resp = self.client.get(reverse('misc.search'))
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, 'SEARCH')

        resp = self.client.get(reverse('misc.search'),
                                data={
                                    'q': 'search'
                                },
                                follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, 'SEARCH')
        self.assertContains(resp, 'No results found.')

    def test_completed_modules(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        resp = self.client.get(reverse('content.completed_modules'))
        self.assertEquals(resp.status_code, 200)
        page = Page.objects.get(slug='completed_modules')
        self.assertContains(resp, page.heading.upper())

    #TODO: check if it's displaying all the modules
    def test_journey_home(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        resp = self.client.get('/journey_home/%s' % self.journey.slug, follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.journey.name.upper())

    def test_module_intro(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        resp = self.client.get('/module_intro/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name)

    def test_module_home(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name)

        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name.upper())

    def test_module_end(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        resp = self.client.get('/module_end/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name)

    #TODO test for levels that don't exist
    def test_level_intro(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        #NEED TO GO HOME TO CREATE HARAMBEEJOUNREYMODULEREL
        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name)

        resp = self.client.get('/level_intro/%s/%s/%d' % (self.journey.slug, self.module.slug, self.level.id),
                               follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())

    #TODO: same as above
    def test_level_end(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        #NEED TO GO HOME TO CREATE HARAMBEEJOUNREYMODULEREL
        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name)

        resp = self.client.get('/level_intro/%s/%s/%d' % (self.journey.slug, self.module.slug, self.level.id),
                               follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())

        resp = self.client.get('/level_end/')
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())

    def test_question(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        #NEED TO GO HOME TO CREATE HARAMBEEJOUNREYMODULEREL
        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name)

        resp = self.client.get('/level_intro/%s/%s/%d' % (self.journey.slug, self.module.slug, self.level.id),
                               follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())

        resp = self.client.get(reverse('content.question'))
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(reverse('content.question'),
                                data={},
                                follow=True)
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(reverse('content.question'),
                                data={
                                    'answer': 99
                                },
                                follow=True)
        self.assertEquals(resp.status_code, 200)

    def test_correct_answer(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        #NEED TO GO HOME TO CREATE HARAMBEEJOUNREYMODULEREL
        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name)

        resp = self.client.get('/level_intro/%s/%s/%d' % (self.journey.slug, self.module.slug, self.level.id),
                               follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())

        resp = self.client.get(reverse('content.question'))
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(reverse('content.question'),
                                data={
                                    'answer': self.correct_question_option.id
                                },
                                follow=True)
        self.assertEquals(resp.status_code, 200)

    def test_incorrect_answer(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        #NEED TO GO HOME TO CREATE HARAMBEEJOUNREYMODULEREL
        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name)

        resp = self.client.get('/level_intro/%s/%s/%d' % (self.journey.slug, self.module.slug, self.level.id),
                               follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())

        resp = self.client.get(reverse('content.question'))
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(reverse('content.question'),
                                data={
                                    'answer': self.incorrect_question_option.id
                                },
                                follow=True)
        self.assertEquals(resp.status_code, 200)


class MetricsTests(TestCase):

    def create_harambee(self, username, mobile, candidate_id, lps=0, **kwargs):
        return Harambee.objects.create(username=username, mobile=mobile, candidate_id=candidate_id, lps=lps, **kwargs)

    def create_journey(self, name, start_date=datetime.now(), **kwargs):
        return Journey.objects.create(name=name, slug=name, title=name, search=name, start_date=start_date, **kwargs)

    def create_module(self, name, journey, minimum_questions, minimum_percentage, start_date=datetime.now(), **kwargs):
        module = Module.objects.create(name=name, slug=name, title=name, minimum_questions=minimum_questions,
                                       minimum_percentage=minimum_percentage, start_date=start_date, **kwargs)
        return JourneyModuleRel.objects.create(journey=journey, module=module)

    def create_level(self, name, module, order, question_order=Level.ORDERED, **kwargs):
        return Level.objects.create(name=name, module=module, order=order, question_order=question_order, **kwargs)

    def create_question(self, name, level, order, **kwargs):
        return LevelQuestion.objects.create(name=name, level=level, order=order, **kwargs)

    def create_question_option(self, name, question, correct, **kwargs):
        return LevelQuestionOption.objects.create(name=name, question=question, correct=correct, **kwargs)

    def create_set_of_questions_and_options(self, level, number):
        question_name = 'question_%s'
        option_name = 'q_%s_option_%s'
        result = list()

        for i in range(number):
            d = dict()
            question = self.create_question(question_name % i, level, i+1)
            d['question'] = question
            d['correct'] = self.create_question_option(option_name % (i, 1), question, True)
            d['incorrect'] = self.create_question_option(option_name % (i, 2), question, False)
            result.append(d)

        return result

    def create_harambee_journey_module_rel(self, harambee, journey_module_rel, **kwargs):
        return HarambeeJourneyModuleRel.objects.create(harambee=harambee, journey_module_rel=journey_module_rel,
                                                       **kwargs)

    def create_harambee_journey_module_level_rel(self, harambee_journey_module_rel, level, level_attempt=1,  **kwargs):
        return HarambeeJourneyModuleLevelRel.objects.create(harambee_journey_module_rel=harambee_journey_module_rel,
                                                            level=level, level_attempt=level_attempt, **kwargs)

    def answer_question(self, harambee, question, option_selected, harambee_level_rel, date_answered=datetime.now()):
        return HarambeeQuestionAnswer.objects.create(harambee=harambee, question=question,
                                                     option_selected=option_selected,
                                                     harambee_level_rel=harambee_level_rel,
                                                     date_answered=date_answered)

    def setUp(self):
        TOTAL_HARAMBEES = 4
        harambee_list = list()

        for i in range(TOTAL_HARAMBEES):
            harambee = dict()
            harambee['harambee'] = self.create_harambee('user_%d' % i, '070123456%d' % i, i, )
            harambee_list.append(harambee)

        journey_list = list()
        module_list = list()
        level_list = list()

        for i in range(4):
            journey = self.create_journey('%d_journey' % i)
            journey_list.append(journey)

            for j in range(2):
                journey_modle_rel = self.create_module('%d_%d_module' % (i, j), journey, 2, 2)
                module_list.append(journey_modle_rel)

                for z in range(TOTAL_HARAMBEES):
                    a = harambee_list[z]['harambee']
                    harambee_list[z]['h_j_m_rel'] = self.create_harambee_journey_module_rel(a, journey_modle_rel)

                for k in range(3):
                    level = self.create_level('%d_%d_%d_level' % (i, j, k), journey_modle_rel.module, k)
                    level_list.append(level)

                    for z in range(TOTAL_HARAMBEES):
                        rel = harambee_list[z]['h_j_m_rel']
                        harambee_list[z]['h_j_m_l_rel'] = self.create_harambee_journey_module_level_rel(rel, level)

                    for l in range(10):
                        question = self.create_question('%d_%d_%d_%d_question' % (i, j, k, l), level, l)
                        correct = self.create_question_option('%d_%d_%d_%d_correct' % (i, j, k, l), question, True)
                        incorrect = self.create_question_option('%d_%d_%d_%d_incorrect' % (i, j, k, l), question, True)

                        self.answer_question(harambee_list[0]['harambee'], question, correct,
                                             harambee_list[0]['h_j_m_l_rel'])

                        self.answer_question(harambee_list[1]['harambee'], question, incorrect,
                                             harambee_list[1]['h_j_m_l_rel'])

                        self.answer_question(harambee_list[2]['harambee'], question, incorrect,
                                             harambee_list[2]['h_j_m_l_rel'])

                        self.answer_question(harambee_list[3]['harambee'], question, correct,
                                             harambee_list[3]['h_j_m_l_rel'])

    def test_metrics(self):
        create_json_stats()