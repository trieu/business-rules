# Hệ Thống Phân Loại Hồ Sơ và Gửi Email Mục Tiêu Dựa Trên Quy Tắc (Profile Segmentation and Targeted Emailing with Business Rules)

## Giới thiệu

Dự án này mô phỏng một hệ thống phân loại hồ sơ (profile) và gửi email mục tiêu (targeted email) dựa trên các quy tắc kinh doanh (business rules). Hệ thống này sử dụng thư viện `business_rules` của Python để định nghĩa và thực thi các quy tắc, từ đó tự động xác định hồ sơ nào phù hợp với chiến dịch email nào và gửi email tương ứng.

## Chức năng chính

*   **Phân loại hồ sơ:** Dựa trên các thông tin trong hồ sơ (ví dụ: bộ phận làm việc, chức danh, sở thích cá nhân), hệ thống sẽ phân loại hồ sơ vào các nhóm khác nhau.
*   **Gửi email mục tiêu:** Khi một hồ sơ khớp với một quy tắc, hệ thống sẽ gửi email được thiết kế riêng cho nhóm đó.
*   **Sử dụng quy tắc kinh doanh:** Các quy tắc được định nghĩa một cách rõ ràng và dễ dàng thay đổi trong file JSON.
* **Mô phỏng gửi email:** Hệ thống mô phỏng việc gửi email, có thể dễ dàng chuyển đổi thành gửi email thật.

## Công nghệ sử dụng

*   **Python:** Ngôn ngữ lập trình chính.
*   **`business_rules`:** Thư viện Python để định nghĩa và thực thi các quy tắc kinh doanh.
*   **`json`:** Thư viện để làm việc với dữ liệu JSON.
* **`smtplib`:** Thư viện để gửi email (sử dụng khi muốn gửi email thật).
* **`email.message`:** Thư viện để tạo email (sử dụng khi muốn gửi email thật).

## Cài đặt

1.  **Cài đặt Python:** Đảm bảo bạn đã cài đặt Python 3.x.
2.  **Cài đặt thư viện `business_rules`:**
    ```bash
    pip install business-rules
    ```

## Cấu trúc dự án

*   **`test_profile_rules.py`:** File chứa code Python chính.
*   **`rules_for_profile.json`:** File chứa các quy tắc kinh doanh được định nghĩa dưới dạng JSON.
* **`rules-simple.json`:** File chứa các quy tắc kinh doanh đơn giản (sử dụng cho ví dụ khác).

## Cách sử dụng

1.  **Cấu hình:**
    *   Mở file `test_profile_rules.py`.
    *   Thay đổi các giá trị trong phần **Configuration** cho phù hợp (nếu bạn muốn gửi email thật):
        *   `SMTP_SERVER`: Địa chỉ SMTP server (ví dụ: `smtp.gmail.com`).
        *   `SMTP_PORT`: Cổng SMTP (ví dụ: 587).
        *   `SMTP_USERNAME`: Tên đăng nhập email của bạn.
        *   `SMTP_PASSWORD`: Mật khẩu email của bạn (hoặc App Password nếu dùng Gmail).
        *   `SENDER_EMAIL`: Địa chỉ email của bạn (người gửi).
    * **Lưu ý:** Để gửi email, bạn cần cấu hình tài khoản email của mình. Nếu dùng Gmail, bạn có thể cần bật "Less secure app access" hoặc tạo "App Password".
2.  **Chỉnh sửa quy tắc:**
    *   Mở file `rules_for_profile.json`.
    *   Chỉnh sửa các quy tắc kinh doanh theo nhu cầu của bạn. Cấu trúc của file JSON sẽ được giải thích chi tiết hơn ở phần sau.
3.  **Chạy chương trình:**
    ```bash
    python test_profile_rules.py
    ```

## Giải thích code

### Các lớp (Classes)

*   **`ProfileVariables`:** Lớp định nghĩa các biến (variables) mà các quy tắc kinh doanh sẽ sử dụng, dựa trên thông tin trong hồ sơ (profile). Kế thừa từ `BaseVariables` của thư viện `business_rules`.
    *   **`profile_email()`:** Trả về địa chỉ email của hồ sơ.
    *   **`profile_name()`:** Trả về tên của hồ sơ.
    *   **`business_unit()`:** Trả về bộ phận làm việc của hồ sơ.
    *   **`job_title()`:** Trả về chức danh của hồ sơ.
    *   **`personal_interests()`:** Trả về sở thích cá nhân của hồ sơ (dưới dạng chuỗi).

*   **`EmailActions`:** Lớp định nghĩa các hành động (actions) mà các quy tắc kinh doanh có thể thực hiện. Kế thừa từ `BaseActions` của thư viện `business_rules`.
    *   **`send_targeted_email(recipient_email, recipient_name, campaign_id)`:** Gửi email mục tiêu đến hồ sơ.
        *   **`recipient_email`:** Địa chỉ email của người nhận.
        *   **`recipient_name`:** Tên của người nhận.
        * **`campaign_id`:** Mã chiến dịch (được lấy từ `rules_for_profile.json`).
    * Phương thức này hiện tại đang mô phỏng việc gửi email. Bạn có thể uncomment phần code để gửi email thật.

### File `rules_for_profile.json`

File này chứa các quy tắc kinh doanh dưới dạng JSON. Mỗi quy tắc có:

*   **`conditions`:** Điều kiện để quy tắc được kích hoạt.
    *   **`all`:** Tất cả các điều kiện con phải đúng.
    *   **`any`:** Ít nhất một điều kiện con phải đúng.
    *   **`name`:** Tên biến (variable) cần kiểm tra.
    *   **`operator`:** Toán tử so sánh (ví dụ: "equal_to", "contains").
    *   **`value`:** Giá trị để so sánh.
*   **`actions`:** Các hành động sẽ được thực hiện nếu điều kiện đúng.
    *   **`name`:** Tên hành động (action) cần thực hiện.
    *   **`params`:** Các tham số cho hành động (nếu có).

**Ví dụ về một quy tắc (trong `rules_for_profile.json`):**

```json
{
  "conditions": {
    "all": [
      {
        "name": "business_unit",
        "operator": "equal_to",
        "value": "Marketing"
      },
      {
        "name": "personal_interests",
        "operator": "contains",
        "value": "Technology"
      }
    ]
  },
  "actions": [
    {
      "name": "send_targeted_email",
      "params": {
        "campaign_id": "TechMarketing",
        "recipient_email": "{{profile_email}}",
        "recipient_name": "{{profile_name}}"
      }
    }
  ]
}
