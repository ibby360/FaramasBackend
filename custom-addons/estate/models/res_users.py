import secrets
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessDenied
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError


from .helpers import format_response


class ResUsers(models.Model):
    _inherit = 'res.users'

    login_number = fields.Char(string='Phone Number', help="User's phone number")
    email_verified = fields.Boolean(default=False, string="Email Verified")
    email_token = fields.Char(string="Email Verification Token")

    def generate_email_token(self):
        for user in self:
            user.email_token = secrets.token_urlsafe(32)

    def send_verification_email(self):
        for user in self:
            user.generate_email_token()
            template = self.env.ref('estate.email_verification_template')
            template.send_mail(user.id, force_send=True)

    @api.model
    def register_user(self, vals):
        try:
            name = vals.get('name')
            email = vals.get('email')
            password = vals.get('password')
            confirm_password = vals.get('confirm_password')
            phone_number = vals.get('phone_number')

            if not name:
                raise UserError(_("Name is required."))
            if not email:
                raise UserError(_("Email is required."))
            if not password:
                raise UserError(_("Password is required."))
            if not confirm_password:
                raise UserError(_("Confirm password is required."))
            if password != confirm_password:
                raise UserError(_("Passwords do not match."))

            # Check if user already exists
            existing_user = self.sudo().search([('login', '=', email)], limit=1)
            if existing_user:
                raise UserError(_("User already exists with this email address."))

            # Prepare signup values as Odoo expects
            signup_vals = {
                'name': name,
                'login': email,
                'email': email,
                'password': password,
                'login_number': phone_number,
            }

            try:
                # Use Odoo's built-in signup logic
                self.sudo()._signup_create_user(signup_vals)
            except (UserError, SignupError, AssertionError) as e:
                raise UserError(_("Could not create a new account"))

            # Fetch the newly created user
            user = self.sudo().search([('login', '=', email)], order=self._get_login_order(), limit=1)

            # Send account creation confirmation email
            # email = self.send_verification_email()
            template = self.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
            if user and template:
                template.sudo().send_mail(user.id, force_send=True)

            # Assign to base group if not already
            # Remove user from other user type groups before assigning 'base.group_user'
            user_type_groups = [
                self.env.ref('base.group_user').id,
                self.env.ref('base.group_portal').id,
                self.env.ref('base.group_public').id,
            ]
            user.sudo().write({'groups_id': [(3, gid) for gid in user_type_groups]})
            user.sudo().write({'groups_id': [(4, self.env.ref('base.group_user').id)]})

            data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone_number': user.login_number,
            }
            return format_response(200, "User registered successfully", data)
        except UserError as e:
            return format_response(400, str(e), None)
        
        except Exception as e:
            return format_response(500, f'An unexpected error occurred: {str(e)}', None)
    
    @api.model
    def user_login(self, vals):
        """
        Authenticates a user by email or phone and verifies the password.

        :param identifier: email or phone number
        :param password: plain text password
        :return: user record or raise exception
        """
        try:
            User = self.env['res.users'].sudo()

            identifier = vals.get('identifier')
            password = vals.get('password')

            if not identifier:
                raise AccessDenied(_('Email or phone number is required.'))
            if not password:
                raise AccessDenied(_('Password is required.'))

            # Try to find user by email first, then by phone
            user = User.search([('login', '=', identifier)], limit=1)
            if not user:
                user = User.search([('login_number', '=', identifier)], limit=1)

            if not user:
                raise AccessDenied(_('Invalid credentials.'))

            # Ensure the identifier matches the correct field for this user
            if identifier != user.login and identifier != user.login_number:
                raise AccessDenied(_('Identifier does not match this user.'))

            # Check password for this user only
            try:
                user._check_credentials(password, {'interactive': False})
            except Exception:
                raise AccessDenied(_('Invalid credentials.'))

            data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.login_number,
            }
            return format_response('Success', "Login successful", data)
        
        except AccessDenied as e:
            return format_response('Error', str(e), None)
        except UserError as e:
            return format_response('Error', str(e), None)
        except Exception as e:
            return format_response('Error', f'An unexpected error occurred: {str(e)}', None)