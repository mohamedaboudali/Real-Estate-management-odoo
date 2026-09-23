from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True) 
    crm_id = fields.Many2one('crm.lead', string='CRM Lead')
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    age = fields.Integer(string='age', compute='_compute_age', store=True)
    lease_ids = fields.One2many('real_estate.lease', 'tenant_id', string='Leases') 
    age_category = fields.Selection([('a', '1:20'),('b', '21:40'),('c', '41:60'),], string='Age Category')

    def update_notes(self):
        """Update the notes of the tenant"""
        for record in self:
            record.write({"notes":record.name})

    def get_crm_lead_email(self):
        for record in self:
            if record.crm_id.email_from:
                record.write({'notes': record.crm_id.email_from})
            else:
                record.write({'notes': record.crm_id.website})

    @api.depends('date_of_birth')
    def _compute_age(self):
        """Calculate tenant age"""
        today = fields.Date.today()
        for record in self:
            dob = fields.Date.from_string(record.date_of_birth)
            if record.date_of_birth:
                    record.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                    record.age = 0

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):                 
        """Ensure date of birth is not in the future"""
        today = fields.Date.today()
        for record in self:
            if record.date_of_birth and record.date_of_birth > today:
                raise ValidationError("Date of Birth cannot be in the future.")

    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Email must be unique! This email is already registered.'),
    ]
                    
        
    
    
