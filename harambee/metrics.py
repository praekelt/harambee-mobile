from django.db.models import Count
from datetime import datetime, timedelta
from my_auth.models import Harambee, HarambeeLog
from content.models import HarambeeJourneyModuleRel, HarambeeJourneyModuleLevelRel, LevelQuestion, \
    HarambeeQuestionAnswer, Level, JourneyModuleRel, HarambeeeQuestionAnswerTime
import json


def get_number_registered_users():
    return Harambee.objects.all().aggregate(Count('id'))['id__count']


def get_number_active_users_today():
    now = datetime.now()
    yesterday = datetime.datetime.now() - timedelta(hours=24)
    return Harambee.objects.filter(last_login__gt=yesterday, last_login__lt=now).aggregate(Count('id'))['id__count']


def get_number_inactive_users():
    two_weeks_ago = datetime.datetime.now() - timedelta(days=14)
    return Harambee.objects.filter(last_login__lt=two_weeks_ago).aggregate(Count('id'))['id__count']


def get_active_user_ids_today():
    now = datetime.now()
    yesterday = datetime.datetime.now() - timedelta(hours=24)
    return Harambee.objects.filter(last_login__gt=yesterday, last_login__lt=now).values_list('id', flat=True)


def get_number_active_users_per_module(journey_module_rel):
    two_weeks_ago = datetime.datetime.now() - timedelta(days=14)
    return HarambeeQuestionAnswer.objects.filter(
        harambee_level_rel__harambee_journey_module_rel__journey_module_rel=journey_module_rel,
        date_answered__gt=two_weeks_ago)\
        .aggregate(Count('id'))['id__count']


def get_active_user_ids_per_module(journey_module_rel):
    two_weeks_ago = datetime.datetime.now() - timedelta(days=14)
    return HarambeeQuestionAnswer.objects.filter(
        harambee_level_rel__harambee_journey_module_rel__journey_module_rel=journey_module_rel,
        date_answered__gt=two_weeks_ago).values_list('harambee__id', flat=True)


def get_number_active_logged_in_users_today_per_module(journey_module_rel):
    active_user_ids_per_module = get_active_user_ids_per_module(journey_module_rel)
    active_user_ids_today = get_active_user_ids_today()
    return Harambee.objects.filter(id__in=active_user_ids_per_module, id__in=active_user_ids_today)\
        .aggregate(Count('id'))['id__count']


def get_number_registered_users_per_module(journey_module_rel):
    return HarambeeJourneyModuleRel.objects.filter(journey_module_rel=journey_module_rel)\
        .aggregate(Count('id'))['id__count']


def get_number_completed_users_per_module(journey_module_rel):
    now = datetime.now()
    return HarambeeJourneyModuleRel.objects.filter(journey_module_rel=journey_module_rel, date_completed__lt=now)\
        .aggregate(Count('id'))['id__count']


def get_number_active_users_per_level(level):
    two_weeks_ago = datetime.datetime.now() - timedelta(days=14)
    return HarambeeJourneyModuleLevelRel.objects.filter(level=level, last_active__gt=two_weeks_ago)\
        .aggregate(Count('id'))['id__count']


def get_number_active_users_per_level_module(journey_module_rel):
    data = dict()
    for level in journey_module_rel.module.get_levels():
        data[level.name] = get_number_active_users_per_level(level)
    return data


def get_number_passed_users_per_level(level):
    return HarambeeJourneyModuleLevelRel.objects.filter(level=level, level_passed=True)\
        .aggregate(Count('id'))['id__count']


def get_number_passed_users_per_level_module(journey_module_rel):
    data = dict()
    for level in journey_module_rel.module.get_levels():
        data[level.name] = get_number_passed_users_per_level(level)
    return data

