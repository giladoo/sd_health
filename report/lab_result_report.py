# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from jdatetimext import jdatejs


class SdHealthLabResultsReport(models.AbstractModel):
    _name = 'report.sd_health.lab_result_template'
    _description = 'lab_result_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # print(f">>>>>>>>>>>>>>> {docids} {data} \n {fields.Date.context_today(self)}")
        data = {
            'date': jdatejs(fields.Date.context_today(self), "%Y/%m/%d"),
        }
        return {
            'doc_ids' : docids,
            'doc_model' : self.env['sd_health.lab_results'],
            'data' : data,
            'docs' : self.env['sd_health.lab_results'].browse(docids),
        }