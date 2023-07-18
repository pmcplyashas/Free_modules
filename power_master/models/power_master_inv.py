from odoo import api, fields, models, _


class InventoryMasterMoves(models.Model):
    _name = 'power.master.inv.moves'

    p_prd_name = fields.Char('Product')
    p_prd_type_id = fields.Char('Product Category')
    p_internal_ref_num = fields.Char('Internal reference No')
    p_unit_of_m = fields.Char('UOM')
    p_store_inv = fields.Char('From Location')
    p_store_inv_to = fields.Char('To location')
    p_batch_no = fields.Char('Lot No')
    p_opening = fields.Char('Opening')
    p_inward = fields.Float('Inward Qty')
    p_outward = fields.Float('Outward Qty')
    p_balance = fields.Char('Balance Qty')
    p_price_rate = fields.Float('Rate')
    p_rate_value = fields.Char('Stock Value')
    p_create_time = fields.Datetime('Stock Move Time')


class ToMoveStockEasy(models.Model):
    _inherit = 'stock.move.line'

    @api.constrains('state')
    def to_transfer_all_moves_to_master(self):

        for rec in self:
            if rec.state == 'done':

                # Purchase order moves
                if rec.picking_code == 'incoming':

                    to_get_bal_qty = self.env['product.product'].search([('name', '=', rec.product_id.name)])
                    if rec.lot_id:
                        # Qty before movement
                        spl_open_val = rec.lot_id.product_qty - rec.qty_done
                        # spl_open_val = to_get_bal_qty.qty_available - rec.qty_done

                        # Qty after movement
                        spl_close_bal = rec.lot_id.product_qty
                        # spl_close_bal = to_get_bal_qty.qty_available

                        inv_stock_val = spl_close_bal * rec.move_id.price_unit
                        # inv_stock_val = spl_close_bal * rec.product_id.standard_price
                    else:
                        # Qty before movement
                        spl_open_val = to_get_bal_qty.qty_available - rec.qty_done

                        # Qty after movement
                        spl_close_bal = to_get_bal_qty.qty_available

                        inv_stock_val = spl_close_bal * rec.move_id.price_unit
                        # inv_stock_val = spl_close_bal * rec.product_id.standard_price


                    self.env['power.master.inv.moves'].create({
                        'p_create_time': fields.datetime.now(),
                        'p_prd_name': rec.product_id.name,
                        'p_prd_type_id': rec.product_id.categ_id.name,
                        'p_internal_ref_num': rec.product_id.default_code,
                        'p_unit_of_m': rec.product_id.uom_id.name,
                        'p_store_inv': rec.location_id.name,
                        'p_store_inv_to': rec.location_dest_id.name,
                        'p_batch_no': rec.lot_id.name,
                        'p_opening': spl_open_val,
                        'p_inward': rec.qty_done,
                        'p_outward': 0,
                        'p_balance': spl_close_bal,
                        'p_price_rate': rec.product_id.standard_price,
                        'p_rate_value': inv_stock_val,
                    })

                # Sale order moves
                elif rec.picking_code == 'outgoing':

                    to_get_bal_qty = self.env['product.product'].search([('name', '=', rec.product_id.name)])

                    if rec.lot_id:

                        # Qty before movement
                        spl_open_val = rec.lot_id.product_qty + rec.qty_done
                        # spl_open_val = to_get_bal_qty.qty_available + rec.qty_done

                        # Qty after movement
                        spl_close_bal = rec.lot_id.product_qty
                        # spl_close_bal = to_get_bal_qty.qty_available

                        inv_stock_val = spl_close_bal * rec.move_id.price_unit
                        # inv_stock_val = spl_close_bal * rec.product_id.standard_price
                    else:
                        # Qty before movement
                        spl_open_val = to_get_bal_qty.qty_available + rec.qty_done

                        # Qty after movement
                        spl_close_bal = to_get_bal_qty.qty_available

                        inv_stock_val = spl_close_bal * rec.move_id.price_unit
                    self.env['power.master.inv.moves'].create({
                        'p_create_time': fields.datetime.now(),
                        'p_prd_name': rec.product_id.name,
                        'p_prd_type_id': rec.product_id.categ_id.name,
                        'p_internal_ref_num': rec.product_id.default_code,
                        'p_unit_of_m': rec.product_id.uom_id.name,
                        'p_store_inv': rec.location_id.name,
                        'p_store_inv_to': rec.location_dest_id.name,
                        'p_batch_no': rec.lot_id.name,
                        'p_opening': spl_open_val,
                        'p_inward': 0,
                        'p_outward': rec.qty_done,
                        'p_balance': spl_close_bal,
                        'p_price_rate': rec.product_id.standard_price,
                        'p_rate_value': inv_stock_val,
                    })

                # Internal Transfer
                elif rec.picking_code == 'internal':
                    if rec.lot_id:
                        bal_qty = rec.lot_id.product_qty - rec.qty_done
                        inv_stock_val = rec.lot_id.product_qty * rec.move_id.price_unit
                        # bal_qty = rec.product_id.qty_available - rec.qty_done
                        # inv_stock_val = rec.product_id.qty_available * rec.product_id.standard_price
                    else:
                        bal_qty = rec.product_id.qty_available - rec.qty_done
                        inv_stock_val = rec.product_id.qty_available * rec.move_id.price_unit

                    self.env['power.master.inv.moves'].create({
                        'p_create_time': fields.datetime.now(),
                        'p_prd_name': rec.product_id.name,
                        'p_prd_type_id': rec.product_id.categ_id.name,
                        'p_internal_ref_num': rec.product_id.default_code,
                        'p_unit_of_m': rec.product_id.uom_id.name,
                        'p_store_inv': rec.location_id.name,
                        'p_store_inv_to': rec.location_dest_id.name,
                        'p_batch_no': rec.lot_id.name,
                        'p_opening': rec.product_id.qty_available,
                        'p_inward': 0,
                        'p_outward': rec.qty_done,
                        'p_balance': bal_qty,
                        'p_price_rate': rec.product_id.standard_price,
                        'p_rate_value': inv_stock_val,
                    })

                # Internal transfer return
                elif rec.picking_code == 'internal_return':
                    if rec.lot_id:
                        inv_stock_val = rec.lot_id.product_qty * rec.move_id.price_unit
                        # inv_stock_val = rec.product_id.qty_available * rec.product_id.standard_price
                    else:
                        inv_stock_val = rec.product_id.qty_available * rec.move_id.price_unit

                    self.env['power.master.inv.moves'].create({
                        'p_create_time': fields.datetime.now(),
                        'p_prd_name': rec.product_id.name,
                        'p_prd_type_id': rec.product_id.categ_id.name,
                        'p_internal_ref_num': rec.product_id.default_code,
                        'p_unit_of_m': rec.product_id.uom_id.name,
                        'p_store_inv': rec.location_id.name,
                        'p_store_inv_to': rec.location_dest_id.name,
                        'p_batch_no': rec.lot_id.name,
                        'p_opening': rec.product_id.qty_available,
                        'p_inward': rec.qty_done,
                        'p_outward': 0,
                        'p_balance': rec.product_id.qty_available,
                        'p_price_rate': rec.product_id.standard_price,
                        'p_rate_value': inv_stock_val,
                    })

                # Return from customer
                elif rec.picking_code == 'customer_return':
                    if rec.lot_id:
                        bal_qty = rec.lot_id.product_qty + rec.qty_done
                        inv_stock_val = bal_qty * rec.move_id.price_unit
                        # bal_qty = rec.product_id.qty_available + rec.qty_done
                        # inv_stock_val = bal_qty * rec.product_id.standard_price
                    else:
                        bal_qty = rec.product_id.qty_available + rec.qty_done
                        inv_stock_val = bal_qty * rec.move_id.price_unit

                    self.env['power.master.inv.moves'].create({
                        'p_create_time': fields.datetime.now(),
                        'p_prd_name': rec.product_id.name,
                        'p_prd_type_id': rec.product_id.categ_id.name,
                        'p_internal_ref_num': rec.product_id.default_code,
                        'p_unit_of_m': rec.product_id.uom_id.name,
                        'p_store_inv': rec.location_id.name,
                        'p_store_inv_to': rec.location_dest_id.name,
                        'p_batch_no': rec.lot_id.name,
                        'p_opening': rec.product_id.qty_available,
                        'p_inward': rec.qty_done,
                        'p_outward': 0,
                        'p_balance': bal_qty,
                        'p_price_rate': rec.product_id.standard_price,
                        'p_rate_value': inv_stock_val,
                    })

                # Return to supplier
                elif rec.picking_code == 'supplier_return':
                    if rec.lot_id:
                        bal_qty = rec.lot_id.product_qty - rec.qty_done
                        inv_stock_val = bal_qty * rec.move_id.price_unit
                        # bal_qty = rec.product_id.qty_available - rec.qty_done
                        # inv_stock_val = bal_qty * rec.product_id.standard_price
                    else:
                        bal_qty = rec.product_id.qty_available - rec.qty_done
                        inv_stock_val = bal_qty * rec.move_id.price_unit
                    self.env['power.master.inv.moves'].create({
                        'p_create_time': fields.datetime.now(),
                        'p_prd_name': rec.product_id.name,
                        'p_prd_type_id': rec.product_id.categ_id.name,
                        'p_internal_ref_num': rec.product_id.default_code,
                        'p_unit_of_m': rec.product_id.uom_id.name,
                        'p_store_inv': rec.location_id.name,
                        'p_store_inv_to': rec.location_dest_id.name,
                        'p_batch_no': rec.lot_id.name,
                        'p_opening': rec.product_id.qty_available,
                        'p_inward': rec.qty_done,
                        'p_outward': 0,
                        'p_balance': bal_qty,
                        'p_price_rate': rec.product_id.standard_price,
                        'p_rate_value': inv_stock_val,
                    })

                # Manufacturing order moves
                else:
                    if rec.reference == 'Quantity Updated' or 'Product Quantity Updated':

                        to_get_bal_qty = self.env['product.product'].search([('name','=',rec.product_id.name)])
                        if rec.lot_id:
                            # Qty after movement
                            spl_bal_val = rec.lot_id.product_qty
                            # spl_bal_val = to_get_bal_qty.qty_available

                            # Qty before movement
                            spl_opening_bal = spl_bal_val - rec.qty_done
                            # spl_opening_bal = spl_bal_val - rec.qty_done

                            # opening_val = rec.qty_done

                            inward_hy = rec.qty_done

                            inv_stock_val = spl_bal_val * rec.move_id.price_unit
                            # inv_stock_val = spl_bal_val * rec.product_id.standard_price
                        else:
                            # Qty after movement
                            spl_bal_val = to_get_bal_qty.qty_available

                            # Qty before movement
                            spl_opening_bal = spl_bal_val - rec.qty_done

                            # opening_val = rec.qty_done

                            inward_hy = rec.qty_done

                            inv_stock_val = spl_bal_val * rec.move_id.price_unit

                        self.env['power.master.inv.moves'].create({
                            'p_create_time': fields.datetime.now(),
                            'p_prd_name': rec.product_id.name,
                            'p_prd_type_id': rec.product_id.categ_id.name,
                            'p_internal_ref_num': rec.product_id.default_code,
                            'p_unit_of_m': rec.product_id.uom_id.name,
                            'p_store_inv': rec.location_id.name,
                            'p_store_inv_to': rec.location_dest_id.name,
                            'p_batch_no': rec.lot_id.name,
                            'p_opening': spl_opening_bal,
                            'p_inward': inward_hy,
                            'p_outward': 0,
                            'p_balance': spl_bal_val,
                            'p_price_rate': rec.product_id.standard_price,
                            'p_rate_value': inv_stock_val,
                        })

                    else:

                        to_get_bal_qty = self.env['product.product'].search([('name', '=', rec.product_id.name)])
                        if rec.lot_id:
                            # Qty after movement
                            spl_val = rec.lot_id.product_qty
                            # spl_val = to_get_bal_qty.qty_available


                            # Qty before movement
                            spl_opening_bal = spl_val - rec.qty_done

                            # bal_qty = rec.product_id.qty_available + rec.qty_done
                            inv_stock_val = spl_val * rec.move_id.price_unit
                            # inv_stock_val = spl_val * rec.product_id.standard_price
                        else:
                            # Qty after movement
                            spl_val = to_get_bal_qty.qty_available

                            # Qty before movement
                            spl_opening_bal = spl_val - rec.qty_done

                            # bal_qty = rec.product_id.qty_available + rec.qty_done
                            inv_stock_val = spl_val * rec.move_id.price_unit

                        self.env['power.master.inv.moves'].create({
                            'p_create_time': fields.datetime.now(),
                            'p_prd_name': rec.product_id.name,
                            'p_prd_type_id': rec.product_id.categ_id.name,
                            'p_internal_ref_num': rec.product_id.default_code,
                            'p_unit_of_m': rec.product_id.uom_id.name,
                            'p_store_inv': rec.location_id.name,
                            'p_store_inv_to': rec.location_dest_id.name,
                            'p_batch_no': rec.lot_id.name,
                            'p_opening': spl_opening_bal,
                            'p_inward': rec.qty_done,
                            'p_outward': 0,
                            'p_balance': spl_val,
                            'p_price_rate': rec.product_id.standard_price,
                            'p_rate_value': inv_stock_val,
                        })















































