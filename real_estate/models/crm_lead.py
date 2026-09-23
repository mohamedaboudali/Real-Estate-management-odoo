from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    tenant_id = fields.Many2one('real_estate.tenant', string='Tenant')
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

    @api.model
    def _cron_create_tenant_from_crm(self):
        leads = self.search([('type', '=', 'lead'), ('property_type', '!=', False), ('tenant_id', '=', False)])
        for lead in leads.filtered(lambda l: l.partner_id and l.partner_id.email):
            try:
                tenant = self.env['real_estate.tenant'].create({
                'name': lead.partner_id.name,
                'email': lead.partner_id.email,
                'phone': lead.partner_id.phone,
                'crm_id': lead.id,
            })
            except Exception as e:
             self.env.cr.rollback()
            continue  # <-- skip this lead entirely, don't fall through to tenant.id
        lead.tenant_id = tenant.id