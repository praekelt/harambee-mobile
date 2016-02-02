from communication.models import Sms, InactiveSMS
from communication.tasks import send_inactive_sms, send_new_content_sms
from content.models import Journey, Module, JourneyModuleRel, Level, LevelQuestion, LevelQuestionOption,\
    HarambeeJourneyModuleRel, HarambeeQuestionAnswer
from core.models import Page, HelpPage
from datetime import timedelta
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from harambee.metrics import create_json_stats
from harambee.tasks import email_stats
from httplib2 import ServerNotFoundError
from mock import patch
from my_auth.models import Harambee, CustomUser
from views import ForgotPinView


def login(self, username, password):
    self.client.post(reverse('auth.login'), data={'username': username, 'password': password}, follow=True)
    return self


def logout(self):
    self.client.get(reverse('auth.logout'), follow=True)
    return self


def create_harambee(mobile, username, candidate_id, lps=1, **kwargs):
    return Harambee.objects.create(mobile=mobile, username=username, candidate_id=candidate_id, lps=lps, **kwargs)


def create_journey(name, start_date=timezone.now(), **kwargs):
    return Journey.objects.create(name=name, slug=name, title=name, start_date=start_date, **kwargs)


def create_module(journey, name, minimum_questions, minimum_percentage, **kwargs):
    module = Module.objects.create(name=name, slug=name, title=name, minimum_questions=minimum_questions,
                                   minimum_percentage=minimum_percentage, **kwargs)
    return JourneyModuleRel.objects.create(journey=journey, module=module)


def create_level(name, module, order, question_order=Level.ORDERED, **kwargs):
    return Level.objects.create(name=name, module=module, order=order, question_order=question_order, **kwargs)


def create_question(name, level, order, question_content='Question', **kwargs):
    return LevelQuestion.objects.create(name=name, level=level, order=order, question_content=question_content,
                                        **kwargs)


def create_question_option(name, question, content='Answer', correct=True):
    return LevelQuestionOption.objects.create(name=name, question=question, content=content, correct=correct)


def create_help_page(slug, title, heading, content, description, activate=timezone.now(), deactivate=None,
                     show=True):
    return HelpPage.objects.create(slug=slug, title=title, heading=heading, content=content,
                                   description=description, activate=activate, deactivate=deactivate, show=show)


def complete_level(self, level, num_correct):
    """
        User needs to be logged in. Questions need to be in order.
    """
    correct_counter = 0
    all_level_questions = level.get_questions()
    for question in all_level_questions:
        #Get question
        resp = self.client.get(reverse('content.question'))
        self.assertEquals(resp.status_code, 200)

        if correct_counter < num_correct:
            correct_counter += 1
            #Correct answer
            answer = LevelQuestionOption.objects.get(question=question, correct=True)
            #Answer question
            resp = self.client.post(reverse('content.question'), data={'answer': answer.id}, follow=True)
            self.assertRedirects(resp, '/right/')
        else:
            #Incorrect answer
            answer = LevelQuestionOption.objects.get(question=question, correct=False)
            #Answer question
            resp = self.client.post(reverse('content.question'), data={'answer': answer.id}, follow=True)
            self.assertRedirects(resp, '/wrong/')

    #Call question again to get to level end page
    resp = self.client.get(reverse('content.question'), follow=True)
    self.assertRedirects(resp, '/level_end/')


