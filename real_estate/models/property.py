from odoo import models, fields, api
from odoo.exceptions import UserError

class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True)    
    bedrooms = fields.Integer(string='Bedrooms', required=True)
    available = fields.Boolean(string='Available', default=True, index=True)   
    agent_id = fields.Many2one('res.users', string='Agent')
    lease_ids = fields.One2many('real_estate.lease', 'property_id', string='Leases') 
    lease_count = fields.Integer(string='Leases',compute='_compute_lease_count')

    

    
    property_type = fields.Selection([
            ('apartment', 'Apartment'),
            ('house', 'House'),
            ('villa', 'Villa'),
            ('commercial', 'Commercial'),
        ], string='Property Type', required=True)

    deposit = fields.Float(string='Deposit')

    @api.depends('lease_ids')
    def _compute_lease_count(self):
        for record in self:
            record.lease_count = len(record.lease_ids)

    def action_view_leases(self):
            self.ensure_one()

            return {
            'type': 'ir.actions.act_window',
            'name': 'Leases',
            'res_model': 'real_estate.lease',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {
                'default_property_id': self.id,
            },
        }

    def mark_as_occupied(self):
        """Mark property as no longer available"""
        for record in self:
            record.write({'available': False, 'price': record.price + 1000})
    
    def mark_as_available(self):
        """Mark property as available"""
        for record in self:
            record.write({'available': True})

    def update_description(self):
            """update the description of the property"""
            for record in self:
                record.write({"description": "mohamed"})

    def increase_deposit(self):
            """increase the deposit of the property"""
            for record in self:
                record.write({"deposit": record.deposit + 1000})

    def add_bedroom(self):
            """add a bedroom to the property"""
            for record in self:
                record.write({"bedrooms": record.bedrooms + 1})

    def make_property_as_villa(self):
        for record in self:
            if record.available:
                record.write({"property_type": "villa"})

    def get_agent_name(self):
        for record in self:
            if record.agent_id:
                record.write({"description": f"Agent Name: {record.agent_id.name}"})

    def write(self, vals):
         if not vals.get('available') and vals.get('bedrooms'):
            raise UserError("You cannot change the bedrooms until the property is available")
         return super(Property, self).write(vals)
