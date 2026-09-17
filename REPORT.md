# Báo cáo Day 5 — điền trực tiếp trong fork của bạn

**Cách dùng:** Thay mọi dấu `…` bằng bài làm thật của bạn trước khi nộp link fork trên VLearn. Giữ nguyên bốn mục và bảng để coach đọc nhanh. Viết ngắn, cụ thể theo ảnh/vùng; không cần thuật ngữ chuyên sâu. Ví dụ trong [hướng dẫn mẫu](reports/REPORT_TEMPLATE.md) chỉ giúp hiểu cách điền, không phải câu trả lời để chép lại.

- Mã học viên theo lớp: 2A202602111 (Lê Việt Anh)
- Ngày / CVAT local: 17/09/2026 / CVAT local & Python Pipeline
- Công cụ đã dùng: Polygon, Brush, Mask2Former Swin-Large, CVAT, Python (OpenCV, PyTorch)

Mã học viên là mã lớp cấp; không cần ghi họ tên trong report nếu kênh VLearn đã nhận diện bạn. Chỉ ghi công cụ thật sự đã dùng; không có SAM vẫn làm bài bình thường.

## 1. Bài đã nộp

Ghi tên ZIP đúng như file trong `submissions/` và số ảnh đã vẽ, Save. Chưa làm hoặc export lỗi thì ghi `chưa có`, không tạo ZIP rỗng. Cột điểm là điểm tối đa của task, **không phải điểm tự chấm**.

| Task | File ZIP đúng tên | Hoàn thành mấy ảnh | Điểm tối đa (coach chấm sau) |
| --- | --- | ---: | ---: |
| easy_semantic | easy_semantic.zip | 3 / 3 | 20 |
| medium_instance | medium_instance.zip | 3 / 3 | 32 |
| hard_panoptic | hard_panoptic.zip | 2 / 2 | 30 |
| cp1_holes | cp1_holes.zip | 1 / 1 | 3 |
| cp2_slice | cp2_slice.zip | 1 / 1 | 3 |
| cp5_occlusion | cp5_occlusion.zip | 1 / 1 | 3 |
| cp3_thin | cp3_thin.zip | 1 / 1 | 3 |
| cp4_curb | cp4_curb.zip | 1 / 1 | 3 |
| cp6_coverage | cp6_coverage.zip | 1 / 1 | 3 |
| **Tổng tối đa** | | | **100** |

Nếu export lỗi, ghi task, dữ liệu đã Save đến đâu và lỗi đã báo coach.

## 2. Một quyết định trước khi dùng gợi ý

Chọn object đầu tiên bạn tự vẽ ở `medium_instance`, trước khi xem bất kỳ đề xuất tự động nào cho object đó. Ghi ảnh/vị trí đủ để tìm lại; “quy tắc biên” là lý do bạn chọn hoặc dừng mask ở ranh đó.

- Ảnh, vị trí và object Medium đầu tiên tự vẽ: Ảnh `000000181542.jpg`, chiếc xe hơi (`car`) đỗ bên lề phải, nửa dưới ảnh.
- Class và quy tắc tôi dùng để chọn biên: Class `car`. Dừng mask sát viền mép vỏ và lốp xe nhìn thấy, không mở rộng sang bóng râm dưới gầm và không vẽ lấn vào lòng đường (`road`) hay vỉa hè (`sidewalk`).
- Nếu dùng gợi ý sau đó: vùng gợi ý sai/đúng, hành động sửa/giữ và lý do: Gợi ý nhận diện đúng bao quát thân xe nhưng phần viền dưới bị dính bóng đổ gầm xe; tôi dùng Polygon/Brush cắt tỉa lại mép dưới bám đúng lốp xe.
- Nếu không dùng gợi ý: ghi “không dùng”; vẫn giải thích một quyết định gán nhãn của mình.

## 3. Một lỗi tôi tìm thấy và sửa

Chọn một lỗi **có thật** trong bài. Nếu công cụ lỗi khiến bạn chưa sửa được, ghi rõ đã thử gì và cần coach hỗ trợ gì; không ghi “đã sửa” khi chưa sửa.

- Task/ảnh/vùng: Task `easy_semantic`, ảnh `7ee6d192-89e2408b.jpg`, dải phân cách và vỉa hè góc dưới bên phải.
- Lỗi thuộc loại: sai lớp / biên: Sai lớp và lem biên giữa `road` và `sidewalk`.
- Bằng chứng tôi nhìn thấy: Màu bề mặt vỉa hè xám đậm gần giống mặt đường khiến mask `road` bị tràn đè lên mép bó vỉa hè.
- Quy tắc và hành động sửa: Căn cứ quy tắc phân định theo cao độ gờ bó vỉa và chức năng hè phố, dùng Brush chỉnh lại ranh giới chuẩn xác và chuyển vùng gờ vỉa sang lớp `sidewalk`.
- Sau sửa đã Save và export lại chưa? Đã Save và export lại thành file `easy_semantic.zip` trong `submissions/`.

Nếu bạn **đã xem Summary tự đánh giá trên GitHub Actions hoặc tự chạy script**, ghi ngắn một kết quả liên quan lỗi vừa sửa (ví dụ task, metric trước/sau nếu có): `easy_semantic` đạt mIoU 0.850 (20.0 / 20.0 điểm). Scorecard ba tier tối đa **82**, không phải điểm cuối trên 100. Không tự ghi PASS/top 3/bonus; người phụ trách xác nhận theo tiêu chí lớp. Không đưa file ground truth vào fork.

## 4. Ba ca chưa chắc hoặc đã cân nhắc

Mỗi ca là một **vùng cụ thể** khiến bạn phải cân nhắc hai cách hiểu. Ghi dấu hiệu nhìn thấy hoặc quy tắc đã dùng, rồi nêu quyết định hoặc câu hỏi cho coach. Không cần ba lỗi; ca đã quyết định được cũng hợp lệ.

| Ảnh/vị trí | Hai cách hiểu có thể | Quy tắc/chứng cứ | Quyết định hoặc câu hỏi cho coach |
| --- | --- | --- | --- |
| 1. `easy_semantic` (`7ee6d192-89e2408b.jpg`), đoạn gờ vỉa hè tiếp giáp lòng đường | Gán là `road` hay `sidewalk` | Gờ bó vỉa hè có cao độ nổi và cùng kết cấu với hè phố, phân tách mặt đường xe chạy | Quyết định gán phần gờ bó vỉa hè vào `sidewalk` |
| 2. `medium_instance` (`000000373353.jpg`), người đi bộ bị cột biển báo che ngang thân | Tách thành 2 instance `person` riêng hay giữ 1 instance `person` đa vùng (multi-polygon) | Đây là một cá thể duy nhất bị vật cản che khuất một phần (occlusion) | Quyết định gán chung 1 instance ID `person` gồm 2 mảng polygon rời |
| 3. `hard_panoptic` (`000000350023.jpg`), tán lá cây che khuất một phần tường nhà phía sau | Vẽ tường nhà xuyên suốt qua lá hay chỉ vẽ các pixel nhìn thấy của từng lớp | Quy tắc chỉ gán nhãn các pixel bề mặt nhìn thấy thực tế (visible surface), không vẽ vùng khuất | Quyết định lớp `vegetation` đè lên trước, chỉ phần tường hở ra mới gán `building` |

