from django.db.models import Count
from django.utils import timezone
from django.db import models
from colorful.fields import RGBColorField


class Journey(models.Model):

    name = models.CharField("Name", max_length=500, blank=False, unique=True)
    intro_text = models.TextField("Introductory Text", blank=True)
    slug = models.SlugField("Slug", unique=True, help_text="Slug used to identify this journey in URL. Must be unique."
                                                           "e.g. Journey_101")
    title = models.CharField("Title", max_length=500, blank=False, help_text="Title is displayed in the browsers tab.")
    show_menu = models.BooleanField("Show in menus", default=True, help_text="Show the journey link in users menu?")
    search = models.CharField("Search description", max_length=500)
    image = models.ImageField("Image", upload_to="journeys/", blank=True, null=True,
                              help_text="This is an icon and the ideal size for this icon is 32 x 32px. "
                                        "If the icon is bigger or smaller the phone's browser will scale it and the "
                                        "image will look very pixelated.")
    colour = RGBColorField("Colour", help_text="Colour theme for the journey.")

    start_date = models.DateTimeField("Go Live On", null=True, blank=True)
    end_date = models.DateTimeField("Expire On", null=True, blank=True)
    publish_date = models.DateTimeField("Published On", null=False, blank=False, auto_now_add=True)
    modified_date = models.DateTimeField("Last Modified", null=False, blank=False, auto_now=True)

    def __unicode__(self):
        return self.name

    def is_active(self):
        if self.start_date:
            if self.start_date <= timezone.now():
                if self.end_date:
                    if self.end_date > timezone.now():
                        return True
                else:
                    return True
        return False


class Module(models.Model):

    # Accessible To
    ALL = 1
    LPS_1_4 = 2
    LPS_5 = 3

    # Percentages
    PERCENT_0 = 0
    PERCENT_25 = 25
    PERCENT_50 = 50
    PERCENT_55 = 55
    PERCENT_60 = 60
    PERCENT_65 = 65
    PERCENT_70 = 70
    PERCENT_75 = 75
    PERCENT_80 = 80
    PERCENT_85 = 85
    PERCENT_90 = 90
    PERCENT_95 = 95
    PERCENT_100 = 100

    PERCENTAGE_CHOICES = (
        (PERCENT_0, "0%"),
        (PERCENT_25, "25%"),
        (PERCENT_50, "50%"),
        (PERCENT_55, "55%"),
        (PERCENT_60, "60%"),
        (PERCENT_65, "65%"),
        (PERCENT_70, "70%"),
        (PERCENT_75, "75%"),
        (PERCENT_80, "80%"),
        (PERCENT_85, "85%"),
        (PERCENT_90, "90%"),
        (PERCENT_95, "95%"),
        (PERCENT_100, "100%")
    )

    name = models.CharField("Name", max_length=500, blank=False, unique=True)
    intro_text = models.TextField("Introductory Text", blank=True)
    end_text = models.TextField("Complete Page Text", blank=True)
    image = models.ImageField("Image", upload_to="modules/", blank=True, null=True,
                              help_text="This is an icon and the ideal size for this icon is 32 x 32px. "
                                        "If the icon is bigger or smaller the phone's browser will scale it and the "
                                        "image will look very pixelated.")
    journeys = models.ManyToManyField(
        Journey, related_name='modules', through='JourneyModuleRel',)
    accessibleTo = models.PositiveIntegerField(
        "Accessible To", choices=(
            (ALL, "All"),
            (LPS_1_4, "Learning Potential Score 1 - 4"),
            (LPS_5, "Learning Potential Score 5+")
        ),
        default=ALL)
    show_recommended = models.BooleanField("Feature in Recommended for You", default=True)
    slug = models.SlugField("Slug", unique=True, help_text="Slug used to identify this module in URL. Must be unique."
                                                           "e.g. Module_101")
    title = models.CharField("Page Title", max_length=500, blank=False,
                             help_text="Title is displayed in the browsers tab.")
    show_menu = models.BooleanField("Show in menu", default=True, help_text="Show the module link in users menu?")
    search = models.CharField("Search description", max_length=500,)
    minimum_questions = models.PositiveIntegerField("Minimum # of questions to answer",
                                                    help_text="Required number of questions to be answered to pass a "
                                                              "level.")
    minimum_percentage = models.PositiveIntegerField(
        "Minimum overall % for all questions answered", choices=PERCENTAGE_CHOICES,
        help_text="Required overall % to pass a level.")
    store_data_per_user = models.BooleanField("Data stored against User I.D.", default=True)
    start_date = models.DateTimeField("Go Live On", null=True, blank=True)
    end_date = models.DateTimeField("Expire On", null=True, blank=True)
    publish_date = models.DateTimeField("Published On", null=False, blank=False, auto_now_add=True)
    modified_date = models.DateTimeField("Last Modified", null=False, blank=False, auto_now=True)
    notified_users = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def is_active(self):
        if self.start_date:
            if self.start_date <= timezone.now():
                if self.end_date:
                    if self.end_date > timezone.now():
                        return True
                else:
                    return True
        return False

    def total_levels(self):
        return self.level_set.all().aggregate(Count('id'))['id__count']

    def get_levels(self):
        return self.level_set.all()

    def slug_intro(self):
        return "module_intro/%s" % self.slug

    def slug_home(self):
        return "module_home/%s" % self.slug

    def slug_end(self):
        return "module_end/%s" % self.slug


