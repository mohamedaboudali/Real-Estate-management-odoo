from odoo import models, fields, api
from odoo.exceptions import UserError

class Lease(models.Model):
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'
    
    name = fields.Char(string='Lease Reference', required=True, readonly=True, default='New')
    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        ondelete='cascade',  # If property deleted, delete lease too
        index=True
    )
    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        ondelete='cascade',
        index=True
    )
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    deposit_paid = fields.Float(string='Deposit Paid')
    user_id = fields.Many2one('res.users', string='Created By', index=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

    def set_state_to_active(self):
            if not self.env.user.has_group('real_estate.group_tenant_manager'):
                raise UserError("Only tenant managers can modify this record.")
            for record in self:
                record.write({'state':'active'})

    def set_state_to_draft(self):
         for record in self:
              record.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        # if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
        return super(Lease, self).create(vals)

    def copy(self, default=None):
        default = default or {}
        if default.get('name'):
             default['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
        return super(Lease, self).copy(default)

    def write(self, vals):
        if not self.env.user.has_group('real_estate.group_property_manager'):
            raise UserError("Only property managers can modify this record.")
        return super(Lease, self).write(vals)

    def unlink(self):
        if not self.env.user.has_group('real_estate.group_property_manager'):
            raise UserError("Only property managers can delete this record.")


    # def write(self, vals):
    #      if not self.env.user.has_group('real_estate.group_tenant_manager'):
    #          raise UserError("Only tenant managers can modify this record.")
            