import logging
import random
from datetime import timedelta

from odoo import Command, api, fields, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_valid_user_picking_type_pairs(self, users, picking_types):
        user_allowed_companies = {u.id: set(u.company_ids.ids) for u in users}
        valid_pairs = []

        for user in users:
            for picking_type in picking_types:
                target_company_id = picking_type.company_id.id

                # Tránh vi phạm record rule: Stock Operation Type multi-company
                if target_company_id and target_company_id not in user_allowed_companies[user.id]:
                    continue

                valid_pairs.append((user, picking_type))

        return valid_pairs

    @api.model
    def simulate_create_picking(self, record_count=100):
        """
        Sử dụng tích Đề-các kết hợp ánh xạ thời gian.
        Không lưu trữ trạng thái và không materialize toàn bộ tổ hợp.
        """
        now = fields.Datetime.now()
        
        # 1. Kéo dữ liệu từ Database ra ngoài vòng lặp
        stock_user_group = self.env.ref('stock.group_stock_user')
        users = self.env['res.users'].search([
            ('id', '>', 1),
            ('share', '=', False),
            ('active', '=', True),
            ('all_group_ids', 'in', stock_user_group.id),
        ])
        picking_types = self.env['stock.picking.type'].search([])
        partners = self.env['res.partner'].search([])
        products = self.env['product.product'].search([])

        valid_user_picking_type_pairs = self._get_valid_user_picking_type_pairs(
            users,
            picking_types,
        )
        total_combinations = (
            len(valid_user_picking_type_pairs) * len(partners) * len(products)
        )

        _logger.info(
            '[SIMULATE CREATE PICKING] Cartesian product size=%s '
            '(users=%s, picking_types=%s, partners=%s, products=%s)',
            total_combinations,
            len(users),
            len(picking_types),
            len(partners),
            len(products),
        )

        # 2. XÁC ĐỊNH VỊ TRÍ TỔ HỢP DỰA VÀO THỜI GIAN
        # Lấy ngày thứ mấy trong năm (ví dụ ngày 1 tháng 2 là ngày thứ 32)
        day_of_year = now.timetuple().tm_yday
        # Tính tổng số phút tính từ ngày 1 tháng 1
        total_minutes = ((day_of_year - 1) * 24 * 60) + (now.hour * 60) + now.minute

        # Nhân tổng số phút với record_count để đảm bảo các lần chạy liên tiếp không bị đè lên nhau
        start_index = (total_minutes * record_count) % total_combinations

        # _logger.info(
        #     '[SIMULATE CREATE PICKING] Batch start_index=%s, record_count=%s',
        #     start_index,
        #     record_count,
        # )
        
        created_picking_ids = []
        
        # 3. Tiến hành chạy theo Batch (record_count)
        for i in range(record_count):
            # Tịnh tiến index và tự động reset về 0 (xoay vòng) nếu vượt quá tổng số tổ hợp
            current_index = (start_index + i) % total_combinations

            pair_index, remainder = divmod(
                current_index,
                len(partners) * len(products),
            )
            partner_index, product_index = divmod(remainder, len(products))

            selected_user, selected_picking_type = valid_user_picking_type_pairs[pair_index]
            selected_partner = partners[partner_index]
            selected_product = products[product_index]

            _logger.info(
                '[SIMULATE CREATE PICKING] Combination index=%s: '
                'user_id=%s, picking_type_id=%s, partner_id=%s, product_id=%s',
                current_index,
                selected_user.id,
                selected_picking_type.id,
                selected_partner.id,
                selected_product.id,
            )

            demand_qty = random.randint(5, 50)
            
            # Random một phần số lượng hoàn thành
            is_partial = random.choice([True, False])
            done_qty = max(0, demand_qty - random.randint(1, 5)) if is_partial else demand_qty
            
            move_commands = [Command.create({
                'description_picking': f"Chi tiết giả lập: {selected_product.name}",
                'product_id': selected_product.id,
                'product_uom_qty': demand_qty,
                'quantity': done_qty,
                'product_uom': selected_product.uom_id.id,
            })]
            
            days_offset = random.randint(1, 5)
            salt = random.randint(1, 10000)
            
            # Mã phiếu có đính kèm current_index để bạn có thể kiểm tra xem nó đang ở tổ hợp thứ mấy
            origin_str = f'SIM-MANUAL-{now.strftime("%Y%m%d%H%M%S")}-{salt}-IDX{current_index}'
            
            # 4. Thực hiện Tạo Phiếu Kho
            picking = self.env['stock.picking'].with_user(selected_user).with_company(selected_picking_type.company_id).create({
                'picking_type_id': selected_picking_type.id,
                'origin': origin_str,
                'partner_id': selected_partner.id,
                'scheduled_date': now + timedelta(days=days_offset),
                'date_deadline': now + timedelta(days=days_offset + random.randint(1, 3)),
                'move_ids': move_commands,
            })
            
            created_picking_ids.append(picking.id)
            
        if record_count == 1 and created_picking_ids:
            return created_picking_ids[0]

        return created_picking_ids
