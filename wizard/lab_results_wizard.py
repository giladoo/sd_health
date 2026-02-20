from odoo import models, fields, api, _
import json
from datetime import datetime, timedelta
import pytz
from odoo.tools import date_utils, format_date

from odoo.exceptions import ValidationError


class SdHealthLabResultsWizard(models.TransientModel):
    _name = 'sd_health.lab_results_wizard'
    _description = "lab_results_wizard"




    def attendance_report(self):
        read_form = self.read()[0]
        data = {'form_data': read_form}
        # print(f"\n {data}")

        return self.env.ref('sd_contacts.attendance_list_report').report_action(self, data=data)

