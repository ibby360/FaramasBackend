import json
from odoo import http
from odoo.http import request, Response

class EmailVerificationController(http.Controller):

    @http.route('/verify_email/<string:token>', type='http', auth='public', website=True)
    def verify_email(self, token):
        user = request.env['res.users'].sudo().search([('email_token', '=', token)], limit=1)
        if not user:
            return request.render('website.404')

        user.email_verified = True
        user.email_token = False  # Invalidate token

        # return request.render('estate.email_verified_success', {
        #     'user': user,
        # })