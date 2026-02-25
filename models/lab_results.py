
from odoo import models, fields, api, _
from odoo.osv import expression
import math
from datetime import datetime
import pytz

class SdHealthLabResults(models.Model):
    _name = "sd_health.lab_results"
    _description = "lab_results"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(copy=False, required=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('sd_health.patients')
    gender = fields.Selection(related='patient_id.gender')
    height = fields.Float(related='patient_id.height')
    age = fields.Integer(compute='_age_compute', store=True, readonly=False)
    record_date = fields.Date(required=True, tracking=True, default=fields.Date.context_today)
    weight = fields.Float()
    hba1c = fields.Float()
    lpa = fields.Float()
    apob = fields.Float()
    hs_crp = fields.Float()
    sbp = fields.Float()
    total_chol = fields.Float()
    hdl = fields.Float()
    smoker = fields.Boolean()
    description = fields.Text()

    bmi = fields.Float(compute="_bmi_calculation")
    lpa_score = fields.Integer(compute="_bmi_calculation")
    apob_score = fields.Integer(compute="_bmi_calculation")
    hba1c_score = fields.Integer(compute="_bmi_calculation")
    hscrp_score = fields.Integer(compute="_bmi_calculation")
    age_score = fields.Integer(compute="_bmi_calculation")
    bmi_score = fields.Integer(compute="_bmi_calculation")
    sbp_score = fields.Integer(compute="_bmi_calculation")
    chol_score = fields.Integer(compute="_bmi_calculation")
    smoker_score = fields.Integer(compute="_bmi_calculation")
    total_score = fields.Integer(compute="_bmi_calculation")
    risk_10yr = fields.Float(compute="_bmi_calculation")
    risk_level = fields.Selection([('very_low', 'Very Low'),
                                   ('low', 'Low'),
                                   ('moderate', 'Moderate'),
                                   ('high', 'High'),
                                   ('very_high', 'Very High'),

                                   ])



    @api.depends('patient_id')
    @api.onchange('patient_id')
    def _age_compute(self):
        for rec in self:
            if rec.patient_id.birth_date:
                rec.age = datetime.now().year - rec.patient_id.birth_date.year
            else:
                rec.age = 0

    @api.onchange('weight')
    def _bmi_calculation(self):
        for rec in self:
            # BMI
            rec.bmi = rec.weight / ((rec.patient_id.height/100) ** 2) if rec.patient_id.height else 0

            # نرمال‌سازی و Score
            rec.lpa_score = self.normalize_score(rec.lpa, [(30,0),(50,25),(75,50),(125,75),(float('inf'),100)])
            rec.apob_score = self.normalize_score(rec.apob, [(65,0),(80,25),(100,50),(130,75),(float('inf'),100)])
            rec.hba1c_score = self.normalize_score(rec.hba1c, [(5.4,0),(5.7,25),(6.5,50),(7.5,75),(float('inf'),100)])
            rec.hscrp_score = self.normalize_score(rec.hs_crp, [(1,0),(3,50),(float('inf'),100)])
            rec.age_score = max(0, min(100, (rec.age-20)/60*100))
            rec.bmi_score = max(0, min(100, (rec.bmi-18)/17*100))
            rec.sbp_score = self.normalize_score(rec.sbp, [(120,0),(130,25),(140,50),(160,75),(float('inf'),100)])
            chol_ratio = rec.total_chol / rec.hdl if rec.hdl else 0
            rec.chol_score = self.normalize_score(chol_ratio, [(3.5,0),(4,25),(5,50),(6,75),(float('inf'),100)])
            rec.smoker_score = 100 if rec.smoker else 0

            # Total Score
            rec.total_score = (
                    0.20 * rec.apob_score + 0.15 * rec.lpa_score + 0.15 * rec.hba1c_score + 0.10 * rec.hscrp_score +
                    0.10 * rec.age_score + 0.05 * rec.bmi_score + 0.10 * rec.sbp_score + 0.10 * rec.chol_score + 0.05 * rec.smoker_score
            )
            # 10-year risk
            rec.risk_10yr = 1 / (1 + math.exp(-(rec.total_score - 50) / 10)) * 100
            if rec.risk_10yr < 20:
                rec.risk_level = "very_low"
            elif rec.risk_10yr < 40:
                rec.risk_level = "low"
            elif rec.risk_10yr < 60:
                rec.risk_level = "moderate"
            elif rec.risk_10yr < 80:
                rec.risk_level = "high"
            else:
                rec.risk_level = "very_high"

    def show_results(self):
        view_id = self.env.ref('sd_health.lab_show_results_form').id
        return {
                    'type': 'ir.actions.act_window',
                    'name': 'Results',
                    'res_model': self._name,
                    'res_id': self.id,
                    'view_id': view_id,
                    'view_mode': 'form',
                    'target': 'new'
                }

    def print_results(self):
        return self.env.ref('sd_health.lab_result_report').report_action(self)

    def normalize_score(self, value, thresholds):
        for limit, score in thresholds:
            if value <= limit:
                return score
        return thresholds[-1][1]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sd_health.lab_results') or _('New')
        return super().create(vals_list)