from odoo import models, fields, api

class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True)    
    bedrooms = fields.Integer(string='Bedrooms', required=True)
    available = fields.Boolean(string='Available', default=True, index=True)   
    agent_id = fields.Many2one('res.users', string='Agent')

    property_type = fields.Selection([
            ('apartment', 'Apartment'),
            ('house', 'House'),
            ('villa', 'Villa'),
            ('commercial', 'Commercial'),
        ], string='Property Type', required=True)

    deposit = fields.Float(string='Deposit')

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
   

                 
                