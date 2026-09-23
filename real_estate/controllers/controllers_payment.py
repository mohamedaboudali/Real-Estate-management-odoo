from odoo import http
from odoo.http import request
from werkzeug.urls import url_quote
from odoo.addons.portal.controllers.portal import CustomerPortal

class RealEstatePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(RealEstatePortal, self)._prepare_portal_layout_values()
        payment = request.env['real_estate.payment'].sudo().search([
            ('tenant_id.user_id', '=', request.env.user.id)
        ], limit=1)
        payment_count = 0
        if payment:
            payment_count = request.env['real_estate.payment'].sudo().search_count([
                ('tenant_id.user_id', '=', request.env.user.id)
            ])
        values.update({
            'payment_count': payment_count,
        })
        return values

    @http.route(['/my/payment', '/my/payment/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_payment(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        payment = values.get('payment_count')
        if not payment:
            values.update({
                'payment': request.env['real_estate.payment'].sudo().browse(),
            })
            return request.render('real_estate.portal_my_payment', values)

        payment_records = request.env['real_estate.payment'].sudo().search([
            ('tenant_id.user_id', '=', request.env.user.id)
        ], order='create_date desc')
        values.update({
            'payment': payment_records,
        })
        return request.render('real_estate.portal_my_payment', values)