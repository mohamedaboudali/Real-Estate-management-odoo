import string

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class Lease(models.Model):
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'
    
    name = fields.Char(string='Lease Reference', required=True, readonly=True, default='New')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    deposit_paid = fields.Float(string='Deposit Paid')
    user_id = fields.Many2one('res.users', string='Created By', index=True)
    maintenance_count = fields.Integer(string='Maintenance', compute='_compute_maintenance_count')
    duration_months = fields.Integer(string='Duration (Months)', compute='_compute_duration', store=True)
    is_active = fields.Boolean(string='Currently Active', compute='_compute_is_active')
    next_service = fields.Date(string='Next Service' ,onchange="_onchange_next_service")
    payment_ids = fields.One2many('real_estate.payment', 'lease_id', string='Payments')
    maintenance_ids = fields.One2many('real_estate.maintenance', 'lease_id', string='Maintenance') 
    #total_cost = fields.Float(compute='_compute_total_cost', string='Total Cost')
    plumbing_count = fields.Integer(string='Plumbing', compute='_compute_maintenance_by_type')
    electrical_count = fields.Integer(string='Electrical', compute='_compute_maintenance_by_type')
    air_condition_count = fields.Integer(string='Air Condition', compute='_compute_maintenance_by_type')
    appliance_count = fields.Integer(string='Appliance', compute='_compute_maintenance_by_type')
    other_count = fields.Integer(string='Other', compute='_compute_maintenance_by_type')

    total_cash_amount = fields.Float(
        string= 'Total Cash Amount', compute='_compute_payment_information', store=True)
    total_visa_amount = fields.Float(
        string= 'Total Visa Amount', compute='_compute_payment_information', store=True)
    total_payment_amount = fields.Float(
        string= 'Total Payment Amount', compute='_compute_payment_information', store=True)

    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        ondelete='cascade',  # If property deleted, delete lease too
        index=True)
    
    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        ondelete='cascade',
        index=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

    @api.depends('maintenance_ids.issue_type')
    def _compute_maintenance_by_type(self):
        for record in self:
           types_count = {
                'plumbing': 0,
                'electrical': 0,
                'air_condition': 0,
                'appliance': 0,
                'other': 0,
        }
        for maintenance in record.maintenance_ids:
            if maintenance.issue_type in types_count:
                types_count[maintenance.issue_type] += 1

        record.plumbing_count = types_count['plumbing']
        record.electrical_count = types_count['electrical']
        record.air_condition_count = types_count['air_condition']
        record.appliance_count = types_count['appliance']
        record.other_count = types_count['other']

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Calculate lease duration in months"""
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_months = int(delta.days / 30)
            else:
                record.duration_months = 0

    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        """Check if lease is currently active"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.start_date and record.end_date:
                record.is_active = record.start_date <= today <= record.end_date
            else:
                record.is_active = False

    @api.depends('maintenance_ids')
    def _compute_maintenance_count(self):
      for record in self:
        record.maintenance_count = len(record.maintenance_ids)

    def action_view_maintenance(self):
     self.ensure_one()

     return {
        'type': 'ir.actions.act_window',
        'name': 'Maintenance Requests',
        'res_model': 'real_estate.maintenance',
        'view_mode': 'tree,form',
        'domain': [('lease_id', '=', self.id)],
        'context': {
            'default_lease_id': self.id,
        },
    }

    def _cron_auto_expire_leases(self):
        """Scheduled action - expire leases whose end date has passed"""
        today = fields.Date.today()
        expired_leases = self.search([
            ('end_date', '<', today),
        ])
        for lease in expired_leases:
            lease.write({'state': 'expired'})

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

    @api.onchange('property_id')
    def _onchange_property_id(self):
            """Set default price when property is selected and validate availability"""
            if self.property_id and not self.property_id.available:
                raise UserError("The selected property is not available.")
            if self.property_id and self.property_id.price:
                self.monthly_rent = self.property_id.price
                self.deposit_paid = self.monthly_rent.price * 0.10

    @api.onchange('start_date')
    def _onchange_next_service_date(self):
            if self.start_date:
                self.next_service = (
                    self.start_date + relativedelta(month=1)
                )
                    
            else:
                self.next_service = False

    def action_create_maintenance(self):
            
        self.ensure_one()

        maintenance = self.env['real_estate.maintenance'].sudo().create({
            'issue_type': 'electrical',
            'description': 'new service',
            'scheduled_date': self.next_service,
            'lease_id': self.id,
        })
    
        return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'real_estate.maintenance',
                    'res_id': maintenance.id,
                    'views': [(False, 'form')],
                    'target': 'current',
                }

    @api.depends('payment_ids.amount', 'payment_ids.payment_method', 'payment_ids.state')
    def _compute_payment_information(self):
        for record in self:
            costs = {
                type_name: sum(
                    record.payment_ids.filtered(
                        lambda payment: payment.payment_method == type_name
                    ).mapped('amount')
                )
                for type_name in ['cash', 'check', 'bank transfer', 'credit card', 'other']
            }

            record.total_cash_amount = costs['cash']
            record.total_visa_amount = costs['check']
            record.total_payment_amount = costs['bank transfer']
            record.total_payment_amount += costs['credit card']
            record.total_payment_amount += costs['other']

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Ensure end date is after start date"""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError("End date must be after start date")

    @api.constrains('monthly_rent', 'deposit_paid')
    def _check_rent_and_deposit(self):
        """ensure deposit is not greater than monthly rent"""
        for record in self:
            if record.deposit_paid > record.monthly_rent:
                raise ValidationError("Deposit cannot be greater than monthly rent")
                
    #@api.depends('maintenance_ids.actual_cost')
    #def _compute_total_cost(self):
        #for lease in self:
            # 1
            #lease.total_cost = sum(maintenance.actual_cost for maintenance in lease.maintenance_ids)

            # 2
            # lease.total_cost = 0
            # total_cost = 0
            # for maintenance in lease.maintenance_ids:
            #     if maintenance.actual_cost:
            #         total_cost += maintenance.actual_cost
            # lease.total_cost = total_cost   

            # 3
            #lease_maintenance_ids = self.env['maintenance.request'].search([('lease_id', '=', lease.id)])  
            #lease.total_cost = 0
            #for maintenance in lease_maintenance_ids:
            #    if maintenance.actual_cost:
            #        lease.total_cost += maintenance.actual_cost

    # def write(self, vals):
    #      if not self.env.user.has_group('real_estate.group_tenant_manager'):
    #          raise UserError("Only tenant managers can modify this record.")
            