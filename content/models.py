from django.db import models
from django.db.models import Count

ACTIVE = 0
PASSED = 1
COMPLETE = 2

STATE_CHOICES = (
    (ACTIVE, "Active"),
    (PASSED, "Passed"),
    (COMPLETE, "Complete"),
)


class Journey(models.Model):

    name = models.CharField("Name", max_length=500, blank=False, unique=True)
    intro_text = models.TextField("Introductory Text", blank=True)

    slug = models.SlugField("Slug", unique=True)
    title = models.CharField("Title", max_length=500, blank=False)
    show_menu = models.BooleanField("Show in menus", default=True)
    search = models.CharField("Search description", max_length=500)
    image = models.ImageField("Image", upload_to="img/", blank=True, null=True)
    start_date = models.DateTimeField("Go Live On", null=True, blank=True)
    end_date = models.DateTimeField("Expire On", null=True, blank=True)

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
    journeys = models.ManyToManyField(Journey)
    accessibleTo = models.PositiveIntegerField(
        "Accessible To", choices=(
            (ALL, "All"),
            (LPS_1_4, "Learning Potential Score 1 - 4"),
            (LPS_5, "Learning Potential Score 5+")
        ),
        default=ALL)
    show_recommended = models.BooleanField("Feature in Recommended for You", default=True)
    slug = models.SlugField("Slug", unique=True)
    title = models.CharField("Page Title", max_length=500, blank=False)
    show_menu = models.BooleanField("Show in menus", default=True)
    search = models.CharField("Search description", max_length=500)
    minimum_questions = models.PositiveIntegerField("Minimum questions answered")
    minimum_percentage = models.PositiveIntegerField(
        "Minimum % gained for all questions answered", choices=PERCENTAGE_CHOICES)
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
    question_order = models.PositiveIntegerField("Question Order", choices=QUESTION_ORDER_CHOICES, default=RANDOM)
    image = models.ImageField("Image", upload_to="img/", blank=True, null=True)

    def __unicode__(self):
        return self.name


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


class HarambeeModuleRel(models.Model):

    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    module = models.ForeignKey(Module, null=False, blank=False)


class HarambeeLevelRel(models.Model):

    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    level = models.ForeignKey(Level, null=False, blank=False)
    state = models.PositiveIntegerField(choices=STATE_CHOICES, default=ACTIVE)
    date_started = models.DateTimeField("Date Started", auto_now_add=True, null=True, blank=True)
    date_completed = models.DateTimeField("Date Completed", null=True, blank=True)
    attempt = models.PositiveIntegerField("Attempt Number")


class HarambeeQuestionAnswer(models.Model):

    harambee = models.ForeignKey('my_auth.Harambee', null=False, blank=False)
    question = models.ForeignKey(LevelQuestion, null=False, blank=False)
    option_selected = models.ForeignKey(LevelQuestionOption, null=False, blank=False)
    date_answered = models.DateTimeField(null=False, blank=False)
    harambee_level_rel = models.ForeignKey(HarambeeLevelRel, null=False, blank=False)

    class Meta:
        verbose_name = "Level Question Answer"
        verbose_name_plural = "Level Question Answers"
