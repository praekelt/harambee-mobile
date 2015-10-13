from datetime import datetime
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from content.models import HarambeeQuestionAnswer, HarambeeLevelRel, COMPLETE


class Harambee(User):
    mobile = models.CharField(verbose_name="Mobile Phone Number", max_length=50, blank=False, unique=True)
    lps = models.PositiveIntegerField("Learning Potential Score")

    REQUIRED_FIELDS = ["mobile"]

    class Meta:
        verbose_name = "Harambee"
        verbose_name_plural = "Harambees"

    def answer_question(self, question, option):
        HarambeeQuestionAnswer.objects.create(
            harambee=self,
            question=question,
            option_selected=option,
            answerdate=datetime.now()
        )

    def num_level_questions_answered(self, level):
        return HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level)\
            .aggregate(Count('id'))['id__count']

    def num_level_questions_correct_percentage(self, level):
        return HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level, answer__correct=True)\
            .aggregate(Count('id'))['id__count'] * 100 / self.num_level_questions_answered(level)

    def num_completed_levels(self, module):
        return HarambeeLevelRel.objects.filter(harambee=self, level__module=module, status=COMPLETE)\
            .aggregate(Count('id'))['id__count']

    def level_completed(self, level):
        total_answered = HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level) \
            .aggregate(Count('id'))['id__count']
        answered_correctly = HarambeeQuestionAnswer.objects.filter(harambee=self, question__level=level,
                                                                   answer__correct=True) \
            .aggregate(Count('id'))['id__count']

        rel = HarambeeLevelRel.objects.filter(harambee=self, level=level).first()

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


class SystemAdministrator(User):

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