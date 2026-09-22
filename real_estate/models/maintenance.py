from odoo import models, fields, api

class MaintenanceRequest(models.Model):
    _name = 'real_estate.maintenance'
    _description = 'Property Maintenance Request'
    
    name = fields.Char()
    lease_id = fields.Many2one('real_estate.lease')
    tenant_id = fields.Many2one('real_estate.tenant', related='lease_id.tenant_id', store=True)
    property_id = fields.Many2one('real_estate.property', related='lease_id.property_id', store=True)
    user_id = fields.Many2one('res.users', string='Created By', index=True)
    preferred_date = fields.Date()
    state = fields.Text(string='state')
    tenant_phone = fields.Char()
    issue_type = fields.Selection([
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('air_condition', 'Air Condition'),
        ('appliance', 'Appliance'),
        ('other', 'Other')
    ], required=True)
    description = fields.Text(required=True)
    urgency = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency')
    ], default='medium', required=True)
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    scheduled_date = fields.Date()
    completion_date = fields.Date()
    actual_cost = fields.Float()

    