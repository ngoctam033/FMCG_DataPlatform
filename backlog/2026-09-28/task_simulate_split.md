# Task: Implement `cron_simulate_picking_split`

## Mục tiêu (Objective)
- Giả lập hành động chia tách (Split) của nhân viên kho.
- Có thể là kịch bản nhận hàng thiếu phải tạo Backorder (tách phiếu), hoặc thao tác bóc 1 dòng hàng hóa lớn thành nhiều dòng nhỏ mang số Lot/Serial khác nhau.

## Kịch bản kiểm thử (Test Scenarios - TDD)
1. **Setup (Chuẩn bị):** 
   - Tạo Phiếu kho A có số lượng yêu cầu (Demand) lớn hơn số lượng thực tế (Done qty), và tiến hành xác nhận để buộc hệ thống hỏi về Backorder.
2. **Action (Thực thi):** 
   - Chạy logic xử lý wizard tạo Backorder.
3. **Assert (Kiểm tra kết quả):**
   - Phiếu kho A hoàn tất một phần số lượng.
   - Hệ thống tự tạo ra Phiếu kho B (Backorder) cho phần số lượng còn thiếu.

## Gợi ý triển khai Logic
- Việc tách phiếu tự động thường liên quan đến xử lý `stock.backorder.confirmation` wizard khi bấm Validate ở các phiếu nhận thiếu hàng.
