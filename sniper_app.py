import streamlit as st
import pandas as pd
import re
from PIL import Image, ImageOps, ImageEnhance
import pytesseract

# --- CẤU HÌNH ---
st.set_page_config(page_title="3-Star Sniper Pro V5", page_icon="🎯", layout="wide")
st.title("🎯 Máy Tính Soi Cầu 3 Sao (Logic Chuẩn V5)")
st.markdown("Quy trình: **Quét/Dán (Giữ nguyên thứ tự) -> Lưu (Cho phép trùng) -> Phân Tích**")

# --- QUẢN LÝ DỮ LIỆU ---
if 'lottery_data' not in st.session_state:
    st.session_state.lottery_data = []

if 'temp_scan_result' not in st.session_state:
    st.session_state.temp_scan_result = ""

# --- HÀM XỬ LÝ TEXT ---
def extract_numbers(text):
    # Regex tìm tất cả các cụm 3 chữ số
    return re.findall(r'\b\d{3}\b', text)

# --- GIAO DIỆN CHÍNH ---
col_input, col_data = st.columns([1, 1])

# === CỘT TRÁI: NHẬP LIỆU ===
with col_input:
    st.subheader("1. Nhập Dữ Liệu")
    input_method = st.radio("Chọn cách nhập:", ["📋 Copy & Dán", "📷 Quét Ảnh (OCR)"], horizontal=True)
    
    # --- CÁCH 1: COPY PASTE ---
    if input_method == "📋 Copy & Dán":
        user_text = st.text_area("Dán kết quả (Số mới nhất ở trên cùng):", height=150, placeholder="Ví dụ:\n932\n932\n296...")
        if st.button("📥 Lưu Dữ Liệu"):
            found = extract_numbers(user_text)
            if found:
                # LOGIC SỬA ĐỔI QUAN TRỌNG:
                # Để giữ nguyên thứ tự "Số đầu tiên trong văn bản là Số mới nhất",
                # và muốn chèn nó lên đầu danh sách (index 0).
                # Ta phải chèn ngược từ dưới lên trên vào vị trí 0.
                count = 0
                for num in reversed(found): 
                    # Đã XÓA điều kiện chặn trùng lặp (vì xổ số có thể về trùng số như 932)
                    st.session_state.lottery_data.insert(0, num)
                    count += 1
                
                st.success(f"Đã thêm {count} kỳ quay mới lên đầu danh sách!")
                st.rerun()
            else:
                st.warning("Không tìm thấy bộ 3 số nào.")

    # --- CÁCH 2: QUÉT ẢNH (OCR) ---
    elif input_method == "📷 Quét Ảnh (OCR)":
        st.info("💡 Lưu ý: Danh sách trong ảnh sẽ được giữ nguyên thứ tự khi đưa vào App.")
        uploaded_file = st.file_uploader("Chọn ảnh kết quả", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Ảnh gốc', use_container_width=True)
            
            if st.button("🔍 Bắt đầu Quét Số"):
                with st.spinner('Đang xử lý ảnh...'):
                    try:
                        # XỬ LÝ ẢNH (Khử sọc xanh, làm rõ số)
                        gray_image = image.convert('L')
                        enhancer = ImageEnhance.Contrast(gray_image)
                        contrast_image = enhancer.enhance(2.0)
                        bw_image = contrast_image.point(lambda x: 0 if x < 128 else 255, '1')
                        
                        # Cấu hình chỉ đọc số
                        my_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
                        text = pytesseract.image_to_string(bw_image, config=my_config)
                        
                        st.session_state.temp_scan_result = text 
                        st.success("Quét xong! Kiểm tra thứ tự bên dưới.")
                    except Exception as e:
                        st.error(f"Lỗi OCR: {e}")

        # KHU VỰC SỬA LỖI & LƯU
        if st.session_state.temp_scan_result:
            st.markdown("---")
            st.markdown("🔽 **Kết quả (Số đầu tiên sẽ là Mới Nhất):**")
            
            edited_text = st.text_area("Chỉnh sửa:", 
                                     value=st.session_state.temp_scan_result, 
                                     height=150)
            
            if st.button("💾 XÁC NHẬN & LƯU (LÊN ĐẦU DANH SÁCH)"):
                found = extract_numbers(edited_text)
                if found:
                    count = 0
                    # LOGIC SỬA ĐỔI: Chèn ngược để giữ đúng thứ tự ảnh
                    for num in reversed(found):
                        st.session_state.lottery_data.insert(0, num)
                        count += 1
                    
                    st.success(f"Đã lưu {count} kỳ quay vào lịch sử!")
                    st.session_state.temp_scan_result = ""
                    st.rerun()
                else:
                    st.warning("Không tìm thấy số nào.")

# === CỘT PHẢI: PHÂN TÍCH ===
with col_data:
    st.subheader("2. Lịch Sử & Phân Tích")
    
    if st.button("🗑️ Xóa tất cả dữ liệu"):
        st.session_state.lottery_data = []
        st.rerun()
        
    if len(st.session_state.lottery_data) > 0:
        st.info(f"Đang có {len(st.session_state.lottery_data)} kỳ quay.")
        
        # HIỂN THỊ BẢNG (Đánh số thứ tự kỳ)
        # Tạo DataFrame và Reset Index để có cột số thứ tự (0 là mới nhất)
        df_history = pd.DataFrame(st.session_state.lottery_data, columns=["Kết Quả"])
        df_history.index.name = "Kỳ (0=Mới nhất)"
        st.dataframe(df_history, height=250, use_container_width=True)
        
        st.markdown("---")
        # NÚT CHẠY PHÂN TÍCH
        if st.button("🚀 PHÂN TÍCH NGAY", type="primary", use_container_width=True):
            
            # Tách số
            data_split = [[int(n[0]), int(n[1]), int(n[2])] for n in st.session_state.lottery_data]
            df = pd.DataFrame(data_split, columns=["Trăm", "Chục", "Đơn Vị"])
            
            # Hàm tìm Hot/Cold
            def get_stats(col):
                counts = df[col].value_counts().reindex(range(10), fill_value=0)
                hot = counts.idxmax()
                cold = counts.idxmin()
                return hot, cold, counts

            h_hot, h_cold, h_counts = get_stats("Trăm")
            t_hot, t_cold, t_counts = get_stats("Chục")
            u_hot, u_cold, u_counts = get_stats("Đơn Vị")
            
            st.success("### ✅ DỰ ĐOÁN KẾT QUẢ")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("🔥 CẦU NÓNG (Hay về)", f"{h_hot}{t_hot}{u_hot}")
                st.caption("Ghép 3 số ra nhiều nhất")
            with c2:
                st.metric("❄️ CẦU GAN (Lâu chưa về)", f"{h_cold}{t_cold}{u_cold}")
                st.caption("Ghép 3 số 'lì lợm' nhất")
                
            st.write("---")
            st.write("**Biểu đồ tần suất xuất hiện (0-9):**")
            st.bar_chart(df.apply(pd.Series.value_counts).fillna(0))
    else:
        st.warning("👈 Dữ liệu trống.")
