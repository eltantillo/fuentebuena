from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.export import Export, CSVExport, ExcelExport


class ExportSudo(Export):

    @http.route()
    def get_fields(self, model, domain, prefix='', parent_name='',import_compat=True, parent_field_type=None,parent_field=None, exclude=None):
        request.env = request.env(su=True)
        return super().get_fields(
            model, domain,
            prefix=prefix, parent_name=parent_name,
            import_compat=import_compat,
            parent_field_type=parent_field_type,
            parent_field=parent_field,
            exclude=exclude,
        )

    @http.route()
    def namelist(self, model, export_id):
        request.env = request.env(su=True)
        return super().namelist(model, export_id)


class CSVExportSudo(CSVExport):

    @http.route()
    def web_export_csv(self, data):
        request.env = request.env(su=True)
        return super().web_export_csv(data)


class ExcelExportSudo(ExcelExport):

    @http.route()
    def web_export_xlsx(self, data):
        request.env = request.env(su=True)
        return super().web_export_xlsx(data)