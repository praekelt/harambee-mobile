from django.test import TestCase
from django.core.urlresolvers import reverse
from my_auth.models import Harambee, CustomUser
from core.models import Page, HelpPage
from content.models import Journey, Module, JourneyModuleRel, Level, LevelQuestion, LevelQuestionOption,\
    HarambeeJourneyModuleRel, HarambeeJourneyModuleLevelRel, HarambeeQuestionAnswer
from datetime import datetime
from mock import patch
from views import ForgotPinView
from harambee.metrics import create_json_stats
from httplib2 import ServerNotFoundError
from harambee.tasks import email_stats


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

    def create_level(self, name, module, order, question_order=Level.ORDERED, **kwargs):
        return Level.objects.create(name=name, module=module, order=order, question_order=question_order, **kwargs)

    def create_question(self, name, level, order, question_content='Question', **kwargs):
        return LevelQuestion.objects.create(name=name, level=level, order=order, question_content=question_content,
                                            **kwargs)

    def create_question_option(self, name, question, content='Answer', correct=True):
        return LevelQuestionOption.objects.create(name=name, question=question, content=content, correct=correct)

    def create_help_page(self, slug, title, heading, content, description, activate=datetime.now(), deactivate=None,
                         show=True):
        return HelpPage.objects.create(slug=slug, title=title, heading=heading, content=content,
                                       description=description, activate=activate, deactivate=deactivate, show=show)

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

        username = '0000000000000'
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

        #EXCEPTION
        get_harambee_by_id_mock.side_effect = ServerNotFoundError
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertContains(resp, 'SERVER UNAVAILABLE')

        #INVALID ID
        username = '1234'
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertContains(resp, 'ID number is incorrect. An ID number is 13 digits only. Please try again.')
        self.assertEquals(resp.status_code, 200)

        username = '1234567890123'
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertContains(resp, 'ID number is incorrect. An ID number is 13 digits only. Please try again.')
        self.assertEquals(resp.status_code, 200)

        #NO MATCH
        username = '0000000000000'
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

        #INVALID PIN
        password = '12m'
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, 'PIN needs to be 4 digits long.')

        harambee = dict()
        harambee['name'] = 'Tom'
        harambee['surname'] = 'Riddle'
        can_id = '147258369'
        harambee['candidateId'] = can_id
        harambee['emailAddr'] = 'tomriddle@hogwarts.com'
        harambee['contactNo'] = '0801234567'
        get_harambee_by_id_mock.return_value = harambee

        #EXCEPTION
        password = '5555'
        get_lps_mock.side_effect = ServerNotFoundError
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertContains(resp, 'SERVER UNAVAILABLE')

        get_lps_mock.side_effect = None
        get_lps_mock.return_value = 5

        #EXISTING CANDIDATE_ID
        har_2 = Harambee.objects.create_user('3698521478965', candidate_id=can_id, lps=0)
        resp = self.client.post(
            reverse('auth.join'),
            data={
                'username': username,
                'password': password},
            follow=True
        )
        self.assertContains(resp, "REGISTRATION ERROR")
        har_2.delete()

        #MATCH
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
    @patch('harambee.views.send_immediate_sms')
    def test_forgot_pin(self, send_sms_mock, generate_random_pin_mock):
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
                'password': new_pin},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        #FAILED TO SEND SMS
        new_pin = '8520'
        generate_random_pin_mock.return_value = new_pin
        send_sms_mock.side_effect = ValueError
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
                'password': new_pin},
            follow=True)
        self.assertContains(resp, "HELLO %s" % self.harambee.first_name.upper())

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

        jou_mod_rel = JourneyModuleRel.objects.get(journey=self.journey, module=self.module)
        har_jou_mod_rel = HarambeeJourneyModuleRel.objects.get(harambee=self.harambee,
                                                               journey_module_rel=jou_mod_rel)
        HarambeeJourneyModuleLevelRel.objects.filter(harambee_journey_module_rel=har_jou_mod_rel).delete()

        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name.upper())

    #TODO: test for levels that don't exist
    def test_complete_module(self):
        """
        Test the complete flow.
        """
        #ADD MORE QUESTIONS
        questions = list()
        questions.append(self.question)
        answers = list()
        answers.append(self.correct_question_option)
        for i in range(2, 6):
            q = self.create_question('question_%s' % i, self.level, i)
            answers.append(self.create_question_option('q_%d_o' % i, q))
            questions.append(q)

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

        #NEW ACTIVE REL
        resp = self.client.get('/level_intro/%s/%s/%d' % (self.journey.slug, self.module.slug, self.level.pk),
                               follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())
        self.assertContains(resp, self.level.text)

        resp = self.client.get('/module_home/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name.upper())

        #ACTIVE REL
        resp = self.client.get('/level_intro/%s/%s/%d' % (self.journey.slug, self.module.slug, self.level.pk),
                               follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())
        self.assertContains(resp, self.level.text)

        for i in range(0, 4):
            resp = self.client.get(reverse('content.question'), follow=True)
            self.assertContains(resp, self.level.name.upper())
            resp = self.client.post(reverse('content.question'),
                                    data={
                                        'answer': answers[i].id
                                    },
                                    follow=True)
            self.assertEquals(resp.status_code, 200)
            self.assertContains(resp, 'CORRECT')

        resp = self.client.get(reverse('content.question'), follow=True)
        self.assertContains(resp, self.level.name.upper())
        resp = self.client.post(reverse('content.question'),
                                data={
                                    'answer': answers[4].id
                                },
                                follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, 'CORRECT')
        self.assertContains(resp, 'WELL DONE!')

        resp = self.client.get(reverse('content.question'), follow=True)
        self.assertRedirects(resp, '/level_end/')
        self.assertContains(resp, self.level.name.upper())
        self.assertContains(resp, 'LEVEL COMPLETE')

        #MODULE END VIEW
        resp = self.client.get('/module_end/%s/%s/' % (self.journey.slug, self.module.slug), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.module.name.upper())

        #COMPLETED MODULES VIEW
        resp = self.client.get(reverse('content.completed_modules'))
        self.assertEquals(resp.status_code, 200)
        page = Page.objects.get(slug='completed_modules')
        self.assertContains(resp, page.heading.upper())

        #REDO LEVEL
        resp = self.client.get('/level_intro/%s/%s/%d' % (self.journey.slug, self.module.slug, self.level.pk),
                               follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())
        self.assertContains(resp, self.level.text)

        for i in range(0, 5):
            resp = self.client.get(reverse('content.question'), follow=True)
            self.assertContains(resp, self.level.name.upper())

            resp = self.client.post(reverse('content.question'),
                                    data={
                                        'answer': answers[i].id
                                    },
                                    follow=True)
            self.assertEquals(resp.status_code, 200)
            self.assertContains(resp, 'CORRECT')

        resp = self.client.get('/level_end/')
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level.name.upper())
        self.assertContains(resp, 'LEVEL COMPLETE')

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

    def test_help(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        page = self.create_help_page('help_slug', 'help_title', 'help_heading', 'help_content', 'help_description')

        resp = self.client.get(reverse('misc.help'))
        self.assertContains(resp, page.heading)

        resp = self.client.get('/help/%s/' % page.slug)
        self.assertContains(resp, page.heading.upper())
        self.assertContains(resp, page.content)

    def test_contact(self):
        resp = self.client.get(reverse('misc.contact'))
        self.assertEquals(resp.status_code, 200)

        resp = self.client.post(reverse('misc.contact'),
                                data={
                                    'first_name': 'Bob',
                                    'last_name': 'Charles',
                                    'id_number': '1234564567890123',
                                    'mobile': '0711234567',
                                    'message': 'This is a message'
                                },
                                follow=True)
        resp = self.assertTemplateUsed(resp, 'misc/error.html')


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
        stats = create_json_stats()
        email_stats(stats)


class AdminTests(TestCase):

    def setUp(self):
        self.password = 'admin'
        self.admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@admin.com',
            password=self.password)

    def admin_page_test_helper(self, url):
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_communication(self):
        self.client.login(username=self.admin, password=self.password)

        self.admin_page_test_helper('/admin/communication/')
        self.admin_page_test_helper('/admin/communication/sms/')

    def test_content(self):
        self.client.login(username=self.admin, password=self.password)

        self.admin_page_test_helper('/admin/content/')
        self.admin_page_test_helper('/admin/content/journey/')
        self.admin_page_test_helper('/admin/content/journey/add/')
        self.admin_page_test_helper('/admin/content/module/')
        self.admin_page_test_helper('/admin/content/module/add/')
        self.admin_page_test_helper('/admin/content/level/')
        self.admin_page_test_helper('/admin/content/level/add/')
        self.admin_page_test_helper('/admin/content/levelquestion/')
        self.admin_page_test_helper('/admin/content/levelquestion/add/')
        self.admin_page_test_helper('/admin/content/harambeejourneymodulerel/')
        self.admin_page_test_helper('/admin/content/harambeejourneymodulelevelrel/')
        self.admin_page_test_helper('/admin/content/harambeequestionanswer/')
        self.admin_page_test_helper('/admin/content/harambeeequestionanswertime/')

    def test_core(self):
        self.client.login(username=self.admin, password=self.password)

        self.admin_page_test_helper('/admin/core/')
        self.admin_page_test_helper('/admin/core/helppage/')
        self.admin_page_test_helper('/admin/core/helppage/add/')
        self.admin_page_test_helper('/admin/core/page/')
        self.admin_page_test_helper('/admin/core/page/add/')

    def test_my_auth(self):
        self.client.login(username=self.admin, password=self.password)

        self.admin_page_test_helper('/admin/my_auth/')
        self.admin_page_test_helper('/admin/my_auth/harambee/')
        self.admin_page_test_helper('/admin/my_auth/harambee/add/')
        self.admin_page_test_helper('/admin/my_auth/systemadministrator/')
        self.admin_page_test_helper('/admin/my_auth/systemadministrator/add/')
