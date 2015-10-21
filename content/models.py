from django.db import models
from django.db.models import Count


class Journey(models.Model):

    name = models.CharField("Name", max_length=500, blank=False, unique=True)
    intro_text = models.TextField("Introductory Text", blank=True)
    slug = models.SlugField("Slug", unique=True)
    title = models.CharField("Title", max_length=500, blank=False)
    show_menu = models.BooleanField("Show in menus", default=True)
    search = models.CharField("Search description", max_length=500)
    image = models.ImageField("Image", upload_to="img/", blank=True, null=True)
    colour = models.CharField("Colour", max_length=7)

    start_date = models.DateTimeField("Go Live On", null=True, blank=True)
    end_date = models.DateTimeField("Expire On", null=True, blank=True)
    publish_date = models.DateTimeField("Published On", null=False, blank=False, auto_now_add=True)
    modified_date = models.DateTimeField("Last Modified", null=False, blank=False, auto_now=True)

    def __unicode__(self):
        return self.name


class Module(models.Model):

    # Accessible To
    ALL = 1
    LPS_1_4 = 2
    LPS_5 = 3

    # Percentages
    PERCENT_0 = 0
    PERCENT_25 = 25
    PERCENT_50 = 50
    PERCENT_75 = 75
    PERCENT_80 = 80
    PERCENT_90 = 90
    PERCENT_100 = 100

    PERCENTAGE_CHOICES = (
        (PERCENT_0, "0%"),
        (PERCENT_25, "25%"),
        (PERCENT_50, "50%"),
        (PERCENT_75, "75%"),
        (PERCENT_80, "80%"),
        (PERCENT_90, "90%"),
        (PERCENT_100, "100%")
    )

    name = models.CharField("Name", max_length=500, blank=False, unique=True)
    intro_text = models.TextField("Introductory Text", blank=True)
    end_text = models.TextField("Complete Page Text", blank=True)
    image = models.ImageField("Image", upload_to="img/", blank=True, null=True)
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
    slug = models.SlugField("Slug", unique=True, help_text="Slug used to identify this module in URL. Must be unique.")
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

    def __unicode__(self):
        return self.name

    def total_levels(self):
        return self.level_set.all().aggregate(Count('id'))['id__count']

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

    MODULE_ACTIVE = 0
    MODULE_COMPLETE = 1

    MODULE_STATE_CHOICES = (
        (MODULE_ACTIVE, "Active"),
        (MODULE_COMPLETE, "Complete"),
    )

    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    journey_module_rel = models.ForeignKey(JourneyModuleRel, null=False, blank=False)
    state = models.PositiveIntegerField(choices=MODULE_STATE_CHOICES, default=MODULE_ACTIVE)
    date_started = models.DateTimeField("Date Started", auto_now_add=True, null=True, blank=True)
    date_completed = models.DateTimeField("Date Completed", null=True, blank=True)


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
    order = models.PositiveIntegerField(blank=False)
    question_order = models.PositiveIntegerField("Question Order", choices=QUESTION_ORDER_CHOICES, default=RANDOM)

    def __unicode__(self):
        return self.name

    def get_num_questions(self):
        return LevelQuestion.objects.filter(level=self).aggregate(Count('id'))['id__count']


class LevelQuestion(models.Model):

    name = models.CharField("Name", max_length=500, blank=False, unique=True)
    description = models.CharField("Description", max_length=500, blank=True)
    order = models.PositiveIntegerField("Order", default=0)
    level = models.ForeignKey(Level, null=True, blank=False)
    question_content = models.TextField("Question", blank=True)
    answer_content = models.TextField("Fully Worked Solution", blank=True)
    notes = models.TextField("Additional Notes", blank=True)
    image = models.ImageField("Image", upload_to="img/", blank=True, null=True)

    def __unicode__(self):
        return self.name

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
    level_attempt = models.PositiveIntegerField("Attempt Number")
    current_question = models.ForeignKey(LevelQuestion, null=True, blank=True)


class LevelQuestionOption(models.Model):

    name = models.CharField("Name", max_length=500, null=True, blank=False, unique=True)
    question = models.ForeignKey(LevelQuestion, null=True, blank=False)
    order = models.PositiveIntegerField("Order", default=0)
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


class HarambeeState(models.Model):
    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    active_level_rel = models.ForeignKey(HarambeeJourneyModuleLevelRel, null=True, blank=True)