def complete_module(self, journey_module, num_correct):
    """
        Needs to be logged in.
    """

    #Get all module levels
    all_module_levels = journey_module.module.get_levels()
    for level in all_module_levels:

        #Go to module home
        resp = self.client.get(reverse('content.module_home',
                                       kwargs={'journey_slug': '%s' % journey_module.journey.slug,
                                               'module_slug': '%s' % journey_module.module.slug}),
                               follow=True)
        self.assertTemplateUsed(resp, 'content/module_home.html')
        self.assertEquals(resp.status_code, 200)

        #Go to level intro
        resp = self.client.get(reverse('content.level_intro',
                                       kwargs={'journey_slug': '%s' % journey_module.journey.slug,
                                               'module_slug': '%s' % journey_module.module.slug,
                                               'pk': '%s' % level.pk}),
                               follow=True)
        self.assertTemplateUsed(resp, 'content/level_intro.html')
        self.assertEquals(resp.status_code, 200)

        #Answer all the questions in a level
        complete_level(self, level, num_correct)

    #MODULE END VIEW
    resp = self.client.get(reverse('content.module_end',
                                   kwargs={'journey_slug': '%s' % journey_module.journey.slug,
                                           'module_slug': '%s' % journey_module.module.slug}),
                           follow=True)

    self.assertTemplateUsed(resp, 'content/module_end.html')
    self.assertEquals(resp.status_code, 200)
    self.assertContains(resp, journey_module.module.name.upper())


def create_level_with_questions(name, module, order, num_questions):
    level = create_level(name, module, order)
    for i in range(1, num_questions+1):
        question = create_question('%s_q_%d' % (name, i), level, i)
        create_question_option('%s_q_%d_c' % (name, i), question)
        create_question_option('%s_q_%d_w' % (name, i), question, correct=False)
    return level


