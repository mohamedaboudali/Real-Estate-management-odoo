from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_type = fields.Selection(
        [
            ('apartment', 'Apartment'),
            ('house', 'House'),
            ('villa', 'Villa'),
            ('commercial', 'Commercial'),
        ],
        string='Property Type',
        required=False,
        default='apartment',
    )

    def update_description(self):
        for record in self:
            record.write({"description": record.name})