import random
import string
from datetime import datetime, timedelta
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import AbstractUser
from content.models import Level, LevelQuestion, HarambeeQuestionAnswer, HarambeeJourneyModuleLevelRel, Module


class CustomUser(AbstractUser):
    mobile = models.CharField(verbose_name="Mobile Phone Number",
                              max_length=50, blank=False, unique=True)

    unique_token = models.CharField(
        verbose_name="Unique Login Token",
        max_length=500,
        blank=True,
        null=True
    )

    unique_token_expiry = models.DateTimeField(
        verbose_name="Unique Login Token Expiry",
        null=True,
        blank=True
    )

    pass_reset_token = models.CharField(
        verbose_name="Password Reset Token",
        max_length=500,
        blank=True,
        null=True
    )

    pass_reset_token_expiry = models.DateTimeField(
        verbose_name="Password Reset Token Expiry",
        null=True,
        blank=True
    )

    def generate_valid_token(self):
        # Base 64 encode from random uuid bytes and make url safe
        self.unique_token = ''.join(
            random.choice(
                string.ascii_letters +
                string.digits) for i in range(8))

        # Calculate expiry date
        self.unique_token_expiry = datetime.now() + timedelta(days=30)

    def generate_unique_token(self):
        # Check if unique token needs regenerating
        if self.unique_token_expiry is None \
                or timezone.now() > self.unique_token_expiry:
            # Check uniqueness on generation
            self.generate_valid_token()
            while CustomUser.objects.filter(
                    unique_token=self.unique_token).exists():
                self.generate_valid_token()

    def generate_valid_reset_token(self):
        # Base 64 encode from random uuid bytes and make url safe
        self.pass_reset_token = ''.join(
            random.choice(
                string.ascii_letters +
                string.digits) for i in range(8))

        # Calculate expiry date
        self.pass_reset_token_expiry = datetime.now() + timedelta(hours=1)

    def generate_reset_password_token(self):
        # Check if reset password token needs regenerating
        if self.pass_reset_token_expiry is None \
                or timezone.now() > self.pass_reset_token_expiry:
            # Check uniqueness on generation
            self.generate_valid_reset_token()
            while CustomUser.objects.filter(
                    pass_reset_token=self.pass_reset_token).exists():
                self.generate_valid_reset_token()

    def get_display_name(self):
        if self.first_name:
            temp = self.first_name + ' ' + self.last_name
        else:
            temp = self.username

        return temp


