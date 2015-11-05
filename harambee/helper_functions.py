from __future__ import division
from content.models import JourneyModuleRel, Journey, HarambeeJourneyModuleRel, HarambeeJourneyModuleLevelRel, Level, \
    HarambeeQuestionAnswer
from django.utils import timezone
from django.db.models import Count


#########################JOURNEYS#########################
def get_live_journeys():
    all_journeys = Journey.objects.all()
    journey_id__list = []
    for journey in all_journeys:
        if journey.start_date:
            if journey.start_date <= timezone.now():
                if journey.end_date:
                    if journey.end_date > timezone.now():
                        journey_id__list.append(journey.id)
                else:
                    journey_id__list.append(journey.id)

    return Journey.objects.filter(id__in=journey_id__list)


def get_menu_journeys():
    return get_live_journeys().filter(show_menu=True)


#########################MODULUES#########################
def get_live_modules():
    """
    Returns all live modules. Module is live if start date is set and is not greater than current date.
    The current date also needs to be less than end date or end date must not be set for module to be live.
    """

    all_module_rel = JourneyModuleRel.objects.all()
    module_rel_id_list = []

    for module_rel in all_module_rel:
        if module_rel.module.start_date:
            if module_rel.module.start_date <= timezone.now():
                if module_rel.module.end_date:
                    if module_rel.module.end_date >= timezone.now():
                        module_rel_id_list.append(module_rel.id)
                else:
                    module_rel_id_list.append(module_rel.id)

    return JourneyModuleRel.objects.filter(id__in=module_rel_id_list)


def get_modules_by_journey(journey):
    return JourneyModuleRel.objects.filter(journey=journey)


def get_live_modules_by_journey(journey):
    module_rel_id_list = get_live_modules().values_list('id', flat=True)
    return get_modules_by_journey(journey).filter(id__in=module_rel_id_list)


def get_menu_modules():
    return get_live_modules().filter(show_menu=True)


def get_recommended_modules(journey, harambee):
    '''
    Return modules are linked to this journey and have not been started by the user and have recommended set to true
    '''
    exclude_list = list()
    exclude_list = exclude_list + list(get_harambee_active_modules(harambee).values_list('id', flat=True))
    exclude_list = exclude_list + list(get_harambee_completed_modules(harambee).values_list('id', flat=True))

    return get_live_modules_by_journey(journey).exclude(id__in=exclude_list)


def get_harambee_active_modules_by_survey(harambee, journey):
    module_rel_id_list = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                                 journey_module_rel__journey=journey,
                                                                 state=HarambeeJourneyModuleRel.MODULE_ACTIVE)\
        .values_list('journey_module_rel__id', flat=True)

    return get_live_modules().filter(id__in=module_rel_id_list)


def get_harambee_active_modules(harambee):
    return HarambeeJourneyModuleRel.objects.filter(harambee=harambee, state=HarambeeJourneyModuleRel.MODULE_ACTIVE)


def get_harambee_completed_modules(harambee):
    module_rel_id_list = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                                 state=HarambeeJourneyModuleRel.MODULE_COMPLETE)\
        .values_list('journey_module_rel__id', flat=True)

    return get_live_modules().filter(id__in=module_rel_id_list)


#########################LEVELS#########################
def get_live_levels(journey_module_rel):
    """
        Returns all the live levels linked to a specific module
    """
    all_levels = Level.objects.filter(module=journey_module_rel.module)

    active_levels_id = list()
    for level in all_levels:
        if level.is_active():
            active_levels_id.append(level.id)

    return all_levels.filter(id__in=active_levels_id)


def get_harambee_active_levels(harambee_journey_module_rel):
    """
        Return all the live active levels (HarambeeJourneyModuleLevelRel) liked to a specific module
    """
    all_module_level_rel = HarambeeJourneyModuleLevelRel.objects\
        .filter(harambee_journey_module_rel=harambee_journey_module_rel)

    latest_rel_id_list = list()
    for rel in all_module_level_rel:
        latest_rel_id_list.append(get_latest_level_rel(rel.harambee_journey_module_rel, rel.level).id)

    return all_module_level_rel.filter(id__in=latest_rel_id_list).order_by('level__order')