def get_correct_percentage_per_level(level):
    question_ids = LevelQuestion.objects.filter(level=level).values_list('id', flat=True)
    correct = HarambeeQuestionAnswer.objects.filter(question__id__in=question_ids, correct=True)\
        .aggregate(Count('id'))['id__count']
    return correct / level.get_num_questions() * 100


def get_average_correct_percentage_per_module_levels(journey_module_rel):
    num_levels = Level.objects.filter(module=journey_module_rel.module).aggregate(Count('id'))['id__count']
    levels = Level.objects.filter(module=journey_module_rel.module)
    total = 0
    for level in levels:
        total += get_correct_percentage_per_level(level)
    return total / num_levels


def get_num_questions_answered_per_level(level):
    question_ids = LevelQuestion.objects.filter(level=level).values_list('id', flat=True)
    num_answered = HarambeeQuestionAnswer.objects.filter(question__id__in=question_ids)\
        .aggregate(Count('id'))['id__count']
    return num_answered


def get_average_num_questions_answered_per_module_levels(journey_module_rel):
    num_levels = Level.objects.filter(module=journey_module_rel.module).aggregate(Count('id'))['id__count']
    levels = Level.objects.filter(module=journey_module_rel.module)
    total = 0
    for level in levels:
        total += get_num_questions_answered_per_level(level)
    return total / num_levels


def get_average_time_per_level(level):
    times = HarambeeeQuestionAnswerTime.objects.filter(harambee_level_rel__level=level)
    total_time = 0;
    for time in times:
        total_time += time.answer_time_in_minutes()
    return total_time/times.aggregate(Count('id'))['id__count']


def get_average_time_per_level_per_module(journey_module_rel):
    levels = journey_module_rel.module.get_levels()
    data = dict()
    for level in levels:
        data[level.name] = get_average_time_per_level(level)
    return data


def get_average_time_per_module(journey_module_rel):
    levels = journey_module_rel.module.get_levels()
    total_time = 0
    for level in levels:
        total_time += get_average_time_per_level(level)
    return total_time/levels.aggregate(Count('id'))['id__count']


def get_number_active_modules_per_harambee(harambee):
    return HarambeeJourneyModuleRel.objects.filter(harambee=harambee, state=HarambeeJourneyModuleRel.MODULE_ACTIVE)\
        .aggregate(Count('id'))['count__id']


def get_number_completed_modules_per_harambee(harambee):
    return HarambeeJourneyModuleRel.objects.filter(harambee=harambee, state=HarambeeJourneyModuleRel.MODULE_COMPLETE)\
        .aggregate(Count('id'))['count__id']


def get_level_achieved_in_module(harambee_journey_module_rel):
    return HarambeeJourneyModuleLevelRel.objects.filter(harambee_journey_module_rel=harambee_journey_module_rel)\
        .order_by('-level__order').first().order


def get_level_time_by_harmabee(harambee, level):
    try:
        times = HarambeeeQuestionAnswerTime.objects.filter(harambee=harambee, harambee_level_rel__level=level)
        total_time = 0;
        for time in times:
            total_time += time.answer_time_in_minutes()
        return total_time/times.aggregate(Count('id'))['id__count']
    except HarambeeeQuestionAnswerTime.DoesNotExist:
        return 0


def get_average_level_time_per_module(harambee_jounrey_module_rel):
    levels = harambee_jounrey_module_rel.journey_module_rel.module.get_levels()
    count = 0
    total_time = 0
    for level in levels:
        time = get_level_time_by_harmabee(harambee_jounrey_module_rel.harambee, level)
        if time > 0:
            total_time += time
            count += 1
    return total_time/count


def get_percentage_correct_in_level(harambee, level):
    num_answered = HarambeeQuestionAnswer.objects.filter(harambee=harambee, harambee_level_rel__level=level)\
        .aggregate(Count('id'))['count_id']
    num_correct = HarambeeQuestionAnswer.objects.filter(harambee=harambee, harambee_level_rel__level=level,
                                                        correct=True).aggregate(Count('id'))['count_id']
    return num_correct/num_answered * 100