class Harambee(CustomUser):
    lps = models.PositiveIntegerField("Learning Potential Score", blank=False)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        verbose_name = "Harambee"
        verbose_name_plural = "Harambees"

    def num_level_questions_answered(self, level):
        return HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level)\
            .aggregate(Count('id'))['id__count']

    def num_level_questions_correct_percentage(self, level):
        return HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level, answer__correct=True)\
            .aggregate(Count('id'))['id__count'] * 100 / self.num_level_questions_answered(level)

    def num_level_questions_answered(self, level):
        return HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level)\
            .aggregate(Count('id'))['id__count']

    def num_level_questions_correct_percentage(self, level):
        return HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level, answer__correct=True)\
            .aggregate(Count('id'))['id__count'] * 100 / self.num_level_questions_answered(level)

    def num_completed_levels(self, module):
        return HarambeeJourneyModuleLevelRel.objects.filter(harambee=self, level__module=module,
                                                            status=HarambeeJourneyModuleLevelRel.LEVEL_COMPLETE)\
            .aggregate(Count('id'))['id__count']

    def level_completed(self, level):
        total_answered = HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level) \
            .aggregate(Count('id'))['id__count']
        answered_correctly = HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level,
                                                                   answer__correct=True) \
            .aggregate(Count('id'))['id__count']

        rel = HarambeeJourneyModuleLevelRel.objects.filter(harambee=self, level=level).first()

        if total_answered > level.module.minimum_questions and \
                (answered_correctly * 100 / total_answered) >= level.module.minimum_percentage:
            # rel.state = COMPLETE
            # rel.date_completed = datetime.now()
            # rel.save()
            return True
        return False

    def answered_streak(self, level, show_all):
        """
            If show_all is true it will return 5 if streak is 5 else 0
        """
        last_incorrect = HarambeeQuestionAnswer.objects.filter(harambee=self, level=level,
                                                               option_selected__correct=False)\
            .latest('date_answered')
        num_correct = HarambeeQuestionAnswer.objects.filter(harambee=self, level=level, option_selected__correct=True,
                                                            date_answered__gt=last_incorrect.date_answered) \
            .aggregate(Count('id'))['id__count']

        if num_correct > 0 and num_correct % 5 == 0 and show_all:
            return 5
        else:
            return num_correct % 5

    def answer_question(self, question, answer, rel):
        HarambeeQuestionAnswer.objects.create(
            harambee=self,
            question=question,
            option_selected=answer,
            harambee_level_rel=rel,
            date_answered=datetime.now()
        )

    def check_if_level_complete(self, question, rel):
        pass

    def can_take_level(self, level):
        if level.order == 1:
            return True
        else:
            previous_level = Level.objects.get(module=level.module, order=level.order-1)

            previous_level_rel = HarambeeJourneyModuleLevelRel.objects.filter(harambee=self, level=previous_level)\
                .exclude(state=HarambeeJourneyModuleLevelRel.LEVEL_ACTIVE)

            if previous_level_rel:
                return True

        return False

    def get_unlocked_levels(self, module):
        all_levels = Level.objects.filter(module=module).order_by('order')

        unlocked_list = []

        for level in all_levels:
            if self.can_take_level(level):
                unlocked_list.append(level.id)

        return Level.objects.filter(id__in=unlocked_list)

    def get_locked_levels(self, module):
        unlocked_list = self.get_unlocked_levels(module).values_list('id', flat=True)
        return Level.objects.exclude(id__in=unlocked_list)

    def answered_previous_question(self, question):
        if question.level.question_order == Level.RANDOM or question.order == 1:
            return True

        if HarambeeQuestionAnswer.objects.filter(harambee=self, question=question, order=question.order-1).exists():
            return True
        else:
            return False

    def can_answer_question(self, question):
        if self.answered_previous_question and self.can_take_level(question.level):
            return True
        else:
            return False

    def module_unlocked(self, module):
        """
        Return True if harambee's lps score is high enough
        """
        if module.accessibleTo == Module.LPS_5:
            if self.lps >= 5:
                return True
            else:
                return False
        elif module.accessibleTo == Module.LPS_1_4:
            if self.lps in range(1, 5):
                return True
            else:
                return False
        else:
            return True

    def get_unlocked_modules_by_journey(self, journey):
        pass

    def get_all_unlocked(self):
        all_modules = Module.objects.all()
        unlocked_list = []

        for module in all_modules:
            if self.module_unlocked(module):
                unlocked_list.append(module.id)

        return Module.objects.filter(id__in=unlocked_list)

    def get_active_modules(self):
        pass

    def completed_modules(self):
        pass

    def get_next_question(self, harambee_level_rel):

        if harambee_level_rel.state != HarambeeJourneyModuleLevelRel.LEVEL_COMPLETE:

            if harambee_level_rel.level.question_order == Level.ORDERED:
                next_question = self.get_next_in_order_question(harambee_level_rel)

            else:
                next_question = self.get_random_question(harambee_level_rel)

            if next_question:
                return next_question

        return None

    def get_answered_questions_list(self, harambee_level_rel):
        return HarambeeQuestionAnswer.objects.filter(harambee_level_rel=harambee_level_rel)\
            .order_by('question__order')\
            .values_list('id', flat=True)

    def get_random_question(self, harambee_level_rel):
        answered_list = self.get_answered_questions_list(harambee_level_rel)

        return LevelQuestion.objects.filter(level=harambee_level_rel.level)\
            .exclude(id__in=answered_list)\
            .order_by('?').first()

    def get_next_in_order_question(self, harambee_level_rel):
        next_question_order_num = HarambeeQuestionAnswer.objects.filter(harambee_level_rel=harambee_level_rel)\
            .aggregate(Count('id'))['id__count'] + 1

        if next_question_order_num < harambee_level_rel.level.get_num_questions():
            try:
                next_question = LevelQuestion.objects.get(order=next_question_order_num)
                return next_question
            except LevelQuestion.MultipleObjectsReturned:
                #TODO more than one question has been returned
                return None
            except LevelQuestion.DoesNotExist:
                #TODO there is no question with that order number
                return None


class SystemAdministrator(CustomUser):

    class Meta:
        verbose_name = "System Administrator"
        verbose_name_plural = "System Administrators"

    def save(self, *args, **kwargs):
        self.is_staff = True
        self.is_superuser = True
        super(SystemAdministrator, self).save(*args, **kwargs)


# class HarambeeLog(models.Model):
#     LOGIN = 0
#     LOGOUT = 1
#     ACTIVE = 2
#
#     ACTION_CHOICES = (
#         (LOGIN, "Login"),
#         (LOGOUT, "Logout"),
#         (ACTIVE, "Active"),
#     )
#
#     harambee = models.ForeignKey(Harambee, null=True, blank=False)
#     date = models.DateTimeField(auto_now_add=True)
#     action = models.PositiveIntegerField("Action", choices=ACTION_CHOICES, blank=False)