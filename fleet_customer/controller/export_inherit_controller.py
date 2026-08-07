from odoo.addons.web.controllers.export import CSVExport
from odoo.http import request
import json
import operator

class CSVExportSudo(CSVExport):
    def base(self, data):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = operator.itemgetter(
            'model',
            'fields',
            'ids',
            'domain',
            'import_compat'
        )(params)
        Model = request.env[model].sudo().with_context(
            import_compat=import_compat,
            **params.get('context', {})
        )
        if not Model._is_an_ordinary_table():
            fields = [field for field in fields if field['name'] != 'id']
        field_names = [f['name'] for f in fields]
        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]
        records = Model.browse(ids) if ids else Model.search(domain)
        export_data = records.export_data(field_names).get('datas', [])
        response_data = self.from_data(
            fields,
            columns_headers,
            export_data
        )
        return request.make_response(
            response_data,
            headers=[
                (
                    'Content-Disposition',
                    'attachment; filename="export.csv"'
                ),
                (
                    'Content-Type',
                    self.content_type
                )
            ],
        )