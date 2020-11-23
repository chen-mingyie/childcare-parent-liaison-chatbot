from datetime import datetime

dateformat_display = '%a, %d %b %Y'
dateformat_backend = '%d/%m/%y'
dateformat_currency = '%d/%m/%y %H:%M'
blank_date_string = 'NoDatesAvailable'

# convert dd/mm/yy to day, dd Mmm yy
def convertdate_for_display(date_string: str) -> str:
    try:
        dateobj = datetime.strptime(date_string, dateformat_backend)
        date = datetime.strftime(dateobj, dateformat_display)
    except:
        date = "None"
    return date

def convertdate_for_datebase(date_string: str) -> str:
    try:
        dateobj = datetime.strptime(date_string, dateformat_display)
        date = datetime.strftime(dateobj, dateformat_backend)
    except:
        date = "None"
    return date