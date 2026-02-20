
from odoo import models, fields, api, _
from odoo.osv import expression

from datetime import datetime
import pytz

class SdHealthPatients(models.Model):
    _name = "sd_health.patients"
    _description = "Patients"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_names_search = ['name', 'national_id']

    name = fields.Char( required=True, tracking=True)
    national_id = fields.Char( required=True, tracking=True)
    gender = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other'),],
                              required=True, tracking=True, default='male')
    birth_date = fields.Date(required=True, tracking=True)
    age = fields.Integer(compute="_age_compute",)
    height = fields.Float(required=True, tracking=True)

    mobile_no = fields.Char()
    emergency_phone = fields.Char()

    image = fields.Image()
    blood_group = fields.Selection(
        selection=[
            ('a+', 'A+'),
            ('a-', 'A-'),
            ('b+', 'B+'),
            ('b-', 'B-'),
            ('ab+', 'AB+'),
            ('ab-', 'AB-'),
            ('o+', 'O+'),
            ('o-', 'O-'),
        ],
        string='Blood Group',
        required=False, tracking=True
    )

    old_disease = fields.Boolean(tracking=True)
    present_disease = fields.Boolean(tracking=True)
    medication_records = fields.Boolean(tracking=True)
    drug_sensitivity = fields.Boolean(tracking=True)
    smoking_drug_history = fields.Boolean(tracking=True)
    surgery_hospitalization = fields.Boolean(tracking=True)
    description = fields.Html()
    lab_result_id = fields.One2many('sd_health.lab_results', 'patient_id')

    @api.depends('birth_date',)
    @api.onchange('birth_date',)
    def _age_compute(self):
        for rec in self:
            if rec.birth_date:
                rec.age = datetime.now().year - rec.birth_date.year
            else:
                rec.age = 0

    @api.depends('name', 'national_id')
    # @api.depends_context('allowed_company_ids')
    def _compute_display_name(self):
        super()._compute_display_name()
        for rec in self:
            # if rec.name == team_default_name:
            rec.display_name = f'{rec.name} - {rec.national_id}'

    def show_lab_results(self):
        context = self.env.context
        print('>>>>> context:', context)