def get_percentage_correct_in_level_per_module(harambee_journey_module_rel):
    levels = harambee_journey_module_rel.journey_module_rel.module.get_levels()
    data = dict()
    for level in levels:
        data[level.name] = get_percentage_correct_in_level(harambee_journey_module_rel.harambee, level)
    return data


def get_module_time(harambee_journey_module_rel):
    levels = harambee_journey_module_rel.journey_module_rel.module.get_levels()
    total_time = 0
    for level in levels:
        time = get_level_time_by_harmabee(harambee_journey_module_rel.harambee, level)
        if time > 0:
            total_time += time
    return total_time


def get_platform_time(harambee):
    modules = HarambeeJourneyModuleRel.objects.filter(harambee=harambee)
    total_time = 0
    for module in modules:
        total_time += get_module_time(module)
    return total_time


def get_number_logins(harambee):
    return HarambeeLog.objects.filter(harambee=harambee, action=HarambeeLog.LOGIN).aggregate(Count('id'))['count_id']


def get_number_logouts(harambee):
    return HarambeeLog.objects.filter(harambee=harambee, action=HarambeeLog.LOGOUT).aggregate(Count('id'))['count_id']


def create_json_stats():
    metrics = dict()

    #ALL USER STATS
    all_users = dict()
    all_users['tot_reg_usrs'] = get_number_registered_users()
    all_users['tot_act_usrs'] = get_number_active_users_today()
    all_users['tot_inact_usrs'] = get_number_inactive_users()

    metrics['all_users'] = all_users

    #PER MODULE OVERVIEW
    modules = list()
    journey_module_rel = JourneyModuleRel.objects.all()
    for rel in journey_module_rel:
        data = dict()
        data['tot_login'] = get_number_active_users_per_module(rel)
        data['tot_start'] = get_number_registered_users_per_module(rel)
        data['tot_act'] = get_number_active_logged_in_users_today_per_module(rel)
        data['tot_comp'] = get_number_completed_users_per_module(rel)
        data['tot_act_lvl'] = get_number_active_users_per_module(rel)
        data['tot_compl_lvl'] = get_number_passed_users_per_level_module(rel);
        data['lvl_avg_perc_cor'] = get_average_correct_percentage_per_module_levels(rel)
        data['avg_quest_ans'] = get_average_num_questions_answered_per_module_levels(rel)
        data['avg_lvl_time'] = get_average_time_per_level_per_module(rel)
        data['avg_mod_time'] = get_average_time_per_module(rel)

        modules.append({'name': rel.module.name, 'data': data})

    metrics['modules'] = modules

    #INDIVIDUAL
    harambees = list()
    all_harambees = Harambee.objects.all()
    for harambee in all_harambees:
        harambee_data = dict()
        harambee_data['num_login'] = get_number_logins(harambee)
        harambee_data['num_logout'] = get_number_logouts(harambee)
        harambee_data['plat_time'] = get_platform_time(harambee)
        harambee_data['act_mod'] = get_number_active_modules_per_harambee(harambee)
        harambee_data['comp_mod'] = get_number_completed_modules_per_harambee(harambee)

        modules_list = list()
        modules_query_set = HarambeeJourneyModuleRel.objects.filter(harambee=harambee)
        for rel in modules_query_set:
            module_data = dict()
            module_data['lvl_achi'] = get_level_achieved_in_module(rel)
            module_data['lvl_avg_time'] = get_average_level_time_per_module(rel)
            module_data['lvl_perc_cor'] = get_percentage_correct_in_level_per_module(rel)
            module_data['mod_time'] = get_module_time(rel)

            modules_list.append({'module_name': rel.module.name, 'module_data': module_data})

        harambees.append({'candidate_id': harambee.candidate_id, 'data': harambee_data, 'modules': modules_list})

    metrics['harambees'] = harambees

    json.dumps([metrics])