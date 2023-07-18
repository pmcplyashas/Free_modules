from odoo import api, fields, models, _
from datetime import datetime


class NewSubMasterReport(models.Model):
    _name = 'sub.master.report'

    sm_prd_name = fields.Char('Product')
    sm_prd_type_id = fields.Char('Product Category')
    sm_internal_ref_num = fields.Char('Internal reference No')
    sm_unit_of_m = fields.Char('UOM')
    sm_store_inv = fields.Char('From Location')
    sm_store_inv_to = fields.Char('To location')
    sm_batch_no = fields.Char('Stock Movement Lot No')
    sm_opening = fields.Char('Stock Opening')
    sm_inward = fields.Float('Inward Qty')
    sm_outward = fields.Float('Outward Qty')
    sm_balance = fields.Float('Balance Qty')
    sm_price_rate = fields.Float('Rate')
    sm_rate_value = fields.Char('Stock Value')
    sm_create_time = fields.Datetime('Stock Move Time')
    start_date_val = fields.Float('Stock Start Date')
    end_date_val = fields.Float('Stock End Date')
    hsn_code = fields.Char('Hsn Code')
    compute_vals = fields.Boolean(compute='start_n_end_vals')

    def start_n_end_vals(self):
        unique_product_list = []
        product_rec = []
        for rec in self:
            rec.compute_vals = False
            if rec.sm_prd_name not in unique_product_list:
                unique_product_list.append(rec.sm_prd_name)
            for j in unique_product_list:
                product_rec = self.search([('sm_prd_name', '=', j)])

                for k in product_rec:

                    if product_rec[0].id != k.id:
                        k.start_date_val = 0

                    if product_rec[-1].id != k.id:
                        k.end_date_val = 0


