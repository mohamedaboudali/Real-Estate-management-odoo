from odoo import models, fields, api

class CreateTenantWizard(models.TransientModel):
    _name = 'tenant.request.wizard'
    _description = 'Tenant Request Wizard'
    
    lead_id = fields.Many2one('crm.lead', string='CRM Lead')
    name = fields.Char(string='Tenant Name')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    city = fields.Char(string='City')
    

    @api.model
    def default_get(self, fields):
        res = super(CreateTenantWizard, self).default_get(fields)
        lead_id = self.env.context.get('active_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)
            res.update({
                'lead_id': lead.id,
                'name': lead.contact_name or lead.name,
                'phone': lead.phone,
                'mobile': lead.mobile,
                'email': lead.email_from,
                'city': lead.city,
            })
        return res
        
    
    def action_create_tenant(self):
        
        self.ensure_one()

    #Create maintenance.request record
        tenant = self.env['real_estate.tenant'].sudo().create({
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'city': self.city,
            'crm_id': self.lead_id.id,
        })
        
        #  #Send notification to property manager (Agent)
        # if self.property_id.agent_id:
        #      maintenance_request.activity_schedule(
        #          'mail.mail_activity_data_todo',
        #          user_id=self.property_id.agent_id.id,
        #          summary=f"New {self.issue_type.capitalize()} Maintenance Request",
        #          note=f"Urgency: {self.urgency}\nDescription: {self.description}"
        #      )

        # 3. Return action to close wizard and show confirmation
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Request Submitted',
        #         'message': 'Your lease request has been submitted successfully and the manager has been notified.',
        #         'type': 'success',
        #         'sticky': False,
        #         'next': {'type': 'ir.actions.act_window_close'},
        #     },
        # }
        return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'real_estate.tenant',
                    'res_id': tenant.id,
                    'views': [(False, 'form')],
                    'target': 'current',
                }