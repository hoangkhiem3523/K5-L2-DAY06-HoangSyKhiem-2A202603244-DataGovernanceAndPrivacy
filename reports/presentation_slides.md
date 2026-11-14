# Báo Cáo Demo Track T02 · Raw QC Triage Pipeline

> **Tài liệu chuẩn bị thuyết trình nhóm G01 — Field-to-Release PoC**  
> **Chủ đề:** Raw QC Triage: Xếp Hạng & Lọc Khiếm Khuyết Ảnh Thô Cho Xe Tự Hành  
> **File slide trình chiếu trực quan (HTML Sáng, Font Arial):** [`reports/presentation_slides.html`](file:///D:/CODE/TrainAI/lab/K5-L2-DAY06-HoangSyKhiem-2A202603244-DataGovernanceAndPrivacy/reports/presentation_slides.html)

---

## 🖥️ SLIDE 1: GIỚI THIỆU & PHÂN CÔNG NHIỆM VỤ 5 THÀNH VIÊN

* **Đề tài:** Raw QC Triage: Tự Động Lọc & Phân Loại Khiếm Khuyết Ảnh Thô (Track T02)
* **Mục tiêu:** Tiền kiểm định chất lượng ảnh camera xe tự hành, bốc đúng 20 ảnh lỗi nặng nhất cho reviewer duyệt với chi phí thấp nhất.
* **Phân công 5 thành viên (Nhóm G01):**
  1. **Hoàng Sỹ Khiêm (Trưởng nhóm):** Điều phối, ghép bài, viết thuật toán cốt lõi, chạy toàn bộ pipeline.
  2. **Nguyễn Đình Phú (Phụ trách Dữ liệu):** Phân tích thống kê dữ liệu đầu vào (EDA), làm baseline.
  3. **Nguyễn Khải Hưng (Xử lý thuật toán):** Mô hình hóa toán học 4 công thức chấm điểm lỗi.
  4. **Trần Đức Thiên (Kiểm tra & Ca khó):** Viết unit test biên (Edge-case tests), đo đạc chỉ số.
  5. **Lê Hoàng Đức (Người duyệt):** Thẩm định hàng đợi reviewer, ghi log quyết định.
* **Số liệu nổi bật:**
  * **Recall@20:** 85.0% (bắt trúng 17/20 ảnh lỗi trong batch).
  * **Thời gian thực thi:** 0.43 giây (chạy offline trên CPU thường).

> **🗣️ Lời thoại Trưởng nhóm (Khiêm):**  
> *"Kính thưa thầy, nhóm em giải quyết bài toán: Ảnh camera xe tự hành gửi về liên tục bị mờ, lóa và tối đen. Nhóm xây dựng một bộ lọc 5 bước xử lý siêu tốc 0.4 giây, bốc trúng 85% ảnh lỗi ném vào hàng đợi cho người duyệt với ngân sách chỉ 20 tấm."*

---

## 🖥️ SLIDE 2: SƠ ĐỒ 6 BƯỚC DEMO THEO ĐÚNG MÁY CHIẾU

*Quy trình khép kín: Dữ liệu đầu vào → Xử lý → Người duyệt → Chạy lại → Kết quả cuối cùng.*

```
[1. Nêu bài toán]  ──► [2. Mẫu đầu vào]  ──► [3. Chạy bản thử]  ──► [4. Duyệt 1 mục]  ──► [5. Chạy lại/Kiểm]  ──► [6. Hiệu quả/Ca khó]
  (Trưởng nhóm)        (Phụ trách Data)        (Xử lý + Lead)          (Người duyệt)        (Chạy + Kiểm tra)        (Kiểm + Ca khó)
```

* **Thao tác cụ thể trên màn hình khi demo:**
  * **Bước 1 (Khiêm):** Mở file `configs/tracks/t02.yaml` nêu mục tiêu.
  * **Bước 2 (Phú):** Mở file `fixtures/t02_raw_qc/images.csv` và show 1 ảnh tối đen mẫu `img_02_3.jpg`.
  * **Bước 3 (Hưng + Khiêm):** Chạy `python -m src.main --track t02 --offline` và mở file `review_queue.csv`.
  * **Bước 4 (Đức):** Mở `out/poc/contact_sheet.html`, bấm xác nhận 1 ảnh lỗi và export file.
  * **Bước 5 (Khiêm):** Mở file `decision.json` (quyết định REWORK).
  * **Bước 6 (Thiên):** Mở bảng so sánh `reports/table1_baseline_vs_poc.md` và chỉ ra ca khó lóa đèn pha `glare_missed.png`.

> **🗣️ Lời thoại:**  
> *"Thưa thầy, nhóm em tuân thủ nghiêm ngặt khung trình bày 6 bước: đi từ việc nạp ảnh mẫu thô, chạy bộ lọc tự động, đưa lên bàn cho reviewer duyệt, áp quyết định và đánh giá ca khó còn tồn tại."*

---

## 🖥️ SLIDE 3: BỐI CẢNH THỰC TẾ & BẪY CỦA THUẬT TOÁN BASELINE CŨ

*Mô hình baseline cũ dùng 1 ngưỡng Laplacian toàn cục duy nhất, dẫn đến 3 thất bại lớn:*

1. **Bẫy Camera phần cứng:**
   * Cam A nét đạt ~1000 điểm; Cam B thấu kính mềm chỉ đạt ~250 điểm.
   * ❌ **Hậu quả:** 100% ảnh sạch của Cam B bị phán oan là ảnh mờ (False Alarm)!
2. **Bẫy lóa đèn pha (Glare):**
   * Đèn pha rọi cháy trắng 1 góc ảnh, nhưng xung quanh vẫn có viền nét.
   * ❌ **Hậu quả:** Baseline bỏ sót 100% các ca lóa đèn pha (Recall Glare = 0%)!
3. **Bẫy trời tối ban đêm:**
   * Ban đêm tự nhiên ít viền tương phản hơn ban ngày.
   * ❌ **Hậu quả:** Baseline phán bừa 75% ảnh đêm là ảnh hỏng, quá tải reviewer!

> **🗣️ Lời thoại (Phú - Data):**  
> *"Thưa thầy, đây là 3 ca lỗi điển hình mà nhóm đã chứng minh bằng ảnh trong thư mục `reports/failure_cases/`. Baseline ngây thơ dùng 1 con số cho tất cả camera và môi trường nên hoàn toàn bị bế tắc."*

---

## 🖥️ SLIDE 4: GIẢI PHÁP KỸ THUẬT CỦA NHÓM (POC PIPELINE)

### 4 Bộ cảm biến hiệu chuẩn toán học:
1. **Lỗi Mờ (Blur):** Chuẩn hóa theo camera: `lap_norm = lap / 1000` (Cam A) hoặc `lap / 250` (Cam B). Chỉ phạt khi độ nét tụt dưới 15% so với chuẩn camera.
2. **Lỗi Tối (Dark):**
   * Ban ngày: Phạt khi độ sáng trung bình `mean < 40`.
   * Ban đêm: Chỉ phạt khi tắt đèn ngúm (`mean < 15` và hơn 85% diện tích là pixel đen).
3. **Lỗi Lóa (Glare):** Quét tỷ lệ pixel cháy sáng bão hòa `sat > 0.003`.
4. **Lỗi Nén (Compression):** Đo độ chênh lệch pixel tại biên khối JPEG 8x8.

### 🛡️ Cơ chế triệt tiêu lỗi chéo (Defect Masking):
* Ảnh đen xì thì không có viền cạnh $\to$ Laplacian tự nhiên bằng 0.
* **Quy tắc code:**
  ```python
  if s_dark > 0.4:
      s_blur = 0.0  # Dập tắt lỗi mờ giả!
  ```
* Báo đúng 100% bệnh là `Dark` để chỉnh phơi sáng, tránh bắt kỹ thuật viên đi lau lens.

> **🗣️ Lời thoại (Hưng - Core):**  
> *"Các ngưỡng 1000, 250, 40, 15 được nhóm tính toán từ phân tích thống kê trên 56 ảnh tập dev. Đặc biệt, nhóm có cơ chế dập lỗi mờ giả khi ảnh bị tối đen để đảm bảo phân loại đúng bệnh."*

---

## 🖥️ SLIDE 5: KẾT QUẢ THỰC NGHIỆM ĐỐI SÁNH (BASELINE VS POC)

| Chỉ Số Đánh Giá (Metric) | Nhóm Dữ Liệu | Baseline | PoC Nhóm G01 | Mức Độ Cải Thiện |
|---|:---:|:---:|:---:|:---:|
| **Defect Recall@20 (Chỉ số chính)** | Toàn bộ ảnh | 0.5000 (10/20) | **0.8500 (17/20)** | **+70.0% vượt trội** |
| **Precision@20** | Toàn bộ ảnh | 0.5000 | **0.8500** | **+70.0% tương đối** |
| **Độ chính xác phân loại lỗi** | Toàn bộ ảnh lỗi | n/a | **0.7500** | **75.0% đúng bệnh** |
| Báo oan ban đêm (False Alarm) | Ban đêm (night) | 0.7500 (75%) | **0.2500 (25%)** | **Giảm 3 lần báo oan** |
| Báo oan chập tối (False Alarm) | Chập tối (dusk) | 0.5000 (50%) | **0.0000 (0%)** | **Sạch 100% báo oan** |
| **Thời gian chạy / 100 ảnh** | Chạy trên CPU | 0.08 s | **0.43 s** | Dưới 0.5 giây |

> **🗣️ Lời thoại (Thiên - QA):**  
> *"So với mô hình cũ chỉ tìm được 10 ảnh lỗi, thuật toán của nhóm đã tìm ra 17/20 ảnh lỗi thật, đưa Recall lên 85%. Đặc biệt dập tắt hoàn toàn báo oan lúc chập tối (0%) và giảm báo oan ban đêm xuống chỉ còn 25%."*

---

## 🖥️ SLIDE 6: GIAO DIỆN VẬN HÀNH & KẾT LUẬN

### 1. Giao diện Reviewer thực tế: Contact Sheet HTML
* File `out/poc/contact_sheet.html` hiển thị lưới 20 ảnh trực quan kèm điểm số và loại lỗi.
* Reviewer có quyền duyệt, sửa nhãn (Override), bấm **Export CSV** lưu nhật ký kiểm toán.
* Tự động sinh `decision.json`: Quyết định **REWORK** do tỷ lệ ảnh lỗi đạt 85% (> 20% ngưỡng an toàn).

### 2. Quản trị dữ liệu (Data Governance):
* **Không rò rỉ dữ liệu:** Chia split theo cảnh gốc (Scene-level split).
* **Quyền riêng tư:** 100% synthetic procedural, không PII, tuân thủ Nghị định 13/2023/NĐ-CP.
* **Toàn vẹn:** Khớp 100% mã băm SHA-256 qua `manifest.csv`.

---

## 🖥️ SLIDE 7: CÁC GIỚI HẠN MÀ GIẢI PHÁP NÀY CHƯA ĐẠT ĐƯỢC

*Phân tích thẳng thắn các điểm nghẽn kỹ thuật và ca khó còn tồn tại:*

1. **Bỏ sót lóa đèn cục bộ quá nhỏ (Local Specular Glare):**
   * *Hiện trạng:* Thuật toán tính tỷ lệ pixel bão hòa `sat > 0.003` trên toàn bộ bức ảnh.
   * *Điểm chưa đạt:* Nếu đốm lóa đèn pha chỉ nhỏ li ti (< 0.1% diện tích) nhưng rọi trúng ngay biển số xe, tỷ lệ toàn ảnh không vượt ngưỡng nên bị bỏ sót (như ca lỗi `reports/failure_cases/glare_missed.png`).
   * *Hướng khắc phục:* Bổ sung quét ô cục bộ (Patch-based scanning) hoặc mặt nạ vùng quan tâm (ROI Masking).

2. **Khoảng cách miền dữ liệu (Sim-to-Real Domain Gap):**
   * *Hiện trạng:* Toàn bộ 96 ảnh thử nghiệm là ảnh tổng hợp nhân tạo (Synthetic Procedural).
   * *Điểm chưa đạt:* Chưa kiểm nghiệm trên dữ liệu camera thực tế ngoài đường với các hiện tượng phức tạp như: nhiễu hạt cảm biến động (sensor noise), vệt nước mưa trên kính lái (wiper streaks), hoặc ánh đèn đường chớp nháy (flickering LED).
   * *Hướng khắc phục:* Mở rộng đánh giá trên các bộ dữ liệu thực tế như BDD100K hoặc ACDC.

3. **Chưa cộng dồn đa khiếm khuyết (Multi-defect Aggregation):**
   * *Hiện trạng:* Thuật toán chọn lỗi có điểm cao nhất `score = max(...)`.
   * *Điểm chưa đạt:* Nếu một bức ảnh vừa mờ nhẹ (score 0.28) vừa thiếu sáng nhẹ (score 0.28), điểm tổng vẫn chỉ là 0.28 (không vượt ngưỡng 0.3) nên bị đánh giá là ảnh sạch, dù thực tế chất lượng cộng dồn đã rất tệ.
   * *Hướng khắc phục:* Chuyển sang mô hình chấm điểm kết hợp đa yếu tố (Weighted Multi-defect Scoring).

4. **Ngưỡng cố định, chưa tự thích ứng (Dynamic Calibration):**
   * *Hiện trạng:* Các thông số Cam A = 1000, Cam B = 250 là hằng số cố định (Hardcoded) được đo đạc từ tập `dev`.
   * *Điểm chưa đạt:* Khi lắp một dòng camera mới (Cam C, Cam D) có đặc tính cảm biến khác lạ, hệ thống chưa tự học được baseline mà phải có kỹ sư phân tích lại từ đầu.
   * *Hướng khắc phục:* Xây dựng mô-đun tự học ngưỡng nền động (Online Baseline Calibration) theo luồng streaming.
