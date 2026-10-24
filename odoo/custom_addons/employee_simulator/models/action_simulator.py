from odoo import models, api, fields
from odoo.exceptions import UserError
import random
import logging
from datetime import timedelta
from itertools import product
from odoo import Command
import string

_logger = logging.getLogger(__name__)

class EmployeeSimulator(models.AbstractModel):
    # Trả lại AbstractModel như thiết kế ban đầu (không tạo bảng)
    _name = 'employee.simulator'
    _description = 'Employee Action Simulator'

    @api.model
    def _get_valid_combinations(self, users, picking_types, partners, products):
        
        user_allowed_companies = {u.id: set(u.company_ids.ids) for u in users}
        pt_company = {pt.id: pt.company_id.id for pt in picking_types}
        
        valid_combinations = []
        
        for user, p_type, partner, product_rec in product(users, picking_types, partners, products):
            u_id, pt_id = user.id, p_type.id
            target_company_id = pt_company.get(pt_id)
            
            # Tránh vi phạm record rule: Stock Operation Type multi-company
            if target_company_id and target_company_id not in user_allowed_companies[u_id]:
                continue
                
            valid_combinations.append((user, p_type, partner, product_rec))
            
        return valid_combinations

    @api.model
    def simulate_create_picking(self, record_count=100):
        """
        Nâng cấp: Sử dụng tích Đề-các (Cartesian Product) kết hợp ánh xạ thời gian (Time-based Indexing).
        Không lưu trữ trạng thái. Tự động xác định vùng tổ hợp cần chạy dựa vào thời gian thực thi của Cron.
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

        # Materialize tích Đề-các để có thể lưu và lọc từng bộ dữ liệu.
        all_combinations = self._get_valid_combinations(
            users,
            picking_types,
            partners,
            products,
        )
        total_combinations = len(all_combinations)

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
        total_minutes = (day_of_year * 24 * 60) + (now.hour * 60) + now.minute

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

            (
                selected_user,
                selected_picking_type,
                selected_partner,
                selected_product,
            ) = all_combinations[current_index]

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

    @api.model
    def cron_simulate_internal_transfer_create(self):
        """Create one draft internal transfer without reserving stock."""
        now = fields.Datetime.now()
        stock_user_group = self.env.ref('stock.group_stock_user')

        users = self.env['res.users'].search([
            ('id', '>', 1),
            ('share', '=', False),
            ('active', '=', True),
            ('all_group_ids', 'in', stock_user_group.id),
        ])

        eligible_contexts = []
        for user in users:
            for company in user.company_ids:
                picking_types = self.env['stock.picking.type'].search([
                    ('code', '=', 'internal'),
                    ('company_id', 'in', [False, company.id]),
                ])
                locations = self.env['stock.location'].search([
                    ('usage', '=', 'internal'),
                    ('active', '=', True),
                    ('company_id', 'in', [False, company.id]),
                ])
                products = self.env['product.product'].search([
                    ('active', '=', True),
                    ('is_storable', '=', True),
                    ('company_id', 'in', [False, company.id]),
                ])
                if picking_types and len(locations) >= 2 and products:
                    eligible_contexts.append(
                        (user, company, picking_types, locations, products)
                    )

        user, company, picking_types, locations, products = random.choice(
            eligible_contexts
        )
        picking_type = random.choice(picking_types)
        source_location = random.choice(locations)
        destination_location = random.choice(
            locations.filtered(lambda location: location != source_location)
        )
        product = random.choice(products)
        demand_qty = random.randint(5, 45)
        salt = random.randint(1, 10000)
        origin = f'SIM-INT-{now.strftime("%Y%m%d%H%M%S")}-{salt}'

        picking = self.env['stock.picking'].with_user(user).with_company(
            company
        ).create({
            'picking_type_id': picking_type.id,
            'company_id': company.id,
            'origin': origin,
            'location_id': source_location.id,
            'location_dest_id': destination_location.id,
            'scheduled_date': now + timedelta(days=random.randint(1, 5)),
            'move_ids': [Command.create({
                'description_picking': f'Chi tiết giả lập: {product.name}',
                'product_id': product.id,
                'product_uom_qty': demand_qty,
                'product_uom': product.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': destination_location.id,
            })],
        })
        return picking.id

    @api.model
    def simulate_confirm_picking(self, picking_type_code=False):
        """
        Cron 2: Giả lập nhân viên thao tác Xác nhận (Confirm) các phiếu kho đang Nháp.
        Hàm dùng chung, có thể nhận các tham số filter để lọc domain.
        """
        domain = [('state', '=', 'draft')]
        
        if picking_type_code:
            domain.append(('picking_type_id.code', '=', picking_type_code))
        pickings = self.env['stock.picking'].search(domain, limit=20)
        
        # Lấy group quyền nhân viên kho
        stock_user_group = self.env.ref('stock.group_stock_user')

        for picking in pickings:
            valid_users = self.env['res.users'].search([
                ('id', '>', 1),
                ('share', '=', False),
                ('active', '=', True),
                ('all_group_ids', 'in', stock_user_group.id),
                ('company_ids', 'in', picking.company_id.id)
            ])
            
            # Chọn user hợp lệ, nếu không có ai thì dùng fallback là user đang chạy cron (thường là Admin)
            random_user = random.choice(valid_users)

            # Gắn context theo user và company hợp lý để vượt qua mọi check quyền của Odoo
            simulated_picking = picking.with_user(random_user.id)
            simulated_picking.action_confirm()

    @api.model
    def cron_simulate_picking_unreserve(self):
        """
        [CRON] Giả lập nhân viên: Unreserve (Bỏ giữ hàng).
        
        Mục đích: 
        - Giả lập hành động của nhân viên kho khi tìm kiếm các phiếu kho (stock.picking)
        đang ở trạng thái giữ hàng (assigned) nhưng cần giải phóng hàng hóa.
        - Gọi thao tác unreserve trên các phiếu kho đó để trả tồn kho về trạng thái khả dụng.
        """
        # TODO: Define test cases and implement logic
        pass

    @api.model
    def cron_simulate_picking_lock_unlock(self):
        """
        [CRON] Giả lập nhân viên quản lý: Lock/Unlock (Khóa / Mở khóa).
        
        Mục đích: 
        - Giả lập thao tác của quản lý kho đi kiểm tra lại các phiếu kho đã hoàn thành (done).
        - Thực hiện Lock các phiếu để chốt sổ, hoặc Unlock các phiếu cần điều chỉnh 
        sai lệch số lượng thực tế.
        """
        # TODO: Define test cases and implement logic
        pass

    @api.model
    def cron_simulate_picking_scrap(self):
        """
        [CRON] Giả lập nhân viên: Scrap (Báo phế liệu).
        
        Mục đích: 
        - Giả lập kịch bản nhân viên đang xử lý phiếu kho thì phát hiện hàng hỏng/rách bao bì.
        - Tự động lấy ngẫu nhiên (hoặc theo quy tắc) một số lượng hàng hóa trên phiếu 
        để tạo action Scrap, đẩy hàng lỗi sang địa điểm phế liệu (Scrap Location).
        """
        # TODO: Define test cases and implement logic
        pass
        
    @api.model
    def cron_simulate_picking_split(self):
        """
        [CRON] Giả lập nhân viên: Split (Tách phiếu / Tách dòng).
        
        Mục đích: 
        - Giả lập hành động chia tách (Split) của nhân viên kho.
        - Có thể là kịch bản nhận hàng thiếu phải tạo Backorder (tách phiếu), 
        hoặc thao tác bóc 1 dòng hàng hóa lớn thành nhiều dòng nhỏ mang số Lot/Serial khác nhau.
        """
        # TODO: Define test cases and implement logic
        pass

    @api.model
    def cron_simulate_picking_assign(self, picking_type_id=False):
        """
        [CRON] Giả lập nhân viên: Check Availability (Kiểm tra khả dụng).
        
        Mục đích: 
        - Giả lập việc nhân viên kho bấm nút 'Kiểm tra khả dụng' để giữ hàng (Reserve).
        - Khi nhấn nút này, hệ thống sẽ gọi action_assign().
        - Điều kiện bắt buộc (Test Case target): Các phiếu kho phải đang ở trạng thái 'Chờ xử lý' (confirmed).
        """
        now = fields.Datetime.now()
        minute = now.minute
        hour = now.hour
        day = now.day

        # Chỉ giả lập bằng user kho đang hoạt động.
        stock_user_group = self.env.ref('stock.group_stock_user')
        users = self.env['res.users'].search([
            ('id', '>', 1),
            ('active', '=', True),
            ('share', '=', False),
            ('all_group_ids', 'in', stock_user_group.id),
        ])
        
        domain = [('state', 'in', ['confirmed', 'waiting'])]
        if isinstance(picking_type_id, (list, tuple)):
            domain.append(('picking_type_id', 'in', picking_type_id))
        elif picking_type_id:
            domain.append(('picking_type_id', '=', picking_type_id))
            
        pickings = self.env['stock.picking'].search(domain)

        # Tạo một salt ngẫu nhiên
        salt = random.randint(1, 10000)

        # Thay vì dùng limit cứng, ta xác định số lượng record cần chạy ngẫu nhiên dựa vào thời gian (ví dụ từ 1 đến 3 phiếu)
        record_count = (minute + hour + salt) % 3 + 1
        record_count = min(record_count, len(pickings))
        
        for i in range(record_count):
            current_salt = salt + i
            
            # 1. Chọn picking ngẫu nhiên dựa vào thuật toán trước
            selected_picking = pickings[(minute * 7 + hour * 17 + day * 23 + current_salt) % len(pickings)]
            pickings -= selected_picking
            
            # 2. Lọc ra các user CÓ QUYỀN TRUY CẬP vào công ty của picking vừa chọn
            valid_users = users.filtered(lambda u: selected_picking.company_id in u.company_ids)
                
            # 3. Chọn ngẫu nhiên user trong tập các user hợp lệ đó
            selected_user = valid_users[(minute * 5 + hour * 11 + day * 13 + current_salt) % len(valid_users)]
            
            # 4. Đảm bảo set đúng ngữ cảnh Công ty bằng with_company() kết hợp with_user()
            simulated_picking = selected_picking.with_company(selected_picking.company_id).with_user(selected_user)
            
            # 5. Thực thi action
            simulated_picking.action_assign()


    @api.model
    def cron_simulate_picking_validate(self):
        """
        [CRON] Giả lập nhân viên: Validate (Xác nhận hoàn tất).
        
        Mục đích: 
        - Giả lập việc nhân viên kho đã lấy/giao xong hàng và bấm 'Xác nhận' để chốt sổ giao dịch.
        - Khi nhấn nút này, hệ thống gọi button_validate().
        - Điều kiện bắt buộc (Test Case target): Các phiếu kho đã được giữ đủ hàng, ở trạng thái 'Sẵn sàng' (assigned).
        """
        now = fields.Datetime.now()
        minute = now.minute
        hour = now.hour
        day = now.day
        # Chỉ giả lập bằng user đang hoạt động và có quyền thao tác kho.
        stock_user_group = self.env.ref('stock.group_stock_user')
        users = self.env['res.users'].search([
            ('id', '>', 1),
            ('active', '=', True),
            ('share', '=', False),
            ('all_group_ids', 'in', [stock_user_group.id]),
        ])
        expired_lot_act_type = self.env.ref('employee_simulator.mail_activity_expired_lot')
        pickings = self.env['stock.picking'].search([
            ('state', '=', 'assigned'),
            ('activity_ids', 'not any', [
                ('activity_type_id', '=', expired_lot_act_type.id),
            ]),
        ])

        salt = random.randint(1, 10000)
        record_count = (minute + hour + salt) % 3 + 1
        
        record_count = min(record_count, len(pickings))
        
        for i in range(record_count):
            current_salt = salt + i
            
            # 1. Chọn phiếu kho trước
            picking_index = (minute * 11 + hour * 19 + day * 23 + current_salt) % len(pickings)
            selected_picking = pickings[picking_index]
            
            # Khi validate, Odoo có thể cần đọc company_id của sản phẩm để tạo
            # Lot/Serial. Vì vậy user mô phỏng phải có quyền với cả công ty của
            # phiếu lẫn các công ty được gán trên sản phẩm của phiếu.
            required_companies = (
                selected_picking.company_id
                | selected_picking.move_ids.product_id.company_id
            )
            valid_users = users.filtered(
                lambda user: not (required_companies - user.company_ids)
            )

            selected_user = valid_users[(minute * 7 + hour * 13 + day * 17 + current_salt) % len(valid_users)]
            
            pickings -= selected_picking
            
            simulated_picking = selected_picking.with_user(selected_user.id).with_company(selected_picking.company_id)

            _logger.info(
                '[VALIDATE] Đang thao tác stock.picking: id=%s, mã=%s, user_id=%s',
                selected_picking.id,
                selected_picking.name,
                selected_user.id,
            )
            try:
                action_result = simulated_picking.with_context(skip_sms=True).button_validate()
            except UserError as e:
                error_msg = str(e)
                if "empty transfer" in error_msg or "zero quantity" in error_msg or "Transfer trouble alert" in error_msg:
                    missing_qty_act_type = self.env.ref('employee_simulator.mail_activity_missing_quantity', raise_if_not_found=False)
                    if missing_qty_act_type:
                        has_missing_qty_act = any(act.activity_type_id.id == missing_qty_act_type.id for act in simulated_picking.activity_ids)
                        if not has_missing_qty_act:
                            simulated_picking.activity_schedule(
                                'employee_simulator.mail_activity_missing_quantity', 
                                summary='Cần điền số lượng hoàn thành (Done Quantity)',
                                note=f'Validate thất bại do chưa điền số lượng: <b>{error_msg}</b>',
                                user_id=selected_user.id
                            )
                elif "Lot/Serial" in str(e):
                    missing_lot_act_type = self.env.ref('employee_simulator.mail_activity_missing_lot', raise_if_not_found=False)
                    if missing_lot_act_type:
                        # Tránh tạo trùng Activity nếu phiếu đã có activity này
                        has_missing_lot_act = any(act.activity_type_id.id == missing_lot_act_type.id for act in simulated_picking.activity_ids)
                        if not has_missing_lot_act:
                            simulated_picking.activity_schedule(
                                'employee_simulator.mail_activity_missing_lot', 
                                summary='Thiếu Lot/Serial khi Xác nhận (Validate)',
                                note=f'Validate thất bại do thiếu Lot/Serial: <b>{str(e)}</b>',
                                user_id=selected_user.id
                            )
                else:
                    _logger.exception("[CRON VALIDATE] Phiếu %s bị lỗi khi Validate: %s", simulated_picking.name, str(e))
                
                # Bỏ qua phiếu kho hiện tại và tiếp tục xử lý các phiếu kho khác
                continue
            if isinstance(action_result, dict):
                if action_result.get('res_model') == 'stock.backorder.confirmation':
                    simulated_picking.activity_schedule(
                        'employee_simulator.mail_activity_backorder',
                        summary='Xác nhận tạo Backorder',
                        note='Hệ thống tự động phát hiện thiếu hàng khi Validate. Cần xử lý tạo Backorder.',
                        user_id=selected_user.id
                    )
                else:
                    import json
                    formatted_json = json.dumps(action_result, indent=4, default=str)
                    _logger.info(f"{simulated_picking.name}:\n{formatted_json}")

    @api.model
    def cron_simulate_picking_cancel(self):
        """
        [CRON] Giả lập nhân viên/quản lý: Cancel (Hủy phiếu).
        
        Mục đích: 
        - Giả lập tình huống khách hủy đơn hoặc tạo nhầm phiếu, người dùng bấm nút 'Hủy'.
        - Khi nhấn nút này, hệ thống gọi action_cancel().
        - Điều kiện bắt buộc (Test Case target): Chỉ tác động lên các phiếu chưa hoàn thành (thường là draft, confirmed, hoặc assigned).
        """
        activity_type = self.env.ref(
            'employee_simulator.mail_activity_simulate_cancel',
            raise_if_not_found=False,
        )

        today = fields.Date.context_today(self)
        pickings = self.env['stock.picking'].search([
            ('activity_ids', 'any', [
                ('activity_type_id', '=', activity_type.id),
                ('date_deadline', '<', today),
            ]),
            ('state', 'in', ['draft', 'confirmed', 'waiting', 'assigned']),
        ], limit=5)

        for picking in pickings:
            target_activities = picking.activity_ids.filtered(
                lambda activity: (
                    activity.activity_type_id.id == activity_type.id
                    and activity.date_deadline < today
                )
            )
            activity_user = target_activities[:1].user_id or self.env.user

            if (
                activity_user.has_group('stock.group_stock_user')
                and picking.company_id in activity_user.company_ids
            ):
                simulated_user = activity_user
            else:
                stock_group = self.env.ref('stock.group_stock_user')
                simulated_user = self.env['res.users'].sudo().search([
                    ('active', '=', True),
                    ('all_group_ids', 'in', [stock_group.id]),
                    ('company_ids', 'in', [picking.company_id.id]),
                ], order='id', limit=1)

            simulated_picking = picking.with_user(simulated_user).with_company(
                picking.company_id
            )

            try:
                simulated_picking.action_cancel()
            except Exception:
                _logger.exception(
                    "[CRON PICKING CANCEL] Không thể hủy phiếu %s với user_id=%s",
                    picking.name,
                    simulated_user.id,
                )
                continue
    
    @api.model
    def cron_process_missing_lot_activities(self, picking_type_domain=None):
        """
        Tự động khai báo Lot/Serial cho các phiếu có activity quá hạn.

        Mặc định chỉ xử lý phiếu nhập kho và sản xuất. Cron chuyển
        nội bộ có thể tái sử dụng logic bằng cách truyền domain riêng.
        """
        activity_type = self.env.ref('employee_simulator.mail_activity_missing_lot', raise_if_not_found=False)

        domain = [
            ('activity_ids', 'any', [
                ('activity_type_id', '=', activity_type.id),
                ('date_deadline', '<', fields.Date.today()),
            ]),
        ]
        if picking_type_domain is None:
            picking_type_domain = [
                ('picking_type_id.code', 'in', ['incoming', 'mrp_operation']),
            ]
        domain += picking_type_domain
        
        pickings = self.env['stock.picking'].search(domain, limit=500)

        local_time = fields.Datetime.now() + timedelta(hours=7)
        time_str = local_time.strftime('%m%d%H%M%S')

        def make_code(prefix, salt):
            rand_str = ''.join(random.choices(string.ascii_uppercase, k=3))
            return f"SIM-{prefix}-{time_str}-{salt}-{rand_str}"
            
        for picking in pickings:
            is_fully_processed = True 
            
            for line in picking.move_line_ids:
                if line.product_id.tracking == 'none' or (line.lot_id or line.lot_name):
                    continue
                
                if line.product_id.tracking == 'lot':
                    line.write({'lot_name': make_code('LOT', f"L{line.id}")})
                
                elif line.product_id.tracking == 'serial':
                    qty = line.product_uom_qty or line.qty_done or 1.0 
                    if qty <= 1.0:
                        line.write({'lot_name': make_code('SN', f"L{line.id}")})
                    else:
                        is_fully_processed = False 
                        continue

            if is_fully_processed:
                target_activities = picking.activity_ids.filtered(lambda a: a.activity_type_id.id == activity_type.id)
                for activity in target_activities:
                    activity.action_done()
    @api.model
    def cron_simulate_backorder_create(self):
        """
        [CRON] Giả lập nhân viên: Xử lý Activity Backorder - Tự động chọn "Tạo Backorder"
        """
        activity_type = self.env.ref('employee_simulator.mail_activity_backorder', raise_if_not_found=False)
        warning_act_type = self.env.ref('employee_simulator.mail_activity_simulator_error', raise_if_not_found=False)
        missing_lot_act_type = self.env.ref('employee_simulator.mail_activity_missing_lot', raise_if_not_found=False)
        expired_lot_act_type = self.env.ref('employee_simulator.mail_activity_expired_lot', raise_if_not_found=False)
        if not activity_type:
            return

        domain = [
            ('activity_ids.activity_type_id', '=', activity_type.id),
            ('activity_ids', 'not any', [('activity_type_id', '=', warning_act_type.id)]),
            ('activity_ids', 'not any', [('activity_type_id', '=', missing_lot_act_type.id)]),
            ('activity_ids', 'not any', [('activity_type_id', '=', expired_lot_act_type.id)]),
        ]
        
        pickings = self.env['stock.picking'].search(domain, limit=10)

        for picking in pickings:
            _logger.info("[CRON SIMULATE BACKORDER] Đang xử lý tạo backorder cho phiếu: %s", picking.name)
            target_activities = picking.activity_ids.filtered(lambda a: a.activity_type_id.id == activity_type.id)
            user_id = target_activities[0].user_id.id if target_activities else self.env.user.id

            simulated_picking = picking.with_user(user_id)
            
            context = {
                'button_validate_picking_ids': [simulated_picking.id],
                'default_pick_ids': [(4, simulated_picking.id)],
                'default_company_id': simulated_picking.company_id.id,
            }
            
            wizard = self.env['stock.backorder.confirmation'].with_user(user_id).with_company(picking.company_id.id).with_context(context).create({
                'pick_ids': [(4, simulated_picking.id)]
            })
            try:
                action_result = wizard.process()
            except UserError as e:
                if "empty transfer" in str(e) or "zero quantity" in str(e) or "Transfer trouble alert" in str(e):
                    # Gắn Activity cảnh báo cho User
                    simulated_picking.activity_schedule(
                        'employee_simulator.mail_activity_simulator_error', 
                        summary='Lỗi xác nhận phiếu trống',
                        note=f'Hệ thống tự động xử lý Backorder thất bại: <b>{str(e)}</b><br/>Vui lòng kiểm tra lại.',
                        user_id=user_id
                    )
                elif "Lot/Serial" in str(e):
                    # Kiểm tra để tránh tạo trùng lặp Activity
                    has_missing_lot_act = any(act.activity_type_id.id == missing_lot_act_type.id for act in simulated_picking.activity_ids)
                    if not has_missing_lot_act:
                        simulated_picking.activity_schedule(
                            'employee_simulator.mail_activity_missing_lot', 
                            summary='Thiếu Lot/Serial khi tạo Backorder',
                            note=f'Xử lý Backorder thất bại do thiếu Lot/Serial: <b>{str(e)}</b>',
                            user_id=user_id
                        )
                else:
                    _logger.exception("[CRON SIMULATE BACKORDER] Phiếu %s bị lỗi khi xử lý: %s", picking.name, str(e))
                continue
            # 1. Nếu có popup, in ra để nghiên cứu
            if isinstance(action_result, dict):
                if action_result.get('res_model') == 'expiry.picking.confirmation':
                    # Sinh ra Activity để đánh dấu phiếu kho đang bị kẹt do hàng hết hạn
                    simulated_picking.activity_schedule(
                        'employee_simulator.mail_activity_expired_lot',
                        summary='Xác nhận hàng hết hạn',
                        note='Hệ thống phát hiện lô hàng đã hết hạn khi Validate. Cần xử lý xác nhận xuất/nhập.',
                        user_id=user_id
                    )
                else:
                    # NẾU KHÁC POPUP HẾT HẠN THÌ MỚI IN LOG RA ĐỂ XEM ĐÓ LÀ GÌ
                    import json
                    _logger.info(
                        "[CRON SIMULATE] Phát hiện Popup/Action mới từ picking %s:\n%s", 
                        simulated_picking.name, 
                        json.dumps(action_result, indent=4, ensure_ascii=False, default=str)
                    )
            
            # 2. KIỂM TRA NGHIỆP VỤ: Chỉ đóng activity khi phiếu kho đã chốt thành công
            if simulated_picking.state == 'done':
                for activity in target_activities:
                    activity.action_done()
