import pandas as pd
import app.model.colname as cname
import app.model.utils as utils
from datetime import datetime
import os
import enum

class alloc_status(enum.Enum):
    pending = 0
    nodatesavailable = 1
    unabletoretrieve = 2
    availabilitynotgiven = 3

class DatabaseQuery():
    def __init__(self, default_replies: dict = None):
        here = os.path.dirname(os.path.abspath(__file__))
        self.excel_data = pd.read_excel(io=cname.excel_filepath, sheet_name=[0,1,2,3,4]) #, converters={cname.op_date:str})
        self.parents_profile = self.excel_data[0]
        self.op_dates = self.excel_data[1]
        self.parents_avail = self.excel_data[2]
        self.cc_vacancy = self.excel_data[3]
        self.repliesDF = self.excel_data[4]
        if default_replies == None:
            self.replies = {}
            for index, row in self.repliesDF.iterrows():
                self.replies[row[cname.purpose]] = row[cname.response]
        else:
            self.replies = default_replies

    def registerUser(self, tgUserid: str, matchingId: str, withUsername: bool):
        colname = cname.tg_user if withUsername else cname.email
        temp_list = self.parents_profile.index[self.parents_profile[colname] == matchingId].tolist()
        if len(temp_list) > 0:
            parent_profile_rl = temp_list[0]
            self.parents_profile.at[parent_profile_rl, cname.tg_id] = tgUserid
            success = True
        else:
            success = False
        if success: self.saveExcelFile(cname.excel_filepath)
        return success

    def getAllocation(self, tgUserid: str) -> str:
        dr = self.parents_profile.loc[self.parents_profile[cname.tg_id] == int(tgUserid)]
        allocatedDate = dr[cname.op_date].values[0] if not dr.empty else "None"
        if str(allocatedDate) == 'nan':
            allocatedDate = alloc_status.pending.name
        elif allocatedDate.lower() == alloc_status.unabletoretrieve.name:
            allocatedDate = alloc_status.availabilitynotgiven.name
        elif allocatedDate.lower() == alloc_status.nodatesavailable.name:
            allocatedDate = alloc_status.nodatesavailable.name
        elif utils.convertdate_for_display(allocatedDate) == "None":
            allocatedDate = "error"
        return allocatedDate

    def cancelAllocation(self, tgUserid: str):
        temp_list = self.parents_profile.index[self.parents_profile[cname.tg_id] == int(tgUserid)].tolist()
        if len(temp_list) > 0:
            parent_profile_rl = temp_list[0]
            curr_alloc_date = self.getAllocation(tgUserid=tgUserid)
            if utils.convertdate_for_display(curr_alloc_date) != 'None':
                curr_alloc_date_rl = self.op_dates.index[self.op_dates[cname.op_date] == curr_alloc_date].tolist()[0]
                self.parents_profile.at[parent_profile_rl, cname.op_date] = utils.blank_date_string # remove allocated date
                self.op_dates.at[curr_alloc_date_rl, cname.vacancy_alloc] = self.op_dates.at[curr_alloc_date_rl, cname.vacancy_alloc] - 1 # reduce vacancy count
                self.parents_profile.at[parent_profile_rl, cname.alloc_curr] = datetime.strftime(datetime.now(), utils.dateformat_currency) # update allocation currency
            success = True
        else:
            success = False
        if success: self.saveExcelFile(cname.excel_filepath)
        return success

    def setAllocation(self, tgUserid: str, new_alloc_date: str) -> bool:
        temp_list1 = self.parents_profile.index[self.parents_profile[cname.tg_id] == int(tgUserid)].tolist()
        temp_list2 = self.op_dates.index[self.op_dates[cname.op_date] == new_alloc_date].tolist()
        if len(temp_list1) > 0 and len(temp_list2) > 0:
            # get row labels of parent and new_alloc_date
            parent_profile_rl = temp_list1[0]
            new_alloc_date_rl = temp_list2[0]

            # check if parent has an allocated date currently
            curr_alloc_date = self.getAllocation(tgUserid=tgUserid)
            if utils.convertdate_for_display(curr_alloc_date) != 'None':
                curr_alloc_date_rl = self.op_dates.index[self.op_dates[cname.op_date] == curr_alloc_date].tolist()[0]
            else:
                curr_alloc_date_rl = -1

            # update allocated date
            if curr_alloc_date != new_alloc_date:
                self.parents_profile.at[parent_profile_rl, cname.op_date] = new_alloc_date # update allocated date
                self.op_dates.at[new_alloc_date_rl, cname.vacancy_alloc] = self.op_dates.at[new_alloc_date_rl, cname.vacancy_alloc] + 1 # increase vacancy count
                if curr_alloc_date_rl != -1:
                    self.op_dates.at[curr_alloc_date_rl, cname.vacancy_alloc] = self.op_dates.at[curr_alloc_date_rl, cname.vacancy_alloc] - 1 # reduce vacancy count
                self.parents_profile.at[parent_profile_rl, cname.alloc_curr] = datetime.strftime(datetime.now(), '%d/%m/%y %H:%M') # update allocation currency
            success = True
        else:
            success = False
        if success: self.saveExcelFile(cname.excel_filepath)
        return success

    def getAvailability(self, tgUserid: str) -> [str]:
        availabilities = []
        dr = self.parents_profile.loc[self.parents_profile[cname.tg_id] == int(tgUserid)]
        if not dr.empty:
            parentIdx = dr.iloc[0][cname.parentId]
            dr = self.parents_avail.loc[self.parents_avail[cname.parentId] == int(parentIdx)]
            nbr_data_col = len(dr.columns)
            for date_idx in range(nbr_data_col):
                date_colname = cname.avail_date.format(idx=date_idx)
                if date_colname in dr.columns.values and dr.iloc[0][date_colname] == 1:
                    rl = self.op_dates.index[self.op_dates[cname.dateId] == date_idx].tolist()[0]
                    availabilities.append(self.op_dates.at[rl, cname.op_date])
        return availabilities

    def setAvailability(self, tgUserid: str, date: str, set: bool) -> bool:
        templist1 = self.op_dates.index[self.op_dates[cname.op_date] == date].tolist()
        parentIdx = self.parents_profile.loc[self.parents_profile[cname.tg_id] == int(tgUserid)].iloc[0][cname.parentId]
        templist2 = self.parents_avail.index[self.parents_avail[cname.parentId] == int(parentIdx)].tolist()
        tag = 1 if set else 0
        if len(templist1) > 0 and len(templist2) > 0:
            date_rl = templist1[0]
            date_idx = int(self.op_dates.at[date_rl, cname.dateId])
            parent_rl = templist2[0]
            self.parents_avail.at[parent_rl, cname.avail_date.format(idx=date_idx)] = tag
            self.parents_avail.at[parent_rl, cname.resp_curr] = datetime.strftime(datetime.now(), utils.dateformat_currency)
            success = True
        else:
            success = False
        if success: self.saveExcelFile(cname.excel_filepath)
        return success

    def getVacantDates(self) -> [str]:
        vacantDates = []
        vacantDF = self.op_dates.query(cname.vacancy_alloc + ' < ' + cname.max_vacancy)
        for index, row in vacantDF.iterrows():
            vacantDates.append(row[cname.op_date])
        return vacantDates

    def getEventStartEnd(self, date: str) -> [str]:
        startend = []
        templist = self.op_dates.index[self.op_dates[cname.op_date] == date].tolist()
        if len(templist) > 0:
            date_rl = templist[0]
            startend.append(self.op_dates.at[date_rl, cname.event_start])
            startend.append(self.op_dates.at[date_rl, cname.event_end])
        return startend

    def checkIfRegistered(self, tgUserId: str) -> bool:
        templist = self.parents_profile.index[self.parents_profile[cname.tg_id] == int(tgUserId)].tolist()
        return (len(templist) > 0)

    def saveExcelFile(self, filename: str):
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        self.parents_profile.to_excel(writer, sheet_name=cname.parent_profile_shtname, index=False)
        self.op_dates.to_excel(writer, sheet_name=cname.opdates_shtname, index=False)
        self.parents_avail.to_excel(writer, sheet_name=cname.parent_avail_shtname, index=False)
        self.cc_vacancy.to_excel(writer, sheet_name=cname.vacancy_shtname, index=False)
        self.repliesDF.to_excel(writer, sheet_name=cname.response_shtname, index=False)
        writer.save()
        writer.close()

    def getReply(self, key: str):
        default_reply = 'Not reply mapping found for intent.'
        return self.replies.get(key, default_reply)

## debugging
# registerUser("6974211793", '@Coldraja', True)
# getAllocation("6974211793")
# getVacantDates()
# cancelAllocation("6974211793")
# setAllocation("6974211793", "10/10/20")
# getAvailability("6974211793")
# setAvailability("6974211793", '31/10/20', set=True)

