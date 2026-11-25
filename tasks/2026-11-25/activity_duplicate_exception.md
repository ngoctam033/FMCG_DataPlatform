Loại trừ Exception khỏi quy tắc chống trùng Activity
Tại sao cần thay đổi?
Quy tắc cũ không cho phép tạo mail.activity nếu đã tồn tại một activity có cùng res_model, res_id, activity_type_id và active = True.

Quy tắc này phù hợp với activity điều phối workflow nhưng không phù hợp với activity cảnh báo (Exception).

Ví dụ trong nghiệp vụ kho: khi một picking được hoàn thành với số lượng thực tế nhỏ hơn nhu cầu và không tạo backorder, Odoo có thể tạo Exception trên chứng từ liên quan cần được cảnh báo. Nhiều picking khác nhau có thể phát sinh các cảnh báo độc lập trên cùng một chứng từ đích.

Nếu chứng từ đích đã có Exception đang active, quy tắc cũ sẽ chặn cảnh báo mới dù hai cảnh báo đại diện cho hai sự kiện khác nhau. UserError khiến các thay đổi chưa commit trong transaction bị rollback và nghiệp vụ có thể không hoàn tất.
Thay đổi
Trong Server Action action_prevent_duplicate_active_activity, bổ sung điều kiện loại trừ Activity Type Exception chuẩn của Odoo:
exception_type = env.ref('mail.mail_activity_data_warning')

if (
    record
    and record.res_model
    and record.res_id
    and record.activity_type_id != exception_type
):
    # Giữ nguyên logic kiểm tra trùng lặp hiện tại.
Kết quả
Điều kiện	Trước	Sau
Exception cùng loại đang active trên cùng chứng từ	Chặn	Cho phép
Activity khác cùng loại đang active trên cùng chứng từ	Chặn	Chặn
Không có activity cùng loại đang active	Cho phép	Cho phép


Bản sửa chỉ miễn kiểm tra trùng đối với Exception chuẩn, kể cả khi nội dung cảnh báo giống nhau. Các Activity Type khác vẫn tuân theo quy tắc cũ.