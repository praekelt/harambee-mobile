from djcelery import celery
from rolefit.communication import save_stats
from harambee.metrics import create_json_stats
from django.core.mail import mail_managers
import json
from django.core.mail import EmailMessage
from datetime import datetime
from settings import MANAGERS, EMAIL_SUBJECT_PREFIX
import os


@celery.task(bind=True)
def send_metrics(self):
    stats = create_json_stats()
    email_stats(stats)
    save_stats(stats)


def compile_stats_message(stats):
    """
        Method complies a text message containing stats details.

        :param stats: dictionary containing harambee stats
        :return: Text message containing stats
        :rtype: string
    """
    message = ''

    total_user_stats = stats['all_users']
    message += 'USER STATS\n'
    message += 'Total Registered Users: %s\n' % total_user_stats['tot_reg_usrs']
    message += 'Total Active Users: %s\n' % total_user_stats['tot_act_usrs']
    message += 'Total Inactive Users: %s\n' % total_user_stats['tot_inact_usrs']
    message += '\n'
    message += '\n'

    message += 'MODULES STATS\n'
    all_modules = stats['modules']
    for module in all_modules:
        message += 'Module Name: %s\n' % module['name']
        data = module['data']
        message += 'Total Logged in Users: %s\n' % data['tot_login']
        message += 'Total Registered Users: %s\n' % data['tot_start']
        message += 'Total Users Logged In Today: %s\n' % data['tot_act']
        message += 'Total Users Completed Module: %s\n' % data['tot_comp']
        message += 'Total Active Users per Level\n'
        all_levels = data['tot_act_lvl']
        for key, value in all_levels.iteritems():
            message += '    %s: %s\n' % (key, value)
        message += 'Total Users Passed Level\n'
        all_levels = data['tot_compl_lvl']
        for key, value in all_levels.iteritems():
            message += '    %s: %s\n' % (key, value)
        message += 'Average Correct per Level: %s%%\n' % data['lvl_avg_perc_cor']
        message += 'Average Number of Questions Answered: %s\n' % data['avg_quest_ans']
        message += 'Average Time per Level\n'
        all_levels = data['avg_lvl_time']
        for key, value in all_levels.iteritems():
            message += '    %s: %s\n' % (key, value)
        message += 'Average Module Time: %s\n' % data['avg_mod_time']
        message += '\n'
    message += '\n'

    message += 'HARAMBEE STATS\n'
    all_harambees = stats['harambees']
    for harambee in all_harambees:
        message += 'Candidate ID: %s\n' % harambee['candidate_id']
        data = harambee['data']
        message += 'Number of Logins: %s\n' % data['num_login']
        message += 'Number of Logouts: %s\n' % data['num_logout']
        message += 'Platform Time: %s\n' % data['plat_time']
        message += 'Total Active Modules: %s\n' % data['act_mod']
        message += 'Total Completed Modules: %s\n' % data['comp_mod']

        all_modules = harambee['modules']
        if len(all_modules) > 0:
            message += 'MODULES\n'
        for module in all_modules:
            message += 'Module Name: %s\n' % module['module_name']
            data = module['module_data']
            message += 'Level Achieved: %s\n' % data['lvl_achi']
            message += 'Average Level Time: %s\n' % data['lvl_avg_time']
            message += 'Percent Correct per Level\n'
            all_levels = data['lvl_perc_cor']
            for key, value in all_levels.iteritems():
                message += '    %s: %s%%\n' % (key, value)
            message += 'Module Time: %s\n' % data['mod_time']
            message += '\n'
        message += '\n'
    message += '\n'

    message += 'QUESTION STATS\n'
    all_questions = stats['questions']
    for question in all_questions:
        message += 'Question Name: %s\n' % question['question_name']
        message += 'Percentage Correct: %s%%\n' % question['perc_cor']
        message += '\n'

    return message


def email_stats(stats):
    """
        Method take a json containing stats and emails them to the managers.
        :param stats: json containing harmabee stats
    """
    stats = json.loads(stats)
    message = compile_stats_message(stats)
    mail_managers('Harambee Daily Stats', message, fail_silently=False)

    #send json file
    subject = '%sJSON stats' % EMAIL_SUBJECT_PREFIX
    body = 'Harambee JSON stats file attached.'
    sent_from = ''
    send_to = []
    for item in MANAGERS:
        send_to.append(item[1])
    json_email = EmailMessage(subject, body, sent_from, send_to)
    filename = datetime.today().strftime('%y-%m-%d_harambee_stats.json')
    with open(filename, 'w') as outfile:
        json.dump(stats, outfile, indent=4)
    json_email.attach_file(filename)
    try:
        json_email.send()
    except Exception:
        pass
    try:
        os.remove(filename)
    except OSError:
        pass
