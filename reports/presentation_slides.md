# Slide Thuyết Trình: Track T02 · Raw QC Triage Pipeline

> **Tài liệu chuẩn bị thuyết trình nhóm G01 — Field-to-Release PoC**  
> **Chủ đề:** Raw QC Triage: Xếp Hạng & Lọc Khiếm Khuyết Ảnh Thô Cho Xe Tự Hành  
> **File slide trình chiếu trực quan (HTML):** [`reports/presentation_slides.html`](file:///D:/CODE/TrainAI/lab/K5-L2-DAY06-HoangSyKhiem-2A202603244-DataGovernanceAndPrivacy/reports/presentation_slides.html)

---

## 🖥️ SLIDE 1: GIỚI THIỆU ĐỀ TÀI & ĐỘI NGŨ THỰC HIỆN

### Tiêu đề đề tài:
**Raw QC Triage: Tự Động Phân Loại & Lọc Khiếm Khuyết Ảnh Thô (Track T02)**  
*Tối ưu hóa quy trình Human-in-the-loop dưới ngân sách cứng $B = 20$ ảnh cho xe tự hành & camera thông minh.*

### Đội ngũ thành viên (Nhóm G01):
1. **Hoàng Sỹ Khiêm (Lead / Integrator / Core):** Kiến trúc pipeline 5 bước, thuật toán hiệu chuẩn camera & lighting, tích hợp và điều phối git. *(Người trình bày chính)*
2. **Nguyễn Đình Phú (Data & Baseline Engineer):** Khám phá dữ liệu (EDA), xây dựng mô hình baseline và trích xuất bằng chứng ca lỗi.
3. **Nguyễn Khải Hưng (Core Algorithm Engineer):** Xây dựng docstrings kỹ thuật và mô hình hóa công thức toán học cho các defect scores.
4. **Trần Đức Thiên (QA & Metrics Lead):** Thiết kế bộ kiểm thử biên (Edge-case tests), đo lường chỉ số Recall/Precision.
5. **Lê Hoàng Đức (Human Reviewer & Reporting):** Thẩm định hàng đợi reviewer (Review Queue), hoàn thiện báo cáo và hồ sơ bàn giao.

> **💡 Lời thoại gợi ý khi mở đầu:**  
> *"Kính thưa thầy, dự án của nhóm em giải quyết bài toán cốt tử của thị giác máy tính: 'Rác vào thì rác ra'. Chúng em xây dựng một bộ lọc 5 bước gọn nhẹ, tự động phát hiện và bốc trúng 85% ảnh hỏng cho người duyệt chỉ trong 0.43 giây mà không cần đầu tư cụm GPU đắt đỏ."*

---

## 🖥️ SLIDE 2: BỐI CẢNH THỰC TẾ & ĐIỂM NGHẼN NHÂN LỰC

### 1. Sự cố dữ liệu (Garbage In $\to$ Garbage Out):
* Đội xe tự hành thu thập hàng trăm ngàn frame ảnh mỗi ngày ngoài đường phố.
* Ảnh liên tục dính lỗi vật lý: **Mờ do xe rung/mưa (Blur)**, **Lóa đèn pha (Glare)**, **Tối đen lúc nửa đêm (Dark)**, hoặc **Vỡ nén mạng (Compression)**.
* Nếu đưa ảnh hỏng vào huấn luyện hoặc nhận diện thời gian thực $\to$ Model AI nhận diện sai người đi bộ, gây tai nạn nghiêm trọng.

### 2. Điểm nghẽn nhân lực (Human Bottleneck):
* Không thể thuê người ngồi soi thủ công 1.000.000 ảnh/ngày.
* Đội ngũ thẩm định (Reviewer) chỉ có sức duyệt tối đa **$B = 20$ ảnh cho mỗi batch kiểm tra**.

### 3. Quy tắc nghiệp vụ ra quyết định (Business Decision Rules):
* **GO (`QC_TRIAGE_PASSED`):** Nếu tỷ lệ ảnh hỏng trong batch $\le 20\% \implies$ Đạt chuẩn, giải phóng dữ liệu sang pipeline dán nhãn.
* **REWORK (`EXCESSIVE_DEFECTS`):** Nếu tỷ lệ ảnh hỏng $> 20\% \implies$ Chặn phát hành, yêu cầu đội xe lau lại cảm biến và chụp lại (recapture).

> **💡 Lời thoại gợi ý:**  
> *"Reviewer chỉ có mắt soi 20 tấm. Nếu thuật toán ngây thơ chọn bừa 20 tấm bình thường thì 20 tấm lỗi lọt vào model AI sẽ gây tai nạn chết người. Vì vậy bài toán này là tối ưu độ phủ lỗi (Recall) trong ngân sách đúng 20 ảnh."*

---

## 🖥️ SLIDE 3: VÌ SAO THUẬT TOÁN BASELINE THẤT BẠI?

*Mô hình baseline dùng 1 ngưỡng phương sai Laplacian toàn cục duy nhất, dẫn đến 3 cái bẫy chết người:*

1. **Bẫy phần cứng Camera:**  
   * Cam A dùng kính xịn sắc nét (Laplacian ~1000).  
   * Cam B dùng kính quang học mềm giá rẻ (Laplacian ~250).  
   * ❌ **Hậu quả:** 100% ảnh sạch của Cam B bị phán oan là ảnh mờ (False Alarm) vì dùng chung một thước đo!
2. **Bẫy lóa đèn pha cục bộ (Local Glare):**  
   * Đèn pha ô tô chiếu thẳng làm cháy trắng một góc ảnh, nhưng xung quanh đường nét vẫn nét.  
   * ❌ **Hậu quả:** Phương sai Laplacian vẫn cao $\implies$ Baseline bỏ sót **100% các ca lóa** (Recall Glare = 0%)!
3. **Bẫy trời tối ban đêm:**  
   * Ban đêm tự nhiên ít chi tiết viền hơn ban ngày, điểm nét tụt tự nhiên.  
   * ❌ **Hậu quả:** Baseline phán bừa **75% ảnh đêm** là ảnh hỏng, làm quá tải đội ngũ review.

> **💡 Lời thoại gợi ý:**  
> *"Thưa thầy, đây chính là 3 ca lỗi kinh điển mà nhóm Phú đã tìm ra và lưu bằng chứng trong `reports/failure_cases/`. Thuật toán cũ chỉ đo 1 chiều nên hoàn toàn 'mù' trước sự khác biệt phần cứng và ánh sáng môi trường."*

---

## 🖥️ SLIDE 4: KIẾN TRÚC & GIẢI PHÁP ĐỀ XUẤT (POC PIPELINE)

*Nhóm xây dựng quy trình 5 bước chuẩn hóa (`Load -> Process -> Rank -> Review -> Decide`):*

### 4 Bộ cảm biến hiệu chuẩn toán học:
1. **Chuẩn hóa độ nét theo camera (Blur):**  
   $$\text{lap\_norm} = \frac{\text{lap}}{\text{baseline}} \quad (\text{Cam A} = 1000, \text{Cam B} = 250)$$  
   *Chỉ phạt khi độ nét tụt $< 15\%$ so với độ nét chuẩn của camera đó.*
2. **Hiệu chuẩn theo môi trường (Dark):**  
   * Ban ngày: $mean < 40$.  
   * Ban đêm: Chỉ báo lỗi khi tắt đèn tối thui ($mean < 15$ VÀ $> 85\%$ diện tích là pixel đen xì).
3. **Bản đồ bão hòa pixel (Glare):**  
   * Quét tỷ lệ pixel bão hòa cháy sáng $sat > 0.003$ để tóm sống đốm lóa đèn pha.
4. **Đo bước nhảy biên khối (Compression):**  
   * So sánh độ biến thiên tại biên khối $8\times 8$ so với trong lòng khối.

### 🛡️ Cơ chế triệt tiêu lỗi chéo (Defect Suppression):
* Một tấm ảnh đen kịt thì không có viền $\to$ Điểm nét tụt về 0.
* **Quy tắc:** Nếu điểm Dark $> 0.4 \implies$ Ép điểm Blur $= 0.0$. Hệ thống báo đúng 100% bệnh gốc là `dark` thay vì phán nhầm là mờ!

> **💡 Lời thoại gợi ý:**  
> *"Mọi con số ngưỡng 1000, 250, 40, 15 đều được nhóm ước lượng thực nghiệm (EDA) từ 56 ảnh tập `dev`, tuyệt đối không dùng nhãn tập eval để bảo đảm nguyên tắc khoa học dữ liệu."*

---

## 🖥️ SLIDE 5: KẾT QUẢ THỰC NGHIỆM ĐỐI SÁNH (BENCHMARK)

*Đánh giá trên cùng tập testset chuẩn (40 ảnh split eval, Seed 42, Budget $B = 20$):*

| Chỉ Số Đo Lường (Metric) | Slice | Baseline | PoC Nhóm G01 | Mức Độ Cải Thiện (Δ) | Ý Nghĩa Thực Tế |
|---|:---:|:---:|:---:|:---:|---|
| **Defect Recall@20 (Chỉ số chính)** | all | 0.5000 | **0.8500** | **+70.0%** | Bắt trúng 17/20 ảnh lỗi (cũ chỉ bắt được 10) |
| **Precision@20** | all | 0.5000 | **0.8500** | **+70.0%** | Hàng đợi 20 ảnh chứa tới 85% là lỗi thật |
| **Độ chính xác phân loại lỗi** | all | n/a | **0.7500** | **75% đúng bệnh** | Báo đúng chính xác loại mờ, lóa, tối |
| Báo oan ban đêm (False Alarm) | night | 0.7500 | **0.2500** | **-66.7%** | Giảm 3 lần tình trạng báo oan ban đêm |
| Báo oan chập tối (False Alarm) | dusk | 0.5000 | **0.0000** | **-100%** | Sạch hoàn toàn báo oan lúc chập tối |
| **Thời gian thực thi / 100 ảnh** | all | 0.08 s | **0.43 s** | **< 0.5 giây** | Xử lý siêu tốc trên CPU thường, offline |

> **💡 Lời thoại gợi ý:**  
> *"Thưa thầy, chúng em đã tăng tỷ lệ vớt lỗi từ 50% lên 85%, đồng thời dập tắt hoàn toàn báo oan lúc chập tối (0%) và giảm báo oan ban đêm xuống chỉ còn 25%."*

---

## 🖥️ SLIDE 6: GIAO DIỆN VẬN HÀNH & QUẢN TRỊ DỮ LIỆU (GOVERNANCE)

### 1. Giao diện bàn làm việc HTML Contact Sheet:
* File `out/poc/contact_sheet.html` hiển thị trực quan 20 ảnh nghi ngờ nhất theo dạng lưới $4\times 5$.
* Reviewer có thể xem ảnh, đối chiếu điểm lỗi, ghi đè nhãn (Override) và bấm **Export CSV** để lưu nhật ký kiểm toán (`audit_log.jsonl`).
* Tự động xuất `out/poc/decision.json` thông báo quyết định GO / REWORK kèm mã lý do rõ ràng.

### 2. Tuân thủ Data Governance & Đạo đức AI:
* **Chống rò rỉ dữ liệu (Anti Data-Leakage):** Chia split dev/eval theo cảnh gốc (Scene-level split), đảm bảo ảnh của cùng 1 cảnh không bao giờ vừa nằm ở dev vừa nằm ở eval.
* **Bảo vệ quyền riêng tư (Privacy-by-Design):** Dữ liệu 100% synthetic procedural, tuyệt đối không có khuôn mặt hay biển số người thật, tuân thủ Nghị định 13/2023/NĐ-CP và Luật Bảo vệ dữ liệu cá nhân.
* **Toàn vẹn dữ liệu (Data Integrity):** Kiểm tra đối chiếu 100% hash SHA-256 qua `manifest.csv`.

> **💡 Lời kết khi kết thúc trình bày:**  
> *"Dự án PoC T02 của nhóm G01 không chỉ là một thuật toán xử lý ảnh đơn thuần, mà là một quy trình Data Governance hoàn chỉnh từ khâu thu thập thô đến khi ra quyết định phát hành an toàn. Nhóm em xin chân thành cảm ơn thầy và hội đồng!"*
