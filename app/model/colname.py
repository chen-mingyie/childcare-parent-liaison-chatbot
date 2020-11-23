import os
from pathlib import Path

# file and sheet name
excel_filepath = ""
db_folderpath = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
for file in os.listdir(db_folderpath):
    if file.endswith(".xlsx"):
        excel_filepath = os.path.join(db_folderpath, file)
        break
# excel_filepath = os.path.join(db_folderpath, "Sample_database.v3.3.xlsx")
parent_profile_shtname = 'waitingList'
opdates_shtname = 'openHouseDates'
parent_avail_shtname = 'parentAvailability'
vacancy_shtname = 'childcareVacancy'
response_shtname = 'intentResponse'

# from waitingList sheet
parentId = 'parentId'
first_name = 'firstName'
last_name = 'lastName'
email = 'email'
sch_level = 'level'
enrol_mth = 'enrolmentMth'
tg_user = 'tgUsername'
tg_id = 'tgUserId'
op_date = 'openHouseDate'
alloc_curr = 'allocationCurrency'
responded = 'invitationResponded'

# from openHouseDates sheet
dateId = 'dateId'
event_start = 'startTime'
event_end = 'endTime'
vacancy_alloc = 'vacancyAllocated'
max_vacancy = 'maxVacancy'
cutoff = 'cutoffDate'

# from parentAvailability sheet
resp_curr = 'responseCurrency'
avail_date = 'date{idx}'

# from intentResponse sheet
purpose = 'intent'
response = 'response'
i_welcome = 'welcome'
i_reg_user = 'register_user'
i_reg_pass = 'register_success'
i_reg_fail = 'register_fail'
i_alloc_get = 'alloc_get'
i_alloc_get_fail_pend = 'alloc_get_fail_pending'
i_alloc_get_fail1 = 'alloc_get_fail1'
i_alloc_get_fail2 = 'alloc_get_fail2'
i_alloc_get_fail3 = 'alloc_get_fail3'
i_alloc_chg_pass = 'alloc_change_success'
i_alloc_chg_fail = 'alloc_change_fail_pending'
i_alloc_cancel_pass = 'alloc_cancel_success'
i_alloc_cancel_fail1 = 'alloc_cancel_fail_syntax'
i_alloc_cancel_fail2 = 'alloc_cancel_fail_incorrect_date'
i_avail_set = 'avail_set'
i_avail_set_pass = 'avail_set_success'
i_avail_set_fail = 'avail_set_fail'
i_duration_user_alloc = 'event_duration_user_alloc'
i_duration_user_entered = 'event_duration_user_entered'
i_duration_invalid_date = 'event_duration_no_OP_on_date'
i_contConverse = 'contConverse'
i_endConverse = 'endConverse'