class InvBetweenDates(models.Model):
    _name = 'inv.between.dates'

    at_start_date = fields.Datetime('Start Date')
    at_close_date = fields.Datetime('Close Date')

    def dates_submit(self):
        older_records = self.env['sub.master.report'].search([])
        older_records.unlink()
        records = self.env['power.master.inv.moves'].search([
            ('p_create_time', '>=', self.at_start_date),
            ('p_create_time', '<=', self.at_close_date)
        ])

        groups = {}

        # Iterate over the records
        for record in records:
            product_name = record.p_prd_name

            # Check if the product name already exists as a key in the dictionary
            if product_name in groups:
                groups[product_name].append(record)
            else:
                groups[product_name] = [record]


        # Perform any necessary operations with the product groups
        for product_name, product_list in groups.items():
            # Print the product name and its associated records

            # To fetch the start stock value from early date(that is opening of that record)
            start_stock_val = product_list[0].p_opening

            # To fetch the end stock value from latest date(that is balance of that record)
            end_stock_val = product_list[-1].p_balance

        un_prod = []
        un_lot = []
        for i in records:
            if i.p_prd_name not in un_prod:
                un_prod.append(i.p_prd_name)
            if i.p_batch_no not in un_lot:
                un_lot.append(i.p_batch_no)
        unique_lot_list1 = []
        for j in un_prod:

            product_id = self.env['product.product'].search([('name', '=', j)])
            lot_list = self.env['stock.lot'].search(
                [('product_id', '=', product_id.id), ('create_date', '<', self.at_start_date),
                 ('product_qty', '>', 0)])
            for recs in lot_list:

                if recs.name not in unique_lot_list1 and recs.name not in un_lot:
                    # if recs.name not in unique_lot_list1:
                        # if recs.name not in unique_lot_list2:
                        unique_lot_list1.append(recs.name)
                        self.env['sub.master.report'].create({
                            'sm_create_time': recs.create_date,
                            'sm_prd_name': recs.product_id.name,
                            'sm_prd_type_id': recs.product_id.detailed_type,
                            'sm_internal_ref_num': recs.product_id.default_code,
                            'sm_unit_of_m': recs.product_id.uom_id.name,
                            'hsn_code': recs.product_id.l10n_in_hsn_code,
                            'sm_store_inv': False,
                            'sm_store_inv_to': False,
                            'sm_batch_no': recs.name,
                            'sm_opening': recs.product_qty,
                            'sm_inward': 0,
                            'sm_outward': 0,
                            'sm_balance': recs.product_qty,
                            'sm_price_rate': 0,
                            'sm_rate_value': 0,
                            'start_date_val': recs.product_qty,
                            # 'start_date_val':start_stock_val,
                            'end_date_val': 0
                            # 'end_date_val':end_stock_val
                        })

        for rec in records:
            if rec.p_inward:
                single_product_list = []
                unique_lot_list = []
                # unique_lot_list1 = []
                unique_lot_list2 = []
                open_bln = 0
                close_bln = 0
                for rec1 in records:
                    if rec1.p_prd_name == rec.p_prd_name:
                        # filter in one list and then put index of 1 and -1 and take start and end value
                        single_product_list.append(
                            rec1)  # has single products all records so through indexing fetching open and close qty
                        unique_lot_list2.append(rec1.p_batch_no)
                for rec2 in single_product_list:
                    if rec2.p_batch_no and rec2.p_batch_no not in unique_lot_list:
                        lot_id = rec.env['stock.lot'].search([('name', '=', rec2.p_batch_no), ('create_date', '>=', self.at_start_date), ('create_date', '<=', self.at_close_date)])
                        if lot_id:
                            rec.p_opening = 0
                            open_bln = 0
                            rec.p_balance = rec2.p_inward
                            unique_lot_list.append(rec2.p_batch_no)
                        else:
                            open_bln = single_product_list[0].p_opening
                            close_bln = single_product_list[-1].p_balance
                product_id = self.env['product.product'].search([('name', '=', single_product_list[0].p_prd_name)])


                self.env['sub.master.report'].create({
                    'sm_create_time': rec.p_create_time,
                    'sm_prd_name': rec.p_prd_name,
                    'sm_prd_type_id': rec.p_prd_type_id,
                    'sm_internal_ref_num': rec.p_internal_ref_num,
                    'sm_unit_of_m': rec.p_unit_of_m,
                    'sm_store_inv': rec.p_store_inv,
                    'sm_store_inv_to': rec.p_store_inv_to,
                    'sm_batch_no': rec.p_batch_no,
                    'sm_opening': rec.p_opening,
                    'sm_inward': rec.p_inward,
                    'sm_outward': 0,
                    'sm_balance': rec.p_balance,
                    'sm_price_rate': rec.p_price_rate,
                    'sm_rate_value': rec.p_rate_value,
                    'start_date_val': open_bln,
                    'hsn_code': product_id.l10n_in_hsn_code,
                    # 'start_date_val':start_stock_val,
                    'end_date_val': close_bln
                    # 'end_date_val':end_stock_val
                })
            else:
                single_product_list = []
                unique_lot_list = []
                unique_lot_list1 = []
                open_bln = 0
                close_bln = 0
                for rec1 in records:
                    if rec1.p_prd_name == rec.p_prd_name:
                        # filter in one list and then put index of 1 and -1 and take start and end value
                        single_product_list.append(
                            rec1)  # has single products all records so through indexing fetching open and close qty

                open_bln = single_product_list[0].p_opening
                close_bln = single_product_list[-1].p_balance
                product_id = self.env['product.product'].search([('name', '=', single_product_list[0].p_prd_name)])

                self.env['sub.master.report'].create({
                    'sm_create_time': rec.p_create_time,
                    'sm_prd_name': rec.p_prd_name,
                    'sm_prd_type_id': rec.p_prd_type_id,
                    'sm_internal_ref_num': rec.p_internal_ref_num,
                    'sm_unit_of_m': rec.p_unit_of_m,
                    'sm_store_inv': rec.p_store_inv,
                    'sm_store_inv_to': rec.p_store_inv_to,
                    'sm_batch_no': rec.p_batch_no,
                    'sm_opening': rec.p_opening,
                    'sm_inward': 0,
                    'sm_outward': rec.p_outward,
                    'sm_balance': rec.p_balance,
                    'sm_price_rate': rec.p_price_rate,
                    'sm_rate_value': rec.p_rate_value,
                    'start_date_val': open_bln,
                    'end_date_val': close_bln,
                    'hsn_code': product_id.l10n_in_hsn_code,
                })









