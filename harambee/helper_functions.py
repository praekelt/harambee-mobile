from content.models import JourneyModuleRel, Journey, Module, HarambeeJourneyModuleRel, HarambeeJourneyModuleLevelRel, \
    Level
from django.utils import timezone
from django.db.models import Count

#############################################################

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


##########################################################
def get_live_modules():
    """
    Returns all live modules. Module is live if start date is set and is not greater than current date.
    The current date also needs to be less than end date or end date must not be set for module to be live.
    """

    all_modules = Module.objects.all()
    module_id__list = []
    for module in all_modules:
        if module.start_date:
            if module.start_date <= timezone.now():
                if module.end_date:
                    if module.end_date > timezone.now():
                        module_id__list.append(module.id)
                else:
                    module_id__list.append(module.id)

    return Module.objects.filter(id__in=module_id__list)


def get_modules_by_journey(journey):
    module_id_list = JourneyModuleRel.objects.filter(journey=journey).values_list('module__id')
    return Module.objects.filter(id__in=module_id_list)


def get_menu_modules():
    return get_live_modules().filter(show_menu=True)


def get_recommended_modules(journey, harambee):
    '''
    Return modules are linked to this journey and have not been started by the user and have recommended set to true
    '''
    module_id_list = get_modules_by_journey(journey).filter(show_recommended=True)\
        .values_list('id', flat=True)

    exclude_list = list()
    exclude_list = exclude_list + list(get_harambee_active_modules(harambee).values_list('id', flat=True))
    exclude_list = exclude_list + list(get_harambee_completed_modules(harambee).values_list('id', flat=True))

    return get_live_modules().filter(id__in=module_id_list).exclude(id__in=exclude_list)


def get_harambee_active_modules_by_survey(harambee, journey):
    module_id_list = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                             journey_module_rel__journey=journey,
                                                             state=HarambeeJourneyModuleRel.MODULE_ACTIVE)\
        .values_list('journey_module_rel__module__id', flat=True)

    return get_live_modules().filter(id__in=module_id_list)


def get_harambee_active_modules(harambee):
    module_id_list = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                             state=HarambeeJourneyModuleRel.MODULE_ACTIVE)\
        .values_list('journey_module_rel__module__id', flat=True)

    return get_live_modules().filter(id__in=module_id_list)


def get_harambee_completed_modules(harambee):
    module_id_list = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                             state=HarambeeJourneyModuleRel.MODULE_COMPLETE)\
        .values_list('journey_module_rel__module__id', flat=True)

    return get_live_modules().filter(id__in=module_id_list)


##########################################

def get_module_data_by_journey(harambee, journey):
    """
        Returns all harambee module data for specific journey in a dictionary form
    """
    module_id_list = JourneyModuleRel.objects.filter(journey=journey).values_list('module__id', flat=True)

    #can maybe send this through
    all_harambee_module_rel = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                                      journey_module_rel__module__in=module_id_list)
    module_list_data = list()
    for module_rel in all_harambee_module_rel:
        module = get_module_data(module_rel)
        module_list_data.append(module)


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
    module['module_id'] = module.journey_module_rel.module.id
    module['module_name'] = module.journey_module_rel.module.name

    module_levels = harambee_journey_module_rel.journey_module_rel.module.get_levels()
    module['total_levels'] = harambee_journey_module_rel.journey_module_rel.module.total_levels()

    count = 0
    for level in module_levels:
        level_rel = get_latest_level_rel(harambee_journey_module_rel, level)
        if level_rel.state == HarambeeJourneyModuleLevelRel.LEVEL_COMPLETE:
            count += 1

    module['levels_completed'] = count

    return module


def get_latest_level_rel(harambee_journey_module_level_rel, level):
    """
        Returns latest HarambeeJourneyModuleLevelRel
    """
    return HarambeeJourneyModuleLevelRel.objects.filter(harambee_journey_module_rel=harambee_journey_module_level_rel,
                                                        level=level).order_by('-level_attempt').first()
