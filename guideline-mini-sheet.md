# Phiếu quy tắc gán nhãn Day 5

- **Học viên:** Lê Việt Anh
- **Mã học viên:** 2A202602111
- **Ngày thực hành:** 17/09/2026
- **Môi trường:** CVAT Local & Model-assisted Pipeline

---

## 1. Phân loại Segmentation theo Task

| Loại | Câu hỏi bản chất | Task tương ứng trong bài | Định dạng Export |
| --- | --- | --- | --- |
| **Semantic** | Pixel này thuộc **loại vùng (stuff)** nào? | `easy_semantic`, `cp3_thin`, `cp4_curb`, `cp6_coverage` | **Segmentation mask 1.1** (PNG) |
| **Instance** | Pixel này thuộc **vật thể (thing) cụ thể nào**? | `medium_instance`, `cp1_holes`, `cp2_slice`, `cp5_occlusion` | **COCO 1.0** (instances.json) |
| **Panoptic** | Vùng thuộc **loại nền** nào VÀ **vật đếm được** nào? | `hard_panoptic` | **COCO 1.0** (panoptic.json + PNG) |

> [!IMPORTANT]
> Tên lớp phải trùng khớp tuyệt đối từng ký tự theo file `classes.json` của từng task (ví dụ: `traffic sign` khác `traffic_sign`, `traffic light` có dấu cách). Không dùng chung một danh sách lớp cho mọi task.

---

## 2. Bảng tra cứu danh sách lớp chuẩn (`classes.json`)

| Task | Số ảnh | Loại | Danh sách Label chính xác |
| --- | :---: | :---: | --- |
| `easy_semantic` | 3 | Semantic | `road`, `sidewalk`, `building`, `vegetation`, `sky` |
| `medium_instance` | 3 | Instance | `person`, `bicycle`, `car`, `motorcycle`, `bus`, `truck` |
| `hard_panoptic` | 2 | Panoptic | **Stuff:** `road`, `sidewalk`, `building`, `vegetation`, `sky`<br>**Things:** `person`, `car`, `bus`, `truck`, `motorcycle`, `bicycle`, `traffic light` |
| `cp1_holes` | 1 | Instance | `car`, `truck`, `bus` *(chú ý khoét rỗng theo quy tắc task)* |
| `cp2_slice` | 1 | Instance | `car`, `motorcycle`, `person` *(tách các vật dính sát nhau)* |
| `cp3_thin` | 1 | Semantic | `pole`, `traffic sign`, `vegetation` *(nét mảnh, dây/cột)* |
| `cp4_curb` | 1 | Semantic | `road`, `sidewalk`, `curb` *(phân ranh gờ bó vỉa)* |
| `cp5_occlusion` | 1 | Instance | `person`, `car` *(vật bị che khuất gộp chung 1 instance)* |
| `cp6_coverage` | 1 | Semantic | `road`, `sidewalk`, `building`, `vegetation`, `sky`, `car` |

---

## 3. Quy tắc hình học & xử lý biên

- [x] **Nguyên tắc nhìn thấy (Visible surface):** Chỉ gán nhãn phần pixel thực tế nhìn thấy được trên ảnh, tuyệt đối không tự ý đoán đường biên phía sau vật cản che khuất.
- [x] **Hai vật cùng lớp sát nhau (Adjacency):** Hai cá thể đứng sát nhau vẫn phải gán thành **hai instance riêng biệt** (không gộp chung mask).
- [x] **Vật bị che khuất (Occlusion):** Một vật thể bị cột điện hoặc vật khác chắn ngang tạo thành 2 vùng nhìn thấy rời rạc vẫn thuộc về **một instance duy nhất** (multi-polygon).
- [x] **Lỗ khoét & chi tiết xe (Holes):** Kính xe/chi tiết xuyên thấu tuân thủ theo quy định riêng của task (ví dụ: không tùy tiện khoét lỗ nếu quy tắc task yêu cầu phủ kín thân xe).
- [x] **Ranh giới `road` – `sidewalk`:** Phân định dựa theo chức năng hạ tầng và cao độ gờ bó vỉa hè thực tế, không dựa thuần túy vào màu sắc bề mặt bê tông/nhựa đường.
- [x] **Kiểm tra độ chi tiết:** Phóng to (zoom in) để kiểm tra các nét mảnh, khe hở giữa các vật thể; Save và kiểm tra lại danh sách Objects trước khi export.

---

## 4. Tự kiểm tra trước khi Export (Checklist)

- [x] **1. Đúng task và đúng loại:** Đã đối chiếu chính xác loại gán nhãn (Semantic / Instance / Panoptic) cho từng bộ ảnh.
- [x] **2. Chuẩn tên Label:** Toàn bộ tên lớp trùng khớp 100% với `classes.json` (không thừa khoảng trắng, đúng chữ hoa/thường).
- [x] **3. Kiểm tra số lượng đối tượng:** Không thiếu vật, không thừa vật, không gộp 2 đối tượng thành 1, không tách sai đối tượng bị che.
- [x] **4. Chất lượng đường biên:** Mask bám sát viền vật thể, không lem sang bóng đổ (shadow), không lấn sang nền hoặc bỏ sót chi tiết rõ.
- [x] **5. Export đúng định dạng:** Đã lưu dữ liệu, tải về và đặt tên đúng định dạng ZIP tương ứng vào thư mục `submissions/`.
- [x] **6. Báo cáo bài làm:** Đã hoàn thành việc ghi chú các quyết định, lỗi đã sửa và các ca cân nhắc trong `REPORT.md`.


