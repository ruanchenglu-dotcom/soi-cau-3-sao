import streamlit as st
import pandas as pd
import re
from PIL import Image, ImageOps, ImageEnhance
import pytesseract

# --- CẤU HÌNH ---
st.set_page_config(page_title="3-Star Sniper Pro V7", page_icon="🎯", layout="wide")
st.title("🎯 Máy Tính Soi Cầu 3 Sao (Giao Diện V7)")

# --- QUẢN LÝ DỮ LIỆU ---
if 'lottery_data' not in st.session_state:
    st.session_state.lottery_data = []

if 'temp_scan_result' not in st.session_state:
    st.session_state.temp_scan_result = ""

# --- HÀM XỬ LÝ TEXT ---
def extract_numbers(text):
    return re.findall(r'\b\d{3}\b', text)

# ==========================================
# PHẦN 1: NHẬP DỮ LIỆU (NẰM TRÊN CÙNG)
# ==========================================
st.subheader("1. Nhập Dữ Liệu")

# Chia cột để đặt nút bấm nằm ngang hàng với Radio chọn
c_radio, c_btn = st.columns([1.5, 1])

with c_radio:
    input_method = st.radio("Chọn cách nhập:", ["📋 Copy & Dán", "📷 Quét Ảnh (OCR)"])

# --- CÁCH 1: COPY PASTE ---
if input_method == "📋 Copy & Dán":
    with c_btn:
        st.write("") # Căn chỉnh
        st.write("")
        if st.button("📥 Lưu Dữ Liệu Ngay", use_container_width=True):
            st.session_state.trigger_save_paste = True

    # Ô nhập liệu nằm dưới các nút điều khiển
    user_text = st.text_area("Dán kết quả (Số mới nhất ở trên):", height=100, placeholder="932\n296...")
    
    if st.session_state.get('trigger_save_paste', False):
        found = extract_numbers(user_text)
        if found:
            count = 0
            for num in reversed(found): 
                st.session_state.lottery_data.insert(0, num)
                count += 1
            st.success(f"Đã lưu {count} số!")
            st.session_state.trigger_save_paste = False 
            st.rerun()

# --- CÁCH 2: QUÉT ẢNH (OCR) ---
elif input_method == "📷 Quét Ảnh (OCR)":
    # Upload file nằm dưới radio, nhưng trên nút quét (để nút quét hiện ra sau khi chọn ảnh)
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

            # Nút 2: LƯU (Chỉ hiện khi đã quét có kết quả)
            if st.session_state.temp_scan_result:
                if st.button("💾 LƯU KẾT QUẢ", use_container_width=True):
                    st.session_state.trigger_save_ocr = True

        # Hiển thị ảnh (Bên trái) và Kết quả text (Bên phải)
        c_img, c_text = st.columns(2)
        with c_img:
            with st.expander("Xem ảnh gốc", expanded=True):
                st.image(image, use_container_width=True)
        
        with c_text:
            if st.session_state.temp_scan_result:
                edited_text = st.text_area("Kết quả quét được (Sửa nếu sai):", 
                                         value=st.session_state.temp_scan_result, 
                                         height=200)
                
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
                        st.rerun()

st.markdown("---") 

# ==========================================
# PHẦN 2: BẢNG KẾT QUẢ & PHÂN TÍCH (DỜI XUỐNG DƯỚI CÙNG)
# ==========================================
st.subheader("2. Lịch Sử & Phân Tích")

# Thanh công cụ cho bảng (Nút xóa + Info)
c_tools_1, c_tools_2 = st.columns([1, 4])
with c_tools_1:
    if st.button("🗑️ Xóa tất cả dữ liệu", type="secondary"):
        st.session_state.lottery_data = []
        st.rerun()

if len(st.session_state.lottery_data) > 0:
    # HIỂN THỊ BẢNG (FULL WIDTH)
    df_history = pd.DataFrame(st.session_state.lottery_data, columns=["Kết Quả"])
    df_history.index.name = "Kỳ (0=Mới nhất)"
    
    # Dùng use_container_width=True để bảng tràn màn hình
    st.dataframe(df_history.T, use_container_width=True) 
    st.caption("Bảng hiển thị ngang cho dễ nhìn.")

    st.markdown("### 📊 Kết Quả Phân Tích")
    
    # Nút Phân Tích To
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
        
        # Hiển thị kết quả to rõ
        st.success("### ✅ DỰ ĐOÁN CHỐT SỐ")
        
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.metric("🔥 CẦU NÓNG (Hay về)", f"{h_hot} - {t_hot} - {u_hot}")
        with c_res2:
            st.metric("❄️ CẦU GAN (Lâu chưa về)", f"{h_cold} - {t_cold} - {u_cold}")
            
        st.write("**Biểu đồ tần suất:**")
        st.bar_chart(df.apply(pd.Series.value_counts).fillna(0))
else:
    st.info("👈 Chưa có dữ liệu. Hãy nhập ở trên.")