class GeneralTests(TestCase):

    def setUp(self):
        self.harambee = create_harambee('0701234567', '0000000000000', '1234567890', first_name="Jamal",
                                        last_name="Lyon")
        self.password = '1234'
        self.harambee.set_password(self.password)
        self.harambee.save()

        self.journey = create_journey('Sales')
        self.journey_module = create_module(self.journey, 'Customer_Service', 1, Module.PERCENT_50,
                                            start_date=timezone.now())
        self.level_1 = create_level_with_questions('Level_1', self.journey_module.module, 1, 5)
        self.level_2 = create_level_with_questions('Level_2', self.journey_module.module, 2, 5)

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

        #NO MATCH
        username = '8501016184086'
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
                'username': "8501016184086",
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
        count = Sms.objects.filter(message__contains='Welcome').count()
        self.assertEquals(count, 1)

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

        #test lps check
        new_module = create_module(self.journey, 'randomness', 1, 1, accessibleTo=Module.LPS_5,
                                   start_date=timezone.now())

        resp = self.client.get('/journey_home/%s' % self.journey.slug, follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertNotContains(resp, new_module.module.name)

        self.harambee.lps = 6
        self.harambee.save()

        resp = self.client.get('/journey_home/%s' % self.journey.slug, follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, new_module.module.name)

        self.harambee.lps = 1
        self.harambee.save()

    #TODO: test for levels that don't exist
    def test_complete_module(self):
        """

        """
        #create a module but don't make it live. Testing sms functionality
        create_module(self.journey, 'Module_2', 2, 2)

        login(self, self.harambee.username, self.password)

        #NEED TO GO HOME TO CREATE HARAMBEEJOUNREYMODULEREL
        resp = self.client.get(reverse('content.module_home',
                                       kwargs={'journey_slug': '%s' % self.journey.slug,
                                               'module_slug': '%s' % self.journey_module.module.slug}),
                               follow=True)
        self.assertTemplateUsed(resp, 'content/module_home.html')
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.journey.name.upper())

        complete_module(self, self.journey_module, 5)

        #Check if module completed
        rel = HarambeeJourneyModuleRel.objects.get(harambee=self.harambee, journey_module_rel=self.journey_module,
                                                   state=HarambeeJourneyModuleRel.MODULE_COMPLETED)
        self.assertIsNotNone(rel)

        #Check if sms have been created for welcome, half way, completed and completed all
        all_smses = Sms.objects.all()
        self.assertEquals(all_smses.count(), 4)
        count = all_smses.filter(message__contains='Welcome').count()
        self.assertEquals(count, 1)
        count = all_smses.filter(message__contains='half way').count()
        self.assertEquals(count, 1)
        count = all_smses.filter(message__contains='completed %s' % self.journey_module.module.name).count()
        self.assertEquals(count, 1)
        count = all_smses.filter(message__contains='completed all').count()
        self.assertEquals(count, 1)

        #COMPLETED MODULES VIEW
        resp = self.client.get(reverse('content.completed_modules'))
        self.assertEquals(resp.status_code, 200)
        page = Page.objects.get(slug='completed_modules')
        self.assertContains(resp, page.heading.upper())

        #REDO LEVEL
        first_level = self.journey_module.module.get_levels().get(order=1)

        resp = self.client.get(reverse('content.level_intro',
                                       kwargs={'journey_slug': '%s' % self.journey_module.journey.slug,
                                               'module_slug': '%s' % self.journey_module.module.slug,
                                               'pk': '%s' % first_level.pk}),
                               follow=True)
        self.assertTemplateUsed(resp, 'content/level_intro.html')
        self.assertEquals(resp.status_code, 200)

        complete_level(self, first_level, 5)

    def test_answering_questions(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        #NEED TO GO HOME TO CREATE HARAMBEEJOUNREYMODULEREL
        resp = self.client.get(reverse('content.module_home',
                                       kwargs={'journey_slug': '%s' % self.journey.slug,
                                               'module_slug': '%s' % self.journey_module.module.slug}),
                               follow=True)
        self.assertTemplateUsed(resp, 'content/module_home.html')
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.journey.name.upper())

        resp = self.client.get(reverse('content.level_intro',
                                       kwargs={'journey_slug': '%s' % self.journey.slug,
                                               'module_slug': '%s' % self.journey_module.module.slug,
                                               'pk': '%s' % self.level_1.pk}),
                               follow=True)
        self.assertTemplateUsed(resp, 'content/level_intro.html')
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, self.level_1.name.upper())

        #Get a question
        resp = self.client.get(reverse('content.question'))
        self.assertEquals(resp.status_code, 200)

        #Incorrect post calls
        resp = self.client.post(reverse('content.question'),
                                data={},
                                follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/question.html')

        resp = self.client.post(reverse('content.question'),
                                data={
                                    'answer': 99
                                },
                                follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/question.html')

        #Answer a question correctly
        question = LevelQuestion.objects.filter(level=self.level_1, order=1).first()
        correct_option = LevelQuestionOption.objects.get(question=question, correct=True)
        resp = self.client.post(reverse('content.question'),
                                data={
                                    'answer': correct_option.id
                                },
                                follow=True)
        self.assertTemplateUsed(resp, 'content/right.html')
        self.assertEquals(resp.status_code, 200)

        #Answer a question incorrectly
        resp = self.client.get(reverse('content.question'))
        self.assertEquals(resp.status_code, 200)

        question = LevelQuestion.objects.filter(level=self.level_1, order=2).first()
        incorrect_option = LevelQuestionOption.objects.get(question=question, correct=False)
        resp = self.client.post(reverse('content.question'),
                                data={
                                    'answer': incorrect_option .id
                                },
                                follow=True)
        self.assertTemplateUsed(resp, 'content/wrong.html')
        self.assertEquals(resp.status_code, 200)

    def test_help(self):
        resp = self.client.post(
            reverse('auth.login'),
            data={
                'username': self.harambee.username,
                'password': self.password},
            follow=True)
        self.assertContains(resp, "WELCOME, %s" % self.harambee.first_name.upper())

        page = create_help_page('help_slug', 'help_title', 'help_heading', 'help_content', 'help_description')

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

    def setUp(self):
        self.NUM_JOURNEYS = 2
        self.NUM_MODULES = 2
        self.NUM_LEVELS = 3
        self.NUM_QUESTIONS = 10
        self.A_CORRECT = 10
        self.B_CORRECT = 8
        self.C_CORRECT = 5

        self.harambee_1 = create_harambee('0901234567', '8501016184086', '1234567890', first_name="Bob",
                                          last_name="Lee")
        self.password = '1234'
        self.harambee_1.set_password(self.password)
        self.harambee_1.save()

        self.harambee_2 = create_harambee('0709876543', '9001015000085', '9876543210', first_name="John",
                                          last_name="Green")
        self.harambee_2.set_password(self.password)
        self.harambee_2.save()

        self.harambee_3 = create_harambee('0801236987', '9010105000087', '1478523690', first_name="Tim",
                                          last_name="Cook")
        self.harambee_3.set_password(self.password)
        self.harambee_3.save()

        self.journey_list = list()
        self.journey_module_list = list()
        for j in range(0, self.NUM_JOURNEYS):
            self.journey_list.insert(j, create_journey('Journey_%s' % (j+1)))

            module_temp_list = list()
            for m in range(0, self.NUM_MODULES):
                module_temp_list.insert(m, create_module(self.journey_list[j], 'J_%s_Module_%s' % ((j+1), (m+1)), 1,
                                                         Module.PERCENT_50, start_date=timezone.now()))

                for l in range(0, self.NUM_LEVELS):
                    create_level_with_questions('J_%s_M_%s_Level_%s' % ((j+1), (m+1), (l+1)),
                                                module_temp_list[m].module, (l+1), self.NUM_QUESTIONS)
            self.journey_module_list.insert(j, module_temp_list)

    def test_metrics(self):
        login(self, self.harambee_1.username, self.password)
        for j in range(0, self.NUM_JOURNEYS):
            for m in range(0, self.NUM_MODULES):
                complete_module(self, self.journey_module_list[j][m], self.A_CORRECT)
        logout(self)

        login(self, self.harambee_2.username, self.password)
        for j in range(0, self.NUM_JOURNEYS):
            for m in range(0, self.NUM_MODULES):
                complete_module(self, self.journey_module_list[j][m], self.B_CORRECT)
        logout(self)

        login(self, self.harambee_3.username, self.password)
        for j in range(0, self.NUM_JOURNEYS):
            for m in range(0, self.NUM_MODULES):
                complete_module(self, self.journey_module_list[j][m], self.C_CORRECT)
        logout(self)

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

        resp = self.client.get(reverse('admin.delete_sms', args='6'))
        self.assertRedirects(resp, '/admin/communication/sms/')

        harambee = Harambee.objects.create(mobile='0719876543', username='1236987524693', candidate_id='16785', lps=2)
        sms_1 = Sms.objects.create(harambee=harambee, message='Helllooo')
        sms_2 = Sms.objects.create(harambee=harambee, message='Byeeeeee', sent=True)

        resp = self.client.get(reverse('admin.delete_sms', kwargs={'ids': '%s,%s' % (sms_1.id, sms_2.id)}))
        self.assertEquals(resp.status_code, 200)
        self.assertContains(resp, '_selected_action', 1)

        resp = self.client.post(reverse('admin.delete_sms', kwargs={'ids': '%s,%s' % (sms_1.id, sms_2.id)}),
                                data={'post': 'yes', 'action': 'delete_selected', '_selected_action': str(sms_1.id)},
                                follow=True)
        self.assertEquals(resp.status_code, 200)
        count = Sms.objects.all().count()
        self.assertEquals(count, 1)
        self.assertContains(resp, '1 SMSes deleted.')

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

        #invalid user ids
        resp = self.client.get(reverse('admin.send_sms', kwargs={'ids': '%s' % 9}))
        self.assertRedirects(resp, '/admin/my_auth/harambee/')

        harambee_1 = Harambee.objects.create(mobile='0719876543', username='1236987524693', candidate_id='16785', lps=2)
        harambee_2 = Harambee.objects.create(mobile='0815467891', username='7841036945821', candidate_id='61528', lps=5)

        #valid get
        resp = self.client.get(reverse('admin.send_sms', kwargs={'ids': '%s,%s' % (harambee_1.id, harambee_2.id)}))
        self.assertEquals(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/my_auth/send_sms.html')
        self.assertContains(resp, '%s' % harambee_1.first_name)
        self.assertContains(resp, '%s' % harambee_2.first_name)

        #valid post
        message_text = 'Test message'
        resp = self.client.post(reverse('admin.send_sms', kwargs={'ids': '%s,%s' % (harambee_1.id, harambee_2.id)}),
                                data={'post': 'yes', 'action': 'send_sms',
                                      'harambee': [harambee_1.id, harambee_2.id],
                                      'message': '%s' % message_text},
                                follow=True)
        self.assertRedirects(resp, '/admin/my_auth/harambee/')
        self.assertContains(resp, '2 SMSes created. They will be sent shortly.')
        count = Sms.objects.filter(message=message_text).count()
        self.assertEquals(count, 2)

        harambee_1.receive_smses = False
        harambee_1.save()
        message_text = 'Test message 2'
        resp = self.client.post(reverse('admin.send_sms', kwargs={'ids': '%s,%s' % (harambee_1.id, harambee_2.id)}),
                                data={'post': 'yes', 'action': 'send_sms',
                                      'harambee': [harambee_1.id, harambee_2.id],
                                      'message': '%s' % message_text},
                                follow=True)
        self.assertRedirects(resp, '/admin/my_auth/harambee/')
        self.assertContains(resp, '1 SMS created. It will be sent shortly.')
        count = Sms.objects.filter(message=message_text).count()
        self.assertEquals(count, 1)

        harambee_2.receive_smses = False
        harambee_2.save()
        message_text = 'Test message 3'
        resp = self.client.post(reverse('admin.send_sms', kwargs={'ids': '%s,%s' % (harambee_1.id, harambee_2.id)}),
                                data={'post': 'yes', 'action': 'send_sms',
                                      'harambee': [harambee_1.id, harambee_2.id],
                                      'message': '%s' % message_text},
                                follow=True)
        self.assertRedirects(resp, '/admin/my_auth/harambee/')
        self.assertContains(resp, 'No SMSes created.')
        count = Sms.objects.filter(message=message_text).count()
        self.assertEquals(count, 0)

        #try access the view when not logged in
        self.client.logout()
        resp = self.client.get(reverse('admin.send_sms', kwargs={'ids': '%s,%s' % (harambee_1.id, harambee_2.id)}))
        self.assertRedirects(resp, '/admin/login/')


class SmsTests(TestCase):

    def test_send_inactive_sms(self):
        date = timezone.now()
        harambee_list = list()
        harambee_list.append(create_harambee('07298765%2d' % len(harambee_list),
                                             '12345678901%2d' % len(harambee_list),
                                             '579%2d' % len(harambee_list), last_login=date))

        inactive_sms = InactiveSMS.objects.all()
        for sms in inactive_sms:
            date = timezone.now() - timedelta(days=sms.days)
            harambee_list.append(create_harambee('07298765%2d' % len(harambee_list),
                                                 '12345678901%2d' % len(harambee_list),
                                                 '579%2d' % len(harambee_list), last_login=date))

        send_inactive_sms.delay()
        count = Sms.objects.all().count()
        self.assertEquals(count, len(harambee_list)-1)

        for harambee in harambee_list:
            harambee.receive_smses = False
            harambee.save()

        send_inactive_sms.delay()
        count = Sms.objects.all().count()
        self.assertEquals(count, len(harambee_list)-1)

    def test_send_new_content_sms(self):
        journey = create_journey('IT')
        create_module(journey, 'COS_101', 0, 0, accessibleTo=Module.ALL, start_date=timezone.now() - timedelta(hours=2))
        create_module(journey, 'COS_102', 0, 0, accessibleTo=Module.LPS_1_4,
                      start_date=timezone.now() - timedelta(hours=2))
        create_module(journey, 'COS_103', 0, 0, accessibleTo=Module.LPS_5,
                      start_date=timezone.now() - timedelta(hours=2))

        create_harambee('0729876599', '1234567890199', '57999', lps=1)
        create_harambee('0729876588', '1234567890188', '57988', lps=2)
        create_harambee('0729876577', '1234567890177', '57977', lps=6)

        send_new_content_sms.delay()
        count = Sms.objects.filter(message__contains='COS_103').count()
        self.assertEquals(count, 1)
        count = Sms.objects.filter(message__contains='COS_102').count()
        self.assertEquals(count, 3)
        count = Sms.objects.filter(message__contains='COS_101').count()
        self.assertEquals(count, 3)
