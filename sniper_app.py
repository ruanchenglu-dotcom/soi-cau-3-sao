import streamlit as st
import pandas as pd
import re
from PIL import Image
import pytesseract

# --- CẤU HÌNH TESSERACT (CHỈ DÀNH CHO WINDOWS) ---
# Nếu bạn đã cài Tesseract và muốn dùng tính năng quét ảnh, hãy bỏ dấu # ở dòng dưới 
# và sửa đường dẫn cho đúng với máy của bạn.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="3-Star Sniper Pro", page_icon="🎯", layout="wide")

st.title("🎯 Máy Tính Soi Cầu 3 Sao (Pro Version)")
st.markdown("Nhập dữ liệu -> Phân tích -> Lấy số đẹp.")

# --- QUẢN LÝ DỮ LIỆU (SESSION STATE) ---
if 'lottery_data' not in st.session_state:
    st.session_state.lottery_data = []

# --- HÀM XỬ LÝ TEXT ---
def extract_numbers(text):
    """Tìm tất cả các bộ 3 số (VD: 123, 456) trong văn bản"""
    # Regex tìm các cụm 3 chữ số liên tiếp
    matches = re.findall(r'\b\d{3}\b', text)
    return matches

# --- SIDEBAR: KHU VỰC NHẬP LIỆU ---
with st.sidebar:
    st.header("1. Nhập Dữ Liệu")
    
    input_method = st.radio("Chọn cách nhập:", ["📋 Copy & Dán", "📷 Quét Ảnh (OCR)"])
    
    raw_numbers = []
    
    if input_method == "📋 Copy & Dán":
        user_text = st.text_area("Dán kết quả vào đây (VD: 123 456 789...)", height=150)
        if st.button("📥 Thêm vào danh sách"):
            raw_numbers = extract_numbers(user_text)
            
    elif input_method == "📷 Quét Ảnh (OCR)":
        st.info("Yêu cầu đã cài đặt Tesseract OCR trên máy tính.")
        uploaded_file = st.file_uploader("Chọn ảnh chụp màn hình kết quả", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Ảnh đã tải lên', use_column_width=True)
            
            if st.button("🔍 Quét chữ trong ảnh"):
                try:
                    # Chuyển ảnh thành text
                    text_from_img = pytesseract.image_to_string(image)
                    st.success("Đã quét xong!")
                    st.text_area("Kết quả quét được:", text_from_img, height=100)
                    raw_numbers = extract_numbers(text_from_img)
                except Exception as e:
                    st.error(f"Lỗi OCR: {e}. Bạn đã cài Tesseract chưa?")

    # Xử lý thêm số vào database
    if raw_numbers:
        # Đảo ngược list để số mới nhất nằm trên cùng (tùy nguồn copy)
        # Giả sử copy từ web là từ mới đến cũ
        count_new = 0
        for num in raw_numbers:
            if num not in st.session_state.lottery_data: # Tránh trùng lặp
                st.session_state.lottery_data.insert(0, num) # Thêm vào đầu
                count_new += 1
        st.success(f"Đã thêm thành công {count_new} bộ số mới!")

    st.markdown("---")
    st.header("2. Quản Lý")
    
    # Nút xóa tất cả
    if st.button("🗑️ XÓA TẤT CẢ DỮ LIỆU", type="primary"):
        st.session_state.lottery_data = []
        st.rerun()

    st.metric("Tổng số kỳ đã nhập", len(st.session_state.lottery_data))

# --- MÀN HÌNH CHÍNH ---

# Hiển thị dữ liệu hiện có
if len(st.session_state.lottery_data) > 0:
    with st.expander("Xem bảng dữ liệu hiện tại", expanded=False):
        df_display = pd.DataFrame(st.session_state.lottery_data, columns=["Kết Quả"])
        st.dataframe(df_display.T, use_container_width=True) # Transpose cho dễ nhìn

    # Nút Chạy Phân Tích
    if st.button("🚀 CHẠY PHÂN TÍCH & CHỐT SỐ", type="primary", use_container_width=True):
        
        st.markdown("---")
        st.subheader("📊 Kết Quả Phân Tích")
        
        # Chuyển list thành DataFrame để tính toán
        # Tách thành 3 cột: Trăm, Chục, Đơn vị
        data_split = [[int(n[0]), int(n[1]), int(n[2])] for n in st.session_state.lottery_data]
        df = pd.DataFrame(data_split, columns=["Trăm", "Chục", "Đơn Vị"])
        
        # Hàm tìm Hot/Cold
        def get_stats(col_name):
            counts = df[col_name].value_counts().reindex(range(10), fill_value=0)
            hot = counts.idxmax()      # Số ra nhiều nhất
            cold = counts.idxmin()     # Số ra ít nhất
            return hot, cold, counts

        h_hot, h_cold, h_counts = get_stats("Trăm")
        t_hot, t_cold, t_counts = get_stats("Chục")
        u_hot, u_cold, u_counts = get_stats("Đơn Vị")
        
        # Hiển thị 3 cột biểu đồ
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("Vị trí 1: Hàng Trăm")
            st.bar_chart(h_counts, height=150)
        with col2:
            st.caption("Vị trí 2: Hàng Chục")
            st.bar_chart(t_counts, height=150)
        with col3:
            st.caption("Vị trí 3: Hàng Đơn Vị")
            st.bar_chart(u_counts, height=150)

        # --- KHU VỰC CHỐT SỐ ---
        st.markdown("### 🏆 CON SỐ NÊN MUA")
        
        final_col1, final_col2 = st.columns(2)
        
        with final_col1:
            st.success(f"🔥 **BẠCH THỦ (Theo Cầu Chạy):**")
            st.markdown(f"# {h_hot} {t_hot} {u_hot}")
            st.caption(f"Giải thích: Đây là ghép 3 số đang ra nhiều nhất tại mỗi vị trí.")
            
        with final_col2:
            st.warning(f"❄️ **NUÔI GAN (Săn Đảo Chiều):**")
            st.markdown(f"# {h_cold} {t_cold} {u_cold}")
            st.caption(f"Giải thích: Đây là ghép 3 số lâu chưa ra nhất (đánh chặn đầu).")

else:
    st.info("👈 Hãy dán dữ liệu hoặc quét ảnh ở cột bên trái để bắt đầu.")
    # Dữ liệu mẫu để user hiểu cách dùng
    st.markdown("**Ví dụ dữ liệu mẫu:**")
    st.code("452 123 889 012 556 789")