class JourneyModuleRel(models.Model):

    journey = models.ForeignKey(Journey)
    module = models.ForeignKey(Module)


class HarambeeJourneyModuleRel(models.Model):

    MODULE_STARTED = 0
    MODULE_HALF = 1
    MODULE_COMPLETED = 2

    MODULE_STATE_CHOICES = (
        (MODULE_STARTED, 'Active'),
        (MODULE_HALF, 'Half Way'),
        (MODULE_COMPLETED, 'Completed')
    )

    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    journey_module_rel = models.ForeignKey(JourneyModuleRel, null=False, blank=False)
    state = models.PositiveIntegerField(choices=MODULE_STATE_CHOICES, default=MODULE_STARTED)
    date_started = models.DateTimeField("Date Started", auto_now_add=True, null=True, blank=True)
    date_completed = models.DateTimeField("Date Completed", null=True, blank=True)
    last_active = models.DateTimeField("Last Active", null=True, blank=True)

    class Meta:
        verbose_name = "Harambee Module Relationship"
        verbose_name_plural = "Harambee Module Relationships"


class Level(models.Model):

    ORDERED = 0
    RANDOM = 1

    QUESTION_ORDER_CHOICES = (
        (ORDERED, "Ordered"),
        (RANDOM, "Random")
    )

    name = models.CharField("Name", max_length=500, blank=False, unique=True)
    text = models.TextField("Introductory Text", blank=True)
    module = models.ForeignKey(Module, null=True, blank=False)
    order = models.PositiveIntegerField("Level number", blank=False,
                                        help_text="Levels are completed according to this number.")
    question_order = models.PositiveIntegerField("Question Order", choices=QUESTION_ORDER_CHOICES, default=RANDOM,
                                                 help_text="Order in which questions will be chosen.")

    def __unicode__(self):
        return self.name

    def get_questions(self):
        return LevelQuestion.objects.filter(level=self)

    def get_num_questions(self):
        return self.get_questions().aggregate(Count('id'))['id__count']

    def is_active(self):
        """
            Level can only be active if it has enough questions that are in order and all questions have enough answer
            options.
        """
        enough_question = self.get_num_questions() >= self.module.minimum_questions
        if not enough_question:
            return False

        question_order_list = LevelQuestion.objects.filter(level=self).values_list('order', flat=True)
        for count in range(1, self.get_num_questions() + 1):
            if count not in question_order_list:
                return False

        all_questions = LevelQuestion.objects.filter(level=self)
        for question in all_questions:
            if not question.is_active():
                return False

        return True


class LevelQuestion(models.Model):

    name = models.CharField("Name", max_length=500, blank=False, unique=True,  default="Auto Generated")
    order = models.PositiveIntegerField("Order Number", blank=False, help_text="Order number determines the order in "
                                                                               "which questions are asked in a level.")
    level = models.ForeignKey(Level, null=True, blank=False)
    question_content = models.TextField("Question", blank=False)
    notes = models.TextField("Additional Notes", blank=True)
    image = models.ImageField("Image", upload_to="questions/", blank=True, null=True,
                              help_text="This is an image and the ideal size for this image should be 150px in width. "
                                        "If the image width is bigger or smaller the phone's browser "
                                        "will scale it and the image will look very pixelated.")

    def __unicode__(self):
        return self.name

    def is_active(self):
        """
            Question is active if it has more than 2 answer options.
        """
        if self.levelquestionoption_set.all().aggregate(Count('id'))['id__count'] >= 2:
            return True
        return False

    class Meta:
        verbose_name = "Level Question"
        verbose_name_plural = "Level Questions"
        ordering = ['order']


class HarambeeJourneyModuleLevelRel(models.Model):

    LEVEL_ACTIVE = 0
    LEVEL_COMPLETE = 1

    LEVEL_STATE_CHOICES = (
        (LEVEL_ACTIVE, "Active"),
        (LEVEL_COMPLETE, "Complete"),
    )

    harambee_journey_module_rel = models.ForeignKey(HarambeeJourneyModuleRel, null=True, blank=False)
    level = models.ForeignKey(Level, null=False, blank=False)
    state = models.PositiveIntegerField(choices=LEVEL_STATE_CHOICES, default=LEVEL_ACTIVE)
    level_passed = models.BooleanField(default=False)
    date_started = models.DateTimeField("Date Started", auto_now_add=True, null=True, blank=True)
    date_completed = models.DateTimeField("Date Completed", null=True, blank=True)
    last_active = models.DateTimeField("Last Active", null=True, blank=True)
    level_attempt = models.PositiveIntegerField("Attempt Number")
    current_question = models.ForeignKey(LevelQuestion, null=True, blank=True)

    def is_current_question_answered(self):
        try:
            HarambeeQuestionAnswer.objects.get(harambee_level_rel=self, question=self.current_question)
            return True
        except HarambeeQuestionAnswer.DoesNotExist:
            return False
        except HarambeeQuestionAnswer.MultipleObjectsReturned:
            self.harambee_journey_module_rel.harambee.delete_multiple_answers(self.current_question, self)
            return True

    class Meta:
        verbose_name = "Harambee Level Relationship"
        verbose_name_plural = "Harambee Level Relationships"


class LevelQuestionOption(models.Model):

    name = models.CharField("Name", max_length=500, null=True, blank=False, unique=True)
    question = models.ForeignKey(LevelQuestion, null=True, blank=False)
    content = models.TextField("Content", blank=False)
    correct = models.BooleanField("Correct")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Question Option"
        verbose_name_plural = "Question Options"


class HarambeeQuestionAnswer(models.Model):

    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    question = models.ForeignKey(LevelQuestion, null=False, blank=False)
    option_selected = models.ForeignKey(LevelQuestionOption, null=False, blank=False)
    date_answered = models.DateTimeField(null=False, blank=False)
    harambee_level_rel = models.ForeignKey(HarambeeJourneyModuleLevelRel, null=False, blank=False)

    class Meta:
        verbose_name = "Level Question Answer"
        verbose_name_plural = "Level Question Answers"

    def is_correct(self):
        return self.option_selected.correct


class HarambeeeQuestionAnswerTime(models.Model):

    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    question = models.ForeignKey(LevelQuestion, null=False, blank=False)
    harambee_level_rel = models.ForeignKey(HarambeeJourneyModuleLevelRel, null=False, blank=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Question Answer Time"
        verbose_name_plural = "Question Answer Times"

    def answer_time_seconds(self):
        if self.start_time and self.end_time:
            return (self.end_time-self.start_time).seconds
        return 'Not answered'


class HarambeeState(models.Model):
    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    active_level_rel = models.ForeignKey(HarambeeJourneyModuleLevelRel, null=True, blank=True)
