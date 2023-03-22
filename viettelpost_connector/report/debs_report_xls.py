from datetime import datetime
from typing import Dict, Any, Sequence, List, Tuple
from odoo import models, _
from odoo.exceptions import ValidationError, UserError


class DebsReportTemplateXls(models.AbstractModel):
    _name = 'report.viettelpost_connector.debs_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def _get_debs_report(self, lst_ids: tuple, date_from: str, date_to: str) -> List[Tuple]:
        query = f"""
            WITH GetTotalAmountPayment AS (
                SELECT RP.id,
                       EXTRACT(MONTH FROM AM.date) month_ap,
                       EXTRACT(YEAR FROM AM.date) year_ap,
                       COALESCE(SUM(AP.amount), 0) paid
                FROM res_partner RP
                LEFT JOIN account_payment AP ON RP.id = AP.partner_id
                JOIN account_move AM ON AM.id = AP.move_id
                WHERE RP.id IN {lst_ids}
                AND AM.date BETWEEN '{date_from}' AND '{date_to}'
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
                WHERE RP.id IN {lst_ids}
                AND SO.date_order BETWEEN '{date_from}' AND '{date_to}'
                AND SO.state IN ('sale', 'done')
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
            ORDER BY SO.name, date
        """
        self._cr.execute(query)
        query_res = self._cr.fetchall()
        return query_res

    @staticmethod
    def _get_name_to_report_xlsx(date_start: str, date_end: str) -> str:
        date_start = datetime.strptime(date_start, '%Y-%m-%d')
        date_end = datetime.strptime(date_end, '%Y-%m-%d')
        name = f'DS tổng hợp công nợ {date_start.year}+{date_end.year}' if date_start.year != date_end.year else f'DS tổng hợp công nợ {date_start.year}'
        return name

    def _get_data_debs_from_db(self, data: Dict[str, Any]) -> (List, str):
        if not data.get('lst_partner_ids'):
            raise ValidationError(_('The value of customers is required.'))
        elif not data.get('date_start'):
            raise ValidationError(_('The value of date start is required.'))
        elif not data.get('date_end'):
            raise ValidationError(_('The value of date end is required.'))
        lst_partner_ids: tuple = tuple(data.get('lst_partner_ids'))
        date_start: str = data.get('date_start')
        date_end: str = data.get('date_end')
        dict_empty, lst_debs = {'id': '', 'name': '', 'date': '', 'arise': '', 'paid': '', 'debs': ''}, []
        datas = self._get_debs_report(lst_partner_ids, date_start, date_end)
        for data in datas:
            dict_debs: dict = {k: v for k, v in zip(dict_empty.keys(), data)}
            lst_debs.append(dict_debs)
        name_xls = self._get_name_to_report_xlsx(date_start, date_end)
        return lst_debs, name_xls

    @staticmethod
    def _build_header_follow_result_month(sheet, header, lst_date, row, col):
        lst_cell: list = [chr(x) for x in range(ord('A'), ord('Z') + 1)]
        lst_cell_prefix: list = lst_cell[:]
        if (len(lst_date) * 3) > len(lst_cell):
            range_loop: int = len(lst_date) * 3 // len(lst_cell)
            for i, prefix in enumerate(lst_cell_prefix):
                if i == range_loop: break
                lst_cell_extend: list = [f'{prefix}{suffix}' for suffix in lst_cell_prefix[:]]
                lst_cell += lst_cell_extend
        count: int = 3
        for data in lst_date:
            cell: str = lst_cell[count:count + 3]
            main_cell: str = f'{cell[0]}:{cell[-1]}'
            sub_cell: str = f'{cell[0]}1:{cell[-1]}1'
            sheet.set_column(main_cell, 10, '')
            sheet.merge_range(sub_cell, data, header)
            sheet.write(row, col, 'Phát sinh', header)
            col += 1
            sheet.write(row, col, 'Đã trả', header)
            col += 1
            sheet.write(row, col, 'Còn lại', header)
            col += 1
            count += 3
        cell: str = lst_cell[count:count + 3]
        main_cell: str = f'{cell[0]}:{cell[-1]}'
        sub_cell: str = f'{cell[0]}1:{cell[-1]}1'
        sheet.set_column(main_cell, 10, '')
        sheet.merge_range(sub_cell, '', header)
        sheet.write(row, col, 'Phát sinh', header)
        col += 1
        sheet.write(row, col, 'Đã trả', header)
        col += 1
        sheet.write(row, col, 'Còn lại', header)
        return sheet

    @staticmethod
    def _build_header_customer(sheet, header, row: int, col: int):
        sheet.set_column('A:C', 15, '')
        sheet.merge_range('A1:C1', 'Khách hàng', header)
        sheet.write(row, col, 'Tên KH', header)
        col += 1
        sheet.write(row, col, 'Mã KH', header)
        col += 1
        sheet.write(row, col, 'KT công nợ', header)
        col += 1
        return sheet, col

    @staticmethod
    def _set_format_for_header(workbook):
        header = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#DDDBDB', 'font_size': 8, 'font_name': 'Tahoma'})
        return header

    @staticmethod
    def _set_format_for_row_cell(workbook):
        row_cell = workbook.add_format({'border': 1, 'bg_color': '#DDDBDB', 'font_size': 8, 'font_name': 'Tahoma'})
        return row_cell

    @staticmethod
    def _set_format_for_cell_and_sheet(workbook):
        last_cell = workbook.add_format({'bg_color': '#AAAAAA', 'border': 1, 'font_name': 'Tahoma'})
        return last_cell

    @staticmethod
    def _set_format_for_currency(workbook):
        currency = workbook.add_format({'num_format': '#,##0', 'bg_color': '#DDDBDB', 'border': 1, 'font_size': 8, 'font_name': 'Tahoma'})
        return currency

    def generate_xlsx_report(self, workbook, data, docs):
        lst_debs, name_xls = self._get_data_debs_from_db(data)
        header = self._set_format_for_header(workbook)
        row_cell = self._set_format_for_row_cell(workbook)
        last_cell = self._set_format_for_cell_and_sheet(workbook)
        currency = self._set_format_for_currency(workbook)
        sheet = workbook.add_worksheet(name_xls)
        col, row = 0, 1
        lst_date: list = []
        for deb in lst_debs:
            if deb['date'] not in lst_date:
                lst_date.append(deb['date'])
        sheet, col = self._build_header_customer(sheet, header, row, col)
        sheet = self._build_header_follow_result_month(sheet, header, lst_date, row, col)
        # names: list = list(sorted(set(deb['name'] for deb in lst_debs)))
        names = {}
        for deb in lst_debs:
            name = deb['name']
            if name in names:
                names[name] += 1
            else:
                names[name] = 1
        totals: dict = {}
        last_totals: dict = {'arise': 0, 'paid': 0, 'debs': 0}
        for name, count in names.items():
            last_name_cell = {'arise': 0, 'paid': 0, 'debs': 0}
            col: int = 0
            row += 1
            sheet.write(row, col, name, row_cell)
            col += 1
            sheet.write(row, col, '', row_cell)
            col += 1
            sheet.write(row, col, '', row_cell)
            col += 1
            for i, deb in enumerate(lst_debs):
                if deb['name'] == name:
                    sheet.write(row, col, deb['arise'], currency)
                    col += 1
                    sheet.write(row, col, deb['paid'], currency)
                    col += 1
                    sheet.write(row, col, deb['debs'], currency)
                    col += 1
                    if deb['date'] not in totals:
                        totals[deb['date']] = {'arise': 0, 'paid': 0, 'debs': 0}
                    totals[deb['date']]['arise'] += deb['arise']
                    totals[deb['date']]['paid'] += deb['paid']
                    totals[deb['date']]['debs'] += deb['debs']
                    last_name_cell['arise'] += deb['arise']
                    last_name_cell['paid'] += deb['paid']
                    last_name_cell['debs'] += deb['debs']
                if deb['name'] == name and i + 1 == count:
                    sheet.write(row, col, last_name_cell['arise'], currency)
                    col += 1
                    sheet.write(row, col, last_name_cell['paid'], currency)
                    col += 1
                    sheet.write(row, col, last_name_cell['debs'], currency)
                    col += 1
                    last_totals['arise'] += last_name_cell['arise']
                    last_totals['paid'] += last_name_cell['paid']
                    last_totals['debs'] += last_name_cell['debs']
                    lst_debs = [dct for dct in lst_debs if dct['name'] != name]
        row += 1
        col: int = 3
        sheet.merge_range(f'A{row+1}:C{row+1}', '', last_cell)
        for prices in totals.values():
            for price in prices.values():
                if price > 0:
                    sheet.write(row, col, price, currency)
                    col += 1
                else:
                    sheet.write(row, col, '', last_cell)
                    col += 1
        for price in last_totals.values():
            if price > 0:
                sheet.write(row, col, price, currency)
                col += 1
            else:
                sheet.write(row, col, '', last_cell)
                col += 1