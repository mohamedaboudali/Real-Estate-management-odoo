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
    portal_access = fields.Boolean(compute='_compute_portal_access', string=' Portal Access')

    @api.depends('user_id')
    def _compute_portal_access(self):
        for record in self:
            record.portal_access = bool(record.user_id)
    
    def action_create_portal_user(self):
         """create a portal user linked to this tenant"""
         self.ensure_one()
         if self.user_id:
             raise ValidationError("This tenant already has a portal user.")
         if not self.email:
             raise ValidationError("Tenant must have an email to create a portal user.")

         existing_user = self.env['res.users'].sudo().search([('login', '=', self.email)], limit=1)
         if existing_user:
          self.user_id = existing_user
         else:
             portal_group = self.env.ref('base.group_portal')
             new_user = self.env['res.users'].sudo().create({
                'name': self.name,
                'login': self.email,
                'email': self.email,
                'phone': self.phone,
                'mobile': self.mobile,
                'groups_id': [(6, 0, [portal_group.id])],
            })
             self.user_id = new_user.id

        #  self.user_id.sudo().with_context(create_user=True).action_reset_password()

         return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Portal User Created',
                'message': f'Portal access granted to {self.name}.',
                'type': 'success',
                'sticky': False,
            }
        }
    
    
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


                    
        
    
    
