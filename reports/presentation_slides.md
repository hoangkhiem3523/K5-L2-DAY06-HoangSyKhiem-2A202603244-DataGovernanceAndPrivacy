# Báo Cáo Demo Track T02 · Raw QC Triage Pipeline

> **Tài liệu chuẩn bị thuyết trình nhóm G01 — Field-to-Release PoC**  
> **Chủ đề:** Raw QC Triage: Xếp Hạng & Lọc Khiếm Khuyết Ảnh Thô Cho Xe Tự Hành  
> **File slide trình chiếu trực quan (HTML Sáng, Font Arial):** [`reports/presentation_slides.html`](file:///D:/CODE/TrainAI/lab/K5-L2-DAY06-HoangSyKhiem-2A202603244-DataGovernanceAndPrivacy/reports/presentation_slides.html)

---

## 🖥️ SLIDE 1: GIỚI THIỆU & PHÂN CÔNG NHIỆM VỤ 5 THÀNH VIÊN

* **Đề tài:** Raw QC Triage: Tự Động Lọc & Phân Loại Khiếm Khuyết Ảnh Thô (Track T02)
* **Mục tiêu:** Tiền kiểm định chất lượng ảnh camera xe tự hành, chọn lọc 20 ảnh lỗi nghiêm trọng nhất cho chuyên gia thẩm định với chi phí vận hành tối ưu.
* **Phân công 5 thành viên (Nhóm G01):**
  1. **Hoàng Sỹ Khiêm (Trưởng nhóm):** Điều phối, ghép bài, phát triển thuật toán cốt lõi, chạy toàn bộ pipeline.
  2. **Nguyễn Đình Phú (Phụ trách Dữ liệu):** Phân tích thống kê dữ liệu đầu vào (EDA), xây dựng mô hình baseline.
  3. **Nguyễn Khải Hưng (Xử lý thuật toán):** Mô hình hóa toán học 4 công thức chấm điểm lỗi.
  4. **Trần Đức Thiên (Kiểm tra & Ca khó):** Thiết kế bộ kiểm thử biên (Edge-case tests), đo đạc chỉ số.
  5. **Lê Hoàng Đức (Người duyệt):** Thẩm định hàng đợi reviewer, ghi nhận nhật ký kiểm toán.
* **Số liệu nổi bật:**
  * **Recall@20:** 85.0% (phát hiện chính xác 17/20 ảnh lỗi trong batch).
  * **Thời gian thực thi:** 0.43 giây (chạy offline trên CPU thường).

---

## 🖥️ SLIDE 2: SƠ ĐỒ 6 BƯỚC DEMO THEO ĐÚNG MÁY CHIẾU

*Quy trình khép kín: Dữ liệu đầu vào → Xử lý → Người duyệt → Chạy lại → Kết quả cuối cùng.*

```
[1. Nêu bài toán]  ──► [2. Mẫu đầu vào]  ──► [3. Chạy bản thử]  ──► [4. Duyệt 1 mục]  ──► [5. Chạy lại/Kiểm]  ──► [6. Hiệu quả/Ca khó]
  (Trưởng nhóm)        (Phụ trách Data)        (Xử lý + Lead)          (Người duyệt)        (Chạy + Kiểm tra)        (Kiểm + Ca khó)
```

* **Thao tác cụ thể trên màn hình khi demo:**
  * **Bước 1 (Khiêm):** Mở file `configs/tracks/t02.yaml` nêu mục tiêu.
  * **Bước 2 (Phú):** Mở file `fixtures/t02_raw_qc/images.csv` và trình chiếu 1 ảnh thiếu sáng mẫu `img_02_3.jpg`.
  * **Bước 3 (Hưng + Khiêm):** Chạy lệnh `python -m src.main --track t02 --offline` và mở file `review_queue.csv`.
  * **Bước 4 (Đức):** Mở `out/poc/contact_sheet.html`, bấm xác nhận 1 ảnh lỗi và export file.
  * **Bước 5 (Khiêm):** Mở file `decision.json` (quyết định REWORK).
  * **Bước 6 (Thiên):** Mở bảng so sánh `reports/table1_baseline_vs_poc.md` và chỉ ra ca khó lóa đèn pha `glare_missed.png`.

---

## 🖥️ SLIDE 3: BỐI CẢNH THỰC TẾ & THỬ THÁCH CỦA THUẬT TOÁN BASELINE CŨ

*Mô hình baseline cũ áp dụng một ngưỡng Laplacian toàn cục cố định, dẫn đến 3 sai lệch lớn:*

1. **Sai lệch phần cứng Camera:**
   * Cam A nét đạt tiêu chuẩn ~1000 điểm; Cam B thấu kính mềm tự nhiên chỉ đạt ~250 điểm.
   * ❌ **Hậu quả:** 100% ảnh đạt chuẩn của Cam B bị đánh giá nhầm là ảnh mờ (False Alarm)!
2. **Lóa sáng cục bộ (Glare):**
   * Đèn pha rọi làm cháy sáng bão hòa một vùng ảnh, nhưng xung quanh vẫn có chi tiết viền.
   * ❌ **Hậu quả:** Baseline bỏ lọt 100% các trường hợp lóa sáng (Recall Glare = 0%)!
3. **Điều kiện ban đêm:**
   * Ban đêm cảnh vật ít viền tương phản hơn ban ngày.
   * ❌ **Hậu quả:** Baseline báo nhầm tới 75% ảnh đêm hợp lệ thành ảnh lỗi, gây quá tải đội ngũ kiểm định!

---

## 🖥️ SLIDE 4: GIẢI PHÁP KỸ THUẬT CỦA NHÓM (POC PIPELINE)

### 4 Bộ cảm biến hiệu chuẩn toán học:
1. **Lỗi Mờ (Blur):** Chuẩn hóa theo camera: `lap_norm = lap / 1000` (Cam A) hoặc `lap / 250` (Cam B). Chỉ phạt khi độ nét tụt dưới 15% so với chuẩn camera.
2. **Lỗi Tối (Dark):**
   * Ban ngày: Phạt khi độ sáng trung bình `mean < 40`.
   * Ban đêm: Chỉ ghi nhận lỗi khi môi trường thiếu sáng nghiêm trọng (`mean < 15` và hơn 85% diện tích là pixel tối).
3. **Lỗi Lóa (Glare):** Quét tỷ lệ pixel cháy sáng bão hòa `sat > 0.003`.
4. **Lỗi Nén (Compression):** Đo độ chênh lệch pixel tại biên khối JPEG 8x8.

### 🛡️ Cơ chế triệt tiêu lỗi chéo (Defect Masking):
* Ảnh thiếu sáng nghiêm trọng sẽ mất toàn bộ viền cạnh → Phương sai Laplacian suy giảm mạnh.
* **Quy tắc code:**
  ```python
  if s_dark > 0.4:
      s_blur = 0.0  # Dập tắt hiện tượng dương tính giả với lỗi mờ!
  ```
* Xác định chính xác nguyên nhân cốt lõi là lỗi `Dark` để điều chỉnh phơi sáng, tránh yêu cầu bảo trì ống kính không cần thiết.

---

## 🖥️ SLIDE 5: KẾT QUẢ THỰC NGHIỆM ĐỐI SÁNH (BASELINE VS POC)

| Chỉ Số Đánh Giá (Metric) | Nhóm Dữ Liệu | Baseline | PoC Nhóm G01 | Mức Độ Cải Thiện |
|---|:---:|:---:|:---:|:---:|
| **Defect Recall@20 (Chỉ số chính)** | Toàn bộ ảnh | 0.5000 (10/20) | **0.8500 (17/20)** | **+70.0% vượt trội** |
| **Precision@20** | Toàn bộ ảnh | 0.5000 | **0.8500** | **+70.0% tương đối** |
| **Độ chính xác phân loại lỗi** | Toàn bộ ảnh lỗi | n/a | **0.7500** | **75.0% đúng bệnh** |
| Tỷ lệ báo nhầm ban đêm (False Alarm) | Ban đêm (night) | 0.7500 (75%) | **0.2500 (25%)** | **Giảm 3 lần tỷ lệ báo nhầm** |
| Tỷ lệ báo nhầm chập tối (False Alarm) | Chập tối (dusk) | 0.5000 (50%) | **0.0000 (0%)** | **Triệt tiêu báo nhầm (0.0%)** |
| **Thời gian chạy / 100 ảnh** | Chạy trên CPU | 0.08 s | **0.43 s** | Dưới 0.5 giây |

---

## 🖥️ SLIDE 6: GIAO DIỆN VẬN HÀNH & QUẢN TRỊ DỮ LIỆU

### 1. Giao diện Reviewer thực tế: Contact Sheet HTML
* File `out/poc/contact_sheet.html` hiển thị lưới 20 ảnh trực quan kèm điểm số và loại lỗi.
* Reviewer có quyền duyệt, sửa nhãn (Override), bấm **Export CSV** lưu nhật ký kiểm toán.
* Tự động sinh `decision.json`: Quyết định **REWORK** do tỷ lệ ảnh lỗi đạt 85% (> 20% ngưỡng an toàn).

### 2. Quản trị dữ liệu (Data Governance):
* **Không rò rỉ dữ liệu:** Chia split theo cảnh gốc (Scene-level split).
* **Quyền riêng tư:** 100% synthetic procedural, không PII, tuân thủ Nghị định 13/2023/NĐ-CP.
* **Toàn vẹn:** Khớp 100% mã băm SHA-256 qua `manifest.csv`.

---

## 🖥️ SLIDE 7: MINH CHỨNG: NHÓM ĐÃ GIẢI QUYẾT 2 CA KHÓ NHẤT

*Hai ca lỗi kinh điển từng làm sai lệch kết quả của thuật toán baseline cũ nay đã được xử lý triệt để:*

### ✅ Ca Khó 1: Khắc Phục Sai Lệch Phần Cứng Camera B (Tránh Báo Nhầm)
* **Bối cảnh:** Camera dòng B sử dụng thấu kính quang học mềm. Độ nét Laplacian nền tự nhiên chỉ đạt **~235 điểm** (so với Cam A đạt ~1000).
* **Thuật toán cũ (Baseline):** Áp dụng ngưỡng cố định > 500 → Đánh giá nhầm **100% ảnh đạt chuẩn của Cam B là ảnh mờ (Blur)**, gây nguy cơ loại bỏ dữ liệu hợp lệ!
* **Cách nhóm giải quyết:** Chuẩn hóa độ nét tương đối theo từng dòng camera:
  `lap_norm = lap / 250 (với Cam B)`
* **Kết quả:** Ảnh đạt 235 điểm có `lap_norm ≈ 0.94 > 0.15` → Hệ thống phân loại chính xác là ảnh đạt chuẩn (`none / KEEP`). **Bảo toàn 100% dữ liệu hợp lệ của Camera B!**

### ✅ Ca Khó 2: Phân Định Rõ Ràng Lỗi Thiếu Sáng và Lỗi Mờ (Dark vs Blur)
* **Bối cảnh:** Ảnh chụp ban ngày nhưng phương tiện di chuyển vào hầm tối hoặc cảm biến mất tín hiệu → Ảnh bị thiếu sáng nghiêm trọng (như mẫu `img_02_3`).
* **Thuật toán cũ (Baseline):** Vùng tối không còn viền cạnh → Phương sai Laplacian suy giảm → **Đánh giá nhầm thành lỗi mờ (Blur)**, dẫn đến xử lý sai quy trình kỹ thuật.
* **Cách nhóm giải quyết:** Thiết kế cơ chế triệt tiêu lỗi chéo:
  ```python
  if s_dark > 0.4:
      s_blur = 0.0  # Dập tắt hiện tượng dương tính giả với lỗi mờ!
  ```
* **Kết quả:** Triệt tiêu hiện tượng dương tính giả với lỗi mờ, **xác định đúng 100% nguyên nhân là Dark (Thiếu sáng)** → Đưa ra khuyến nghị điều chỉnh phơi sáng chính xác.

---

## 🖥️ SLIDE 8: CÁC GIỚI HẠN MÀ GIẢI PHÁP NÀY CHƯA ĐẠT ĐƯỢC

*Phân tích khách quan các điểm nghẽn kỹ thuật và ca khó còn tồn tại:*

1. **Bỏ sót lóa đèn cục bộ quá nhỏ (Local Specular Glare):**
   * *Hiện trạng:* Thuật toán tính tỷ lệ pixel bão hòa `sat > 0.003` trên toàn bộ bức ảnh.
   * *Điểm chưa đạt:* Nếu đốm lóa có kích thước quá nhỏ (< 0.1% diện tích) nhưng rọi trúng ngay biển số xe, tỷ lệ toàn ảnh không vượt ngưỡng nên bị bỏ sót (như ca lỗi `reports/failure_cases/glare_missed.png`).
   * *Hướng khắc phục:* Bổ sung quét ô cục bộ (Patch-based scanning) hoặc mặt nạ vùng quan tâm (ROI Masking).

2. **Khoảng cách miền dữ liệu (Sim-to-Real Domain Gap):**
   * *Hiện trạng:* Toàn bộ 96 ảnh thử nghiệm là ảnh mô phỏng máy tính (Synthetic Procedural).
   * *Điểm chưa đạt:* Chưa kiểm nghiệm trên dữ liệu thế giới thực phức tạp với các hiện tượng nhiễu hạt cảm biến động (dynamic sensor noise), vệt nước mưa trên kính lái (wiper streaks) hay đèn đường nhấp nháy.
   * *Hướng khắc phục:* Mở rộng thử nghiệm trên các tập dữ liệu mở thực tế ngoài đường phố (BDD100K hoặc ACDC).

3. **Chưa cộng dồn đa khiếm khuyết (Multi-defect Aggregation):**
   * *Hiện trạng:* Thuật toán gộp điểm bằng hàm lấy giá trị lớn nhất `score = max(...)`.
   * *Điểm chưa đạt:* Khi một bức ảnh vừa mờ nhẹ (0.28) vừa thiếu sáng nhẹ (0.28), điểm tổng vẫn chỉ là 0.28 (< 0.3 ngưỡng phạt) nên bị đánh giá là ảnh sạch, dù thực tế chất lượng cộng dồn đã rất tệ.
   * *Hướng khắc phục:* Chuyển sang mô hình chấm điểm kết hợp đa yếu tố (Weighted Multi-defect Scoring).

4. **Ngưỡng cố định, chưa tự thích ứng (Dynamic Threshold):**
   * *Hiện trạng:* Các thông số Cam A = 1000, Cam B = 250 là hằng số cố định được ước lượng từ tập dev.
   * *Điểm chưa đạt:* Nếu bổ sung dòng camera mới có đặc tính quang học khác, hệ thống phải tiến hành phân tích và cấu hình lại bằng tay.
   * *Hướng khắc phục:* Xây dựng cơ chế tự động học ngưỡng nền động (Online Baseline Calibration) từ luồng video.
