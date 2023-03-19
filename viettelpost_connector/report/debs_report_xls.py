from odoo import models


class DebsReportTemplateXls(models.AbstractModel):
    _name = 'report.viettelpost_connector.debs_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def _get_debs_report(self, date_from, date_to, lst_ids):
        query = f"""
            WITH GetTotalAmountPayment AS (
                SELECT RP.id,
                       EXTRACT(MONTH FROM AM.date) month_ap,
                       EXTRACT(YEAR FROM AM.date) year_ap,
                       COALESCE(SUM(AP.amount), 0) paid
                FROM res_partner RP
                LEFT JOIN account_payment AP ON RP.id = AP.partner_id
                JOIN account_move AM ON AM.id = AP.move_id
                WHERE RP.id IN (SELECT UNNEST(ARRAY{lst_ids})
                AND AM.date BETWEEN {date_from} AND {date_to}
                AND AM.state = 'posted'
                AND AP.payment_type = 'inbound'
                GROUP BY RP.id, RP.name, month_ap, year_ap
                ORDER BY RP.id
            ),
            GetTotalAmountSaleOrder AS (
                SELECT RP.id, 
                       RP.name,
                       EXTRACT(MONTH FROM SO.date_order) month_so,
                       EXTRACT(YEAR FROM SO.date_order) year_so,
                       SUM(SO.money_total) arise
                 FROM res_partner RP
                 LEFT JOIN sale_order SO ON RP.id = SO.partner_id
                 WHERE RP.id IN (SELECT UNNEST(ARRAY{lst_ids})
                 AND SO.date_order BETWEEN {date_from} AND {date_to}
                 AND SO.state = 'sale'
                 GROUP BY RP.id, RP.name, month_so, year_so
                 ORDER BY RP.id
            )
            SELECT SO.id, 
                   SO.name,
                   CONCAT(SO.month_so, '/', SO.year_so) date,
                   COALESCE(SO.arise, 0) arise,
                   COALESCE(AP.paid, 0) paid,
                   COALESCE(arise - paid, 0) debs
                 FROM GetTotalAmountSaleOrder SO
                 LEFT JOIN GetTotalAmountPayment AP ON SO.id = AP.id
                 AND AP.month_ap = SO.month_so
                 AND AP.year_ap = SO.year_so
        """
        self._cr.execute(query)
        query_res = self._cr.fetchall()
        return query_res

    # def generate_xlsx_report(self, workbook, data, docs):
