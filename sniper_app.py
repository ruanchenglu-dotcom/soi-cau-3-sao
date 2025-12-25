import streamlit as st
import pandas as pd
import re
from PIL import Image, ImageOps, ImageEnhance
import pytesseract

# --- CẤU HÌNH ---
st.set_page_config(page_title="3-Star Sniper Pro V8", page_icon="🎯", layout="wide")
st.title("🎯 Máy Tính Soi Cầu 3 Sao (Bố Cục V8)")

# --- QUẢN LÝ DỮ LIỆU ---
if 'lottery_data' not in st.session_state:
    st.session_state.lottery_data = []

if 'temp_scan_result' not in st.session_state:
    st.session_state.temp_scan_result = ""

# Biến để giữ trạng thái đã bấm phân tích chưa
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = False

# --- HÀM XỬ LÝ TEXT ---
def extract_numbers(text):
    return re.findall(r'\b\d{3}\b', text)

# ==========================================
# BỐ CỤC CHÍNH: 2 CỘT
# ==========================================
col_input, col_data = st.columns([1, 1.2]) # Cột phải rộng hơn chút để hiển thị biểu đồ đẹp

# ==========================================
# CỘT TRÁI: NHẬP DỮ LIỆU
# ==========================================
with col_input:
    st.subheader("1. Nhập Dữ Liệu")
    
    # Chia cột nhỏ để đặt nút bấm nằm ngang hàng với Radio
    c_radio, c_btn = st.columns([1.2, 1])
    
    with c_radio:
        input_method = st.radio("Chọn cách nhập:", ["📋 Copy & Dán", "📷 Quét Ảnh (OCR)"])

    # --- CÁCH 1: COPY PASTE ---
    if input_method == "📋 Copy & Dán":
        with c_btn:
            st.write("") # Căn chỉnh xuống dòng
            st.write("")
            if st.button("📥 Lưu Dữ Liệu Ngay", use_container_width=True):
                st.session_state.trigger_save_paste = True

        user_text = st.text_area("Dán kết quả (Số mới nhất ở trên):", height=150, placeholder="932\n296...")
        
        if st.session_state.get('trigger_save_paste', False):
            found = extract_numbers(user_text)
            if found:
                count = 0
                for num in reversed(found): 
                    st.session_state.lottery_data.insert(0, num)
                    count += 1
                st.success(f"Đã lưu {count} số!")
                st.session_state.trigger_save_paste = False 
                st.session_state.show_analysis = True # Tự động bật phân tích khi có dữ liệu mới
                st.rerun()

    # --- CÁCH 2: QUÉT ẢNH (OCR) ---
    elif input_method == "📷 Quét Ảnh (OCR)":
        uploaded_file = st.file_uploader("Chọn ảnh kết quả:", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            # Đưa nút QUÉT lên vị trí bên phải (cột c_btn)
            with c_btn:
                st.write("") 
                st.write("") 
                
                # Nút 1: QUÉT
                if st.button("🔍 QUÉT ẢNH NGAY", type="primary", use_container_width=True):
                    with st.spinner('Đang quét...'):
                        try:
                            # Xử lý ảnh
                            gray_image = image.convert('L')
                            enhancer = ImageEnhance.Contrast(gray_image)
                            contrast_image = enhancer.enhance(2.0)
                            bw_image = contrast_image.point(lambda x: 0 if x < 128 else 255, '1')
                            
                            # OCR config
                            my_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
                            text = pytesseract.image_to_string(bw_image, config=my_config)
                            
                            st.session_state.temp_scan_result = text 
                            st.toast("Quét xong! Kết quả hiện bên dưới 👇", icon="✅")
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

                # Nút 2: LƯU
                if st.session_state.temp_scan_result:
                    if st.button("💾 LƯU KẾT QUẢ", use_container_width=True):
                        st.session_state.trigger_save_ocr = True

            # Hiển thị ảnh và kết quả
            with st.expander("Xem ảnh gốc", expanded=False):
                st.image(image, use_container_width=True)
        
            if st.session_state.temp_scan_result:
                st.markdown("---")
                edited_text = st.text_area("Kết quả quét được (Sửa nếu sai):", 
                                         value=st.session_state.temp_scan_result, 
                                         height=150)
                
                if st.session_state.get('trigger_save_ocr', False):
                    found = extract_numbers(edited_text)
                    if found:
                        count = 0
                        for num in reversed(found):
                            st.session_state.lottery_data.insert(0, num)
                            count += 1
                        st.success(f"Đã lưu {count} kỳ quay!")
                        st.session_state.temp_scan_result = "" 
                        st.session_state.trigger_save_ocr = False
                        st.session_state.show_analysis = True # Tự động bật phân tích
                        st.rerun()

# ==========================================
# CỘT PHẢI: PHÂN TÍCH (TRÊN) & LỊCH SỬ (DƯỚI)
# ==========================================
with col_data:
    st.subheader("2. Phân Tích & Dự Đoán")
    
    # Chỉ hiện nút phân tích nếu có dữ liệu
    if len(st.session_state.lottery_data) > 0:
        
        # Nút bấm chạy phân tích (Luôn nằm trên cùng bên phải)
        if st.button("🚀 CẬP NHẬT PHÂN TÍCH", type="primary", use_container_width=True):
            st.session_state.show_analysis = True

        # --- KHU VỰC HIỂN THỊ KẾT QUẢ DỰ ĐOÁN (NẰM TRÊN) ---
        if st.session_state.show_analysis:
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
            
            st.success("### ✅ KẾT QUẢ SOI CẦU")
            
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.metric("🔥 CẦU NÓNG", f"{h_hot} - {t_hot} - {u_hot}", delta="Hay về nhất")
            with c_res2:
                st.metric("❄️ CẦU GAN", f"{h_cold} - {t_cold} - {u_cold}", delta="Lâu chưa về", delta_color="inverse")
            
            with st.expander("Xem biểu đồ tần suất chi tiết", expanded=True):
                st.bar_chart(df.apply(pd.Series.value_counts).fillna(0))
        
        st.markdown("---") # Đường kẻ phân cách
        
        # --- KHU VỰC LỊCH SỬ (NẰM DƯỚI) ---
        st.subheader("📜 Lịch Sử Kết Quả")
        
        c_hist_1, c_hist_2 = st.columns([1, 3])
        with c_hist_1:
            if st.button("🗑️ Xóa hết"):
                st.session_state.lottery_data = []
                st.session_state.show_analysis = False
                st.rerun()
        
        with c_hist_2:
            st.caption(f"Tổng cộng: {len(st.session_state.lottery_data)} kỳ quay")

        # Bảng dữ liệu
        df_history = pd.DataFrame(st.session_state.lottery_data, columns=["Kết Quả"])
        df_history.index.name = "Kỳ (0=Mới nhất)"
        st.dataframe(df_history, height=300, use_container_width=True)

    else:
        st.info("👈 Chưa có dữ liệu. Vui lòng nhập dữ liệu ở cột bên trái.")