def get_harambee_locked_levels(harambee_journey_module_rel):
    """
        Returns all the live but locked levels linked a specific module
    """
    live_levels_id_list = get_live_levels(harambee_journey_module_rel.journey_module_rel).values_list('id', flat=True)
    active_levels_id_list = get_harambee_active_levels(harambee_journey_module_rel).values_list('level__id', flat=True)
    combined_list = list(live_levels_id_list) + list(active_levels_id_list)

    return Level.objects.filter(module=harambee_journey_module_rel.journey_module_rel.module,
                                id__in=live_levels_id_list)\
        .exclude(id__in=active_levels_id_list).order_by('order')


#########################MODULE RELATED DATA#########################
def get_module_data_by_journey(harambee, journey):
    """
        Returns all harambee module data for specific journey in a dictionary form
    """
    rel_id_list = JourneyModuleRel.objects.filter(journey=journey).values_list('id', flat=True)

    #can maybe send this through
    all_harambee_module_rel = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                                      journey_module_rel__module__in=rel_id_list)
    module_list_data = list()
    for module_rel in all_harambee_module_rel:
        module = get_module_data(module_rel)
        module_list_data.append(module)

    return module_list_data


def get_all_module_data(harambee):
    """
        Returns all harambee module data in a dictionary form
    """
    all_harambee_module_rel = HarambeeJourneyModuleRel.objects.filter(harambee=harambee)

    module_list_data = list()
    for module_rel in all_harambee_module_rel:
        module = get_module_data(module_rel)
        module_list_data.append(module)

    return module_list_data


def get_module_data(harambee_journey_module_rel):
    """
        Returns all harambee data for a specific module in a dictionary form
    """
    module = dict()
    module['module_id'] = harambee_journey_module_rel.journey_module_rel.module.id
    module['module_name'] = harambee_journey_module_rel.journey_module_rel.module.name
    module['module_slug'] = harambee_journey_module_rel.journey_module_rel.module.slug
    module['journey_colour'] = harambee_journey_module_rel.journey_module_rel.journey.colour

    module_levels = harambee_journey_module_rel.journey_module_rel.module.get_levels()
    module['total_levels'] = harambee_journey_module_rel.journey_module_rel.module.total_levels()

    count = 0
    for level in module_levels:
        level_rel = get_latest_level_rel(harambee_journey_module_rel, level)
        if level_rel:
            if level_rel.state == HarambeeJourneyModuleLevelRel.LEVEL_COMPLETE:
                count += 1

    module['levels_completed'] = count

    return module


def get_latest_level_rel(harambee_journey_module_rel, level):
    """
        Returns latest HarambeeJourneyModuleLevelRel
    """
    return HarambeeJourneyModuleLevelRel.objects.filter(harambee_journey_module_rel=harambee_journey_module_rel,
                                                        level=level).order_by('-level_attempt').first()


#########################LEVEL RELATED DATA#########################
def get_level_data(harambee_journey_module_level_rel):

    level = dict()
    level['id'] = harambee_journey_module_level_rel.level.id
    level['name'] = harambee_journey_module_level_rel.level.name
    level['streak'] = 0
    level['colour'] = harambee_journey_module_level_rel.harambee_journey_module_rel.journey_module_rel.journey.colour

    total_questions = harambee_journey_module_level_rel.level.get_num_questions()
    answered = HarambeeQuestionAnswer.objects\
        .filter(harambee=harambee_journey_module_level_rel.harambee_journey_module_rel.harambee,
                harambee_level_rel=harambee_journey_module_level_rel)
    percent_correct = answered.filter(option_selected__correct=True)\
        .aggregate(Count('id'))['id__count'] * 100 / total_questions

    level['questions_answered'] = answered.aggregate(Count('id'))['id__count']
    level['questions_correct'] = answered.filter(option_selected__correct=True).aggregate(Count('id'))['id__count']
    level['total_questions'] = total_questions
    level['percent_correct'] = percent_correct
    number_required = harambee_journey_module_level_rel.harambee_journey_module_rel.journey_module_rel.module.minimum_questions
    percent_required = harambee_journey_module_level_rel.harambee_journey_module_rel.journey_module_rel.module.minimum_percentage
    progress_percentage = (min(1.0, answered.aggregate(Count('id'))['id__count'] / number_required) +
                           min(1.0, percent_correct / percent_required)) / 2.0 * 100
    level['progress_percentage'] = int(progress_percentage)

    level['completed'] = (total_questions == answered.aggregate(Count('id'))['id__count'])

    return level