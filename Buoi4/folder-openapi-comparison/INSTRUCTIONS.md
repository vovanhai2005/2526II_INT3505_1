# So Sánh Các Đặc Tả API

Thư mục này chứa cùng một Book Management API (API Quản lý Sách) nhưng được triển khai bằng bốn định dạng đặc tả API khác nhau. Mục tiêu là để minh họa sự khác biệt về cú pháp, cấu trúc, khả năng đọc hiểu và các công cụ hỗ trợ giữa những tiêu chuẩn phổ biến này.

## Các Ngôn Ngữ Được So Sánh

### 1. OpenAPI (trước đây là Swagger)
* **Định dạng:** YAML hoặc JSON.
* **Tổng quan:** Là tiêu chuẩn công nghiệp thống lĩnh không thể bàn cãi trong việc định nghĩa các RESTful API. Nó sở hữu hệ sinh thái công cụ lớn nhất hỗ trợ cho việc sinh code, viết tài liệu và kiểm thử.
* **Điểm mạnh:** Cộng đồng khổng lồ, được hỗ trợ sẵn (out-of-the-box) bởi hầu hết các API gateway và framework (như thư viện `flasgger` được dùng trong ứng dụng Flask của chúng ta).
* **Điểm yếu:** Cú pháp có thể trở nên rườm rà, khó đọc và khó bảo trì khi gom chung vào các file đơn lẻ có kích thước lớn.

### 2. RAML (RESTful API Modeling Language)
* **Định dạng:** YAML.
* **Tổng quan:** Được thiết kế để định nghĩa API một cách rành mạch bằng cách sử dụng cấu trúc phân cấp từ trên xuống (top-down). Nó nhấn mạnh vào khả năng tái sử dụng thông qua các khái niệm như "traits" (đặc điểm) và "resource types" (loại tài nguyên).
* **Điểm mạnh:** Cực kỳ tuân thủ nguyên tắc DRY (Don't Repeat Yourself - Không lặp lại code). Rất xuất sắc cho quy trình lập kế hoạch API theo hướng Design-First (Thiết kế trước).
* **Điểm yếu:** Hệ sinh thái nhỏ hơn so với OpenAPI.

### 3. API Blueprint
* **Định dạng:** Markdown (Markdown với cú pháp cấu trúc đặc thù).
* **Tổng quan:** Tập trung mạnh mẽ vào khía cạnh tài liệu và khả năng đọc hiểu của con người. Nếu bạn đã biết Markdown, API Blueprint sẽ cực kỳ dễ tiếp cận.
* **Điểm mạnh:** Cực kỳ dễ dàng cho những người không phải lập trình viên (như Quản lý sản phẩm, Chuyên viên viết tài liệu kỹ thuật) đọc và đánh giá.
* **Điểm yếu:** Các công cụ hỗ trợ hầu như chỉ giới hạn ở việc sinh tài liệu (như `aglio`), và việc mô hình hóa các cấu trúc dữ liệu phức tạp có thể gặp nhiều khó khăn.

### 4. TypeSpec
* **Định dạng:** TypeSpec (Cú pháp giống TypeScript).
* **Tổng quan:** Một ngôn ngữ hiện đại do Microsoft tạo ra. Nó mượn các khái niệm cú pháp từ TypeScript để định nghĩa API và model, sau đó sẽ được biên dịch (compile) ngược ra chuẩn OpenAPI (hoặc các định dạng khác).
* **Điểm mạnh:** Tính mô-đun hóa cao, mang lại trải nghiệm cho lập trình viên (DX) xuất sắc, hỗ trợ tự động gợi ý code (auto-complete) trên IDE rất tuyệt vời và cú pháp cực kỳ ngắn gọn.
* **Điểm yếu:** Còn tương đối mới, nghĩa là các công cụ gốc chạy trực tiếp TypeSpec vẫn đang trong giai đoạn phát triển (tuy nhiên, khả năng biên dịch ra OpenAPI đã giải quyết được hầu hết các vấn đề về tính tương thích).

## Bảng Tóm Tắt So Sánh

| Tiêu chí | OpenAPI | RAML | API Blueprint | TypeSpec |
| :--- | :--- | :--- | :--- | :--- |
| **Cú pháp** | YAML / JSON | YAML | Markdown | Giống TypeScript |
| **Mức độ Dễ đọc** | Trung bình (có thể rườm rà) | Tốt (phân cấp) | Xuất sắc | Xuất sắc (với Lập trình viên) |
| **Hệ sinh thái/Công cụ** | Khổng lồ | Trung bình | Nhỏ | Đang phát triển (Dựa vào trình biên dịch OpenAPI) |
| **Phù hợp nhất cho** | Khả năng tương thích phổ quát | Các API có cấu trúc cao, dễ tái sử dụng | Ưu tiên tài liệu, người không code review | Ưu tiên lập trình viên, API mô-đun quy mô lớn |

## Hướng Dẫn Chạy & Xem Tài Liệu

Mỗi thư mục con đều chứa file đặc tả cho Book Management API và một file `README.md` đính kèm hướng dẫn cách render tài liệu đó trên máy cá nhân (localhost).

* [Hướng dẫn OpenAPI](./openapi/README.md)
* [Hướng dẫn RAML](./raml/README.md)
* [Hướng dẫn API Blueprint](./api-blueprint/README.md)
* [Hướng dẫn TypeSpec](./typespec/README.md)