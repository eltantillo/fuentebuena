from odoo import fields,models,_
# from odoo.addons.account.models.exceptions import TaxClosingNonPostedDependingMovesError
#
# class FacturaAccountValidate(models.TransientModel):
#     _inherit = 'validate.account.move'
#     _description = 'Herencia para modificar el compotamiento de la confirmación global de facturas'
#
#     def validate_move(self):
#         if self.ignore_abnormal_amount:
#             self.abnormal_amount_partner_ids.ignore_abnormal_invoice_amount = True
#         if self.ignore_abnormal_date:
#             self.abnormal_date_partner_ids.ignore_abnormal_invoice_date = True
#         if self.force_post:
#             self.move_ids.auto_post = 'no'
#         try:
#             self.move_ids.validar_multiples()
#         except TaxClosingNonPostedDependingMovesError as exception:
#             return {
#                 "type": "ir.actions.client",
#                 "tag": "account_reports.redirect_action",
#                 "target": "new",
#                 "name": "Depending Action",
#                 "params": {
#                     "depending_action": exception.args[0],
#                     "message": _("It seems there is some depending closing move to be posted"),
#                     "button_text": _("Depending moves"),
#                 },
#                 'context': {
#                     'dialog_size': 'medium',
#                 },
#             }
#         if autopost_bills_wizard := self.move_ids._show_autopost_bills_wizard():
#             return autopost_bills_wizard
#         return {'type': 'ir.actions.act_window_close'}
