from odoo import http
from odoo.http import request
from werkzeug.urls import url_quote
from odoo.addons.portal.controllers.portal import CustomerPortal

class RealEstatePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(RealEstatePortal, self)._prepare_portal_layout_values()
        maintenance = request.env['real_estate.maintenance'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        maintenance_count = 0
        if maintenance:
            maintenance_count = request.env['real_estate.maintenance'].sudo().search_count([
                ('user_id', '=', request.env.user.id)
            ])
        values.update({
            'maintenance_count': maintenance_count,
        })
        return values

    @http.route(['/my/maintenance', '/my/maintenance/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_maintenance(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        maintenance = values.get('maintenance_count')
        if not maintenance:
            values.update({
                'maintenance': request.env['real_estate.maintenance'].sudo().browse(),
            })
            return request.render('real_estate.portal_my_maintenance', values)

        maintenance_records = request.env['real_estate.maintenance'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], order='create_date desc')
        values.update({
            'maintenance': maintenance_records,
        })
        return request.render('real_estate.portal_my_maintenance', values)