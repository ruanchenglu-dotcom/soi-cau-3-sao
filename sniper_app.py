import streamlit as st
import pandas as pd
import re
from PIL import Image
import pytesseract

# --- CẤU HÌNH ---
st.set_page_config(page_title="3-Star Sniper Pro V2", page_icon="🎯", layout="wide")

st.title("🎯 Máy Tính Soi Cầu 3 Sao (Bản Chuẩn V2)")
st.markdown("Quy trình: **Quét Ảnh -> Kiểm Tra & Lưu -> Phân Tích**")

# --- QUẢN LÝ DỮ LIỆU ---
if 'lottery_data' not in st.session_state:
    st.session_state.lottery_data = []

# Biến tạm để lưu kết quả quét được nhưng chưa bấm lưu
if 'temp_scan_result' not in st.session_state:
    st.session_state.temp_scan_result = ""

# --- HÀM XỬ LÝ TEXT ---
def extract_numbers(text):
    """Tìm tất cả các bộ 3 số (VD: 123, 456)"""
    return re.findall(r'\b\d{3}\b', text)

# --- KHU VỰC 1: NHẬP LIỆU (BÊN TRÁI) ---
col_input, col_data = st.columns([1, 1])

with col_input:
    st.subheader("1. Nhập Dữ Liệu")
    input_method = st.radio("Chọn cách nhập:", ["📋 Copy & Dán", "📷 Quét Ảnh (OCR)"], horizontal=True)
    
    # --- CÁCH 1: COPY PASTE ---
    if input_method == "📋 Copy & Dán":
        user_text = st.text_area("Dán kết quả vào đây:", height=150, placeholder="Ví dụ: 123 456 789...")
        if st.button("📥 Lưu Dữ Liệu Này"):
            found = extract_numbers(user_text)
            if found:
                # Thêm vào lịch sử (đảo ngược để mới nhất lên đầu)
                new_count = 0
                for num in found:
                    if num not in st.session_state.lottery_data:
                        st.session_state.lottery_data.insert(0, num)
                        new_count += 1
                st.success(f"Đã lưu thành công {new_count} số mới!")
            else:
                st.warning("Không tìm thấy bộ 3 số nào hợp lệ.")

    # --- CÁCH 2: QUÉT ẢNH (OCR) ---
    elif input_method == "📷 Quét Ảnh (OCR)":
        uploaded_file = st.file_uploader("Chọn ảnh kết quả", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Ảnh đã tải lên', use_column_width=True)
            
            # Nút bắt đầu quét
            if st.button("🔍 Bắt đầu Quét Chữ"):
                with st.spinner('Đang đọc ảnh...'):
                    try:
                        # 1. Thực hiện OCR
                        text = pytesseract.image_to_string(image)
                        # 2. Lưu vào biến tạm để hiển thị ở bước sau
                        st.session_state.temp_scan_result = text 
                        st.success("Quét xong! Hãy kiểm tra kết quả bên dưới.")
                    except Exception as e:
                        st.error(f"Lỗi: {e}. Bạn chưa cài đặt thư viện OCR trên server.")

        # HIỂN THỊ KẾT QUẢ QUÉT ĐỂ SỬA (QUAN TRỌNG)
        if st.session_state.temp_scan_result:
            st.markdown("---")
            st.write("🔽 **Kết quả quét được (Bạn có thể sửa nếu máy đọc sai):**")
            
            # Cho phép người dùng sửa trực tiếp vào ô này
            edited_text = st.text_area("Chỉnh sửa nội dung quét:", 
                                     value=st.session_state.temp_scan_result, 
                                     height=100)
            
            # Nút Lưu chính thức
            if st.button("💾 XÁC NHẬN & LƯU VÀO LỊCH SỬ"):
                found = extract_numbers(edited_text)
                if found:
                    new_count = 0
                    for num in found:
                        if num not in st.session_state.lottery_data:
                            st.session_state.lottery_data.insert(0, num)
                            new_count += 1
                    st.success(f"Đã lưu {new_count} số vào lịch sử! Hãy qua bên phải để phân tích.")
                    # Xóa biến tạm để dọn dẹp màn hình
                    st.session_state.temp_scan_result = ""
                    st.rerun() # Tải lại trang để cập nhật bảng
                else:
                    st.warning("Không tìm thấy số nào trong văn bản trên.")

# --- KHU VỰC 2: LỊCH SỬ & PHÂN TÍCH (BÊN PHẢI) ---
with col_data:
    st.subheader("2. Lịch Sử & Phân Tích")
    
    # Hiển thị nút xóa
    if st.button("🗑️ Xóa tất cả dữ liệu"):
        st.session_state.lottery_data = []
        st.rerun()
        
    # Hiển thị bảng dữ liệu
    if len(st.session_state.lottery_data) > 0:
        st.info(f"Đang có {len(st.session_state.lottery_data)} kỳ quay trong bộ nhớ.")
        
        # Tạo bảng cuộn được
        df_history = pd.DataFrame(st.session_state.lottery_data, columns=["Kết Quả"])
        st.dataframe(df_history, height=200, use_container_width=True)
        
        st.markdown("---")
        # NÚT CHẠY PHÂN TÍCH
        if st.button("🚀 CHẠY PHÂN TÍCH NGAY", type="primary", use_container_width=True):
            
            # --- LOGIC PHÂN TÍCH ---
            data_split = [[int(n[0]), int(n[1]), int(n[2])] for n in st.session_state.lottery_data]
            df = pd.DataFrame(data_split, columns=["Trăm", "Chục", "Đơn Vị"])
            
            def get_hot_cold(col):
                counts = df[col].value_counts().reindex(range(10), fill_value=0)
                return counts.idxmax(), counts.idxmin() # Trả về số Nóng nhất và Lạnh nhất

            h_hot, h_cold = get_hot_cold("Trăm")
            t_hot, t_cold = get_hot_cold("Chục")
            u_hot, u_cold = get_hot_cold("Đơn Vị")
            
            st.success("### ✅ KẾT QUẢ SOI CẦU")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("🔥 CẦU NÓNG (Nên mua)", f"{h_hot}{t_hot}{u_hot}")
                st.caption("Ghép từ các số ra nhiều nhất")
            with c2:
                st.metric("❄️ CẦU GAN (Nuôi)", f"{h_cold}{t_cold}{u_cold}")
                st.caption("Ghép từ các số lâu chưa ra")
                
            st.bar_chart(df.apply(pd.Series.value_counts).fillna(0))
            
    else:
        st.warning("👈 Dữ liệu trống. Hãy nhập hoặc quét ảnh ở bên trái trước.")
