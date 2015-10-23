from content.models import JourneyModuleRel, Journey, Module, HarambeeJourneyModuleRel
from django.utils import timezone


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

def get_live_modules_by_journey(journey):
    ids = get_live_modules().values_list("id", flat=True)
    return get_modules_by_journey(journey).exclude(module__id__in=ids)

def get_modules_by_journey(journey):
    return JourneyModuleRel.objects.filter(journey=journey)


def get_menu_modules():
    return get_live_modules().filter(show_menu=True)


def get_recommended_modules(journey, harambee):
    '''
    Return modules are linked to this journey and have not been started by the user and have recommended set to true
    '''
    module_id_list = get_modules_by_journey(journey).filter(module__show_recommended=True)\
        .values_list('id', flat=True)

    exclude_list = list()
    exclude_list = exclude_list + list(get_harambee_active_modules(harambee).values_list('id', flat=True))
    exclude_list = exclude_list + list(get_harambee_completed_modules(harambee).values_list('id', flat=True))

    return get_live_modules_by_journey(journey).filter(id__in=module_id_list).exclude(module__id__in=exclude_list)


def get_harambee_active_modules_by_survey(harambee, journey):
    module_id_list = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                             journey_module_rel__journey=journey,
                                                             state=HarambeeJourneyModuleRel.MODULE_ACTIVE)\
        .values_list('journey_module_rel__module__id', flat=True)

    return get_live_modules().filter(id__in=module_id_list)


def get_harambee_active_modules(harambee):
    return HarambeeJourneyModuleRel.objects.filter(harambee=harambee, state=HarambeeJourneyModuleRel.MODULE_ACTIVE)


def get_harambee_completed_modules(harambee):
    module_id_list = HarambeeJourneyModuleRel.objects.filter(harambee=harambee,
                                                             state=HarambeeJourneyModuleRel.MODULE_COMPLETE)\
        .values_list('journey_module_rel__module__id', flat=True)

    return get_live_modules().filter(id__in=module_id_list)


##########################################
