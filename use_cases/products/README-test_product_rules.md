# Hệ Thống Quản Lý Sản Phẩm và Áp Dụng Quy Tắc Kinh Doanh (Business Rules)

## Giới thiệu

Dự án này mô phỏng một hệ thống quản lý sản phẩm đơn giản và sử dụng thư viện `business_rules` của Python để áp dụng các quy tắc kinh doanh (business rules) một cách tự động. Hệ thống này có thể tự động thực hiện các hành động như:

- **Giảm giá sản phẩm (put on sale):** Khi sản phẩm sắp hết hạn và còn nhiều hàng tồn kho.
- **Đặt hàng thêm (order more):** Khi hàng tồn kho thấp hoặc vào tháng 12 (tháng cao điểm mua sắm).
- **Thay đổi trạng thái kho (change stock state):** Khi số lượng hàng tồn kho thấp.
- **Gửi email thông báo (send low stock email):** Khi hàng tồn kho thấp.
- **Gửi SMS thông báo (send low stock sms):** Khi hàng tồn kho thấp.

## Công nghệ sử dụng

- **Python:** Ngôn ngữ lập trình chính.
- **`business_rules`:** Thư viện Python để định nghĩa và thực thi các quy tắc kinh doanh.
- **`datetime`:** Thư viện để làm việc với ngày tháng.
- **`json`:** Thư viện để làm việc với dữ liệu JSON.
- **`email.mime.text`:** Thư viện để tạo email.
- **`smtplib`:** Thư viện để gửi email.

## Cài đặt

1.  **Cài đặt Python:** Đảm bảo bạn đã cài đặt Python 3.x.
2.  **Cài đặt thư viện `business_rules`:**
    ```bash
    pip install business-rules
    ```

## Cấu trúc dự án

- **`test_rules_engine.py`:** File chứa code Python chính.
- **`rules.json`:** File chứa các quy tắc kinh doanh được định nghĩa dưới dạng JSON.

## Cách sử dụng

1.  **Cấu hình:**
    - Mở file `test_rules_engine.py`.
    - Thay đổi các giá trị trong phần **Configuration** cho phù hợp:
      - `EMAIL_SENDER`: Địa chỉ email của bạn (người gửi).
      - `EMAIL_RECIPIENT`: Địa chỉ email của người nhận thông báo.
      - `SMS_NUMBER`: Số điện thoại nhận SMS thông báo.
      - `RULES_FILE`: Tên file JSON chứa các quy tắc (mặc định là `rules.json`).
    - **Lưu ý:** Để gửi email, bạn cần cấu hình tài khoản email của mình. Nếu dùng Gmail, bạn có thể cần bật "Less secure app access" hoặc tạo "App Password".
2.  **Chỉnh sửa quy tắc:**
    - Mở file `rules.json`.
    - Chỉnh sửa các quy tắc kinh doanh theo nhu cầu của bạn. Cấu trúc của file JSON sẽ được giải thích chi tiết hơn ở phần sau.
3.  **Chạy chương trình:**
    ```bash
    python test_rules_engine.py
    ```

## Giải thích code

### Các lớp (Classes)

- **`Product`:** Đại diện cho một sản phẩm.

  - **`id`:** Mã sản phẩm (int).
  - **`current_inventory`:** Số lượng hàng tồn kho hiện tại (int).
  - **`price`:** Giá sản phẩm (float).
  - **`orders`:** Danh sách các đơn hàng liên quan đến sản phẩm (list of `Order`).
  - **`related_products`:** Danh sách các sản phẩm liên quan (list of int).
  - **`stock_state`:** Trạng thái kho (ví dụ: "available", "last_items", "out_of_stock") (str).
  - **`save()`:** Phương thức mô phỏng việc lưu thông tin sản phẩm vào cơ sở dữ liệu.

- **`ProductOrder`:** Đại diện cho một đơn hàng đặt mua sản phẩm.

  - **`objects`:** Danh sách tĩnh (static list) để lưu trữ tất cả các đơn hàng đã tạo.
  - **`product_id`:** Mã sản phẩm được đặt hàng (int).
  - **`quantity`:** Số lượng sản phẩm được đặt hàng (int).
  - **`create(product_id, quantity)`:** Phương thức tĩnh để tạo một đơn hàng mới và thêm nó vào danh sách `objects`.

- **`Order`:** Đại diện cho một đơn hàng (có thể là đơn hàng của khách hàng).

  - **`expiration_date`:** Ngày hết hạn của đơn hàng (`datetime.date`).

- **`Products`:** Lớp tiện ích để quản lý danh sách sản phẩm.

  - **`all_products`:** Danh sách tĩnh (static list) để lưu trữ tất cả các đối tượng `Product`.
  - **`top_holiday_items()`:** Trả về danh sách các mặt hàng bán chạy vào dịp lễ (list of dict).
  - **`add_product(product)`:** Thêm một sản phẩm vào danh sách `all_products`.
  - **`get_all_products()`:** Trả về danh sách tất cả các sản phẩm.

- **`ProductVariables`:** Lớp định nghĩa các biến (variables) mà các quy tắc kinh doanh sẽ sử dụng. Kế thừa từ `BaseVariables` của thư viện `business_rules`.

  - **`current_inventory()`:** Trả về số lượng hàng tồn kho hiện tại của sản phẩm.
  - **`expiration_days()`:** Trả về số ngày cho đến khi đơn hàng cuối cùng của sản phẩm hết hạn. Nếu không có đơn hàng, trả về 999.
  - **`current_month()`:** Trả về tháng hiện tại (ví dụ: "December").
  - **`goes_well_with()`:** Trả về danh sách các sản phẩm liên quan.

- **`ProductActions`:** Lớp định nghĩa các hành động (actions) mà các quy tắc kinh doanh có thể thực hiện. Kế thừa từ `BaseActions` của thư viện `business_rules`.
  - **`put_on_sale(sale_percentage)`:** Giảm giá sản phẩm theo phần trăm.
  - **`order_more(number_to_order)`:** Đặt hàng thêm sản phẩm với số lượng nhất định.
  - **`change_stock_state(stock_state)`:** Thay đổi trạng thái kho của sản phẩm.
  - **`send_low_stock_email()`:** Gửi email thông báo khi hàng tồn kho thấp.
  - **`send_low_stock_sms()`:** Gửi SMS thông báo khi hàng tồn kho thấp.
  - **`_send_email(subject, body)`:** Phương thức nội bộ để gửi email.
  - **`_send_sms(message)`:** Phương thức nội bộ để gửi SMS (mô phỏng).

### Hàm `load_rules_from_json(filepath)`

- Hàm này đọc các quy tắc kinh doanh từ file JSON.
- **`filepath`:** Đường dẫn đến file JSON.
- Trả về danh sách các quy tắc hoặc danh sách rỗng nếu có lỗi.

### File `rules.json`

File này chứa các quy tắc kinh doanh dưới dạng JSON. Mỗi quy tắc có:

- **`conditions`:** Điều kiện để quy tắc được kích hoạt.
  - **`all`:** Tất cả các điều kiện con phải đúng.
  - **`any`:** Ít nhất một điều kiện con phải đúng.
  - **`name`:** Tên biến (variable) cần kiểm tra.
  - **`operator`:** Toán tử so sánh (ví dụ: "less_than", "greater_than", "equal_to").
  - **`value`:** Giá trị để so sánh.
- **`actions`:** Các hành động sẽ được thực hiện nếu điều kiện đúng.
  - **`name`:** Tên hành động (action) cần thực hiện.
  - **`params`:** Các tham số cho hành động (nếu có).

**Ví dụ về một quy tắc:**

```json
{
  "conditions": {
    "all": [
      {
        "name": "expiration_days",
        "operator": "less_than",
        "value": 5
      },
      {
        "name": "current_inventory",
        "operator": "greater_than",
        "value": 20
      }
    ]
  },
  "actions": [
    {
      "name": "put_on_sale",
      "params": {
        "sale_percentage": 0.25
      }
    }
  ]
}
```
