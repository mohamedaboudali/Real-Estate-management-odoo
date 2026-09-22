from odoo import models, fields, api

class LeaseRequestWizard(models.TransientModel):
    _name = 'lease.request.wizard'
    _description = 'Lease Request Wizard'
    
    lease_id = fields.Many2one('real_estate.lease', required=True)
    tenant_id = fields.Many2one('real_estate.tenant', required=True)
    property_id = fields.Many2one('real_estate.property', related='lease_id.property_id', readonly=True)
    
    name = fields.Char(string='Lease Reference', required=True, readonly=True, default='New')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    
    description = fields.Text(string='Description')
    
    
    def action_create_lease(self):
        
        self.ensure_one()

    #Create maintenance.request record
        self.action_create_lease = self.env['real_estate.lease'].create({
            'property_id': self.property_id.id,
            'tenant_id': self.tenant_id.id,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'monthly_rent': self.monthly_rent,
            'state': 'submitted',
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
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Request Submitted',
                'message': 'Your lease request has been submitted successfully and the manager has been notified.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }