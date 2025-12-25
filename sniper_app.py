import streamlit as st
import pandas as pd
import re
from PIL import Image, ImageOps, ImageEnhance
import pytesseract

# --- CẤU HÌNH ---
st.set_page_config(page_title="3-Star Sniper Pro V4", page_icon="🎯", layout="wide")
st.title("🎯 Máy Tính Soi Cầu 3 Sao (Bản Chuẩn V4)")
st.markdown("Quy trình: **Nhập liệu (Quét/Dán) -> Kiểm tra -> Lưu -> Phân Tích**")

# --- QUẢN LÝ DỮ LIỆU ---
if 'lottery_data' not in st.session_state:
    st.session_state.lottery_data = []

if 'temp_scan_result' not in st.session_state:
    st.session_state.temp_scan_result = ""

# --- HÀM XỬ LÝ TEXT ---
def extract_numbers(text):
    # Regex tìm tất cả các cụm 3 chữ số (VD: 932, 296...)
    return re.findall(r'\b\d{3}\b', text)

# --- GIAO DIỆN CHÍNH ---
col_input, col_data = st.columns([1, 1])

# === CỘT TRÁI: NHẬP LIỆU ===
with col_input:
    st.subheader("1. Nhập Dữ Liệu")
    input_method = st.radio("Chọn cách nhập:", ["📋 Copy & Dán", "📷 Quét Ảnh (OCR)"], horizontal=True)
    
    # --- CÁCH 1: COPY PASTE ---
    if input_method == "📋 Copy & Dán":
        user_text = st.text_area("Dán kết quả vào đây:", height=150, placeholder="Ví dụ: 932 296 302...")
        if st.button("📥 Lưu Dữ Liệu"):
            found = extract_numbers(user_text)
            if found:
                count = 0
                for num in found:
                    if num not in st.session_state.lottery_data:
                        st.session_state.lottery_data.insert(0, num)
                        count += 1
                st.success(f"Đã lưu thành công {count} số mới!")
                st.rerun()
            else:
                st.warning("Không tìm thấy bộ 3 số nào hợp lệ.")

    # --- CÁCH 2: QUÉT ẢNH (OCR) ---
    elif input_method == "📷 Quét Ảnh (OCR)":
        st.info("💡 Mẹo: Ảnh nên chụp thẳng, rõ nét các con số.")
        uploaded_file = st.file_uploader("Chọn ảnh kết quả (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file is not None:
            # Mở ảnh
            image = Image.open(uploaded_file)
            st.image(image, caption='Ảnh gốc', use_container_width=True)
            
            if st.button("🔍 Bắt đầu Quét Số"):
                with st.spinner('Đang xử lý ảnh...'):
                    try:
                        # --- BƯỚC XỬ LÝ ẢNH CAO CẤP ---
                        # 1. Chuyển sang ảnh xám (Grayscale)
                        gray_image = image.convert('L')
                        
                        # 2. Tăng độ tương phản để loại bỏ sọc xanh nhạt
                        enhancer = ImageEnhance.Contrast(gray_image)
                        contrast_image = enhancer.enhance(2.0) # Tăng gấp đôi tương phản
                        
                        # 3. Chuyển thành đen trắng tuyệt đối (Binarization)
                        # Những điểm ảnh sáng (sọc xanh/nền trắng) -> Thành trắng tinh
                        # Những điểm ảnh tối (số đen) -> Thành đen tuyền
                        bw_image = contrast_image.point(lambda x: 0 if x < 128 else 255, '1')
                        
                        # Hiển thị ảnh sau khi xử lý để user biết máy nhìn thấy gì
                        st.caption("Ảnh sau khi máy tính xử lý (Đen trắng):")
                        st.image(bw_image, use_container_width=True)

                        # 4. Cấu hình Tesseract (Chỉ đọc số)
                        # --psm 6: Coi như một cột văn bản thống nhất
                        # whitelist: Chỉ cho phép số 0-9
                        my_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
                        
                        # 5. Đọc ảnh
                        text = pytesseract.image_to_string(bw_image, config=my_config)
                        
                        # Lưu vào biến tạm
                        st.session_state.temp_scan_result = text 
                        st.success("Đã quét xong! Hãy kiểm tra và bấm Lưu bên dưới.")
                        
                    except Exception as e:
                        st.error(f"Lỗi: {e}. (Hãy chắc chắn bạn đã tạo file packages.txt trên GitHub)")

        # KHU VỰC HIỆN KẾT QUẢ ĐỂ SỬA
        if st.session_state.temp_scan_result:
            st.markdown("---")
            st.markdown("🔽 **Kết quả máy đọc được (Bạn hãy sửa lại nếu sai):**")
            
            edited_text = st.text_area("Chỉnh sửa:", 
                                     value=st.session_state.temp_scan_result, 
                                     height=150)
            
            if st.button("💾 XÁC NHẬN & LƯU VÀO LỊCH SỬ"):
                found = extract_numbers(edited_text)
                if found:
                    new_count = 0
                    # Đảo ngược list found để số trên cùng (mới nhất) được thêm vào đầu danh sách
                    for num in found: 
                        if num not in st.session_state.lottery_data:
                            st.session_state.lottery_data.insert(0, num)
                            new_count += 1
                    
                    st.success(f"Đã thêm {new_count} số vào lịch sử!")
                    st.session_state.temp_scan_result = "" # Xóa tạm
                    st.rerun()
                else:
                    st.warning("Không tìm thấy số nào. Hãy kiểm tra lại phần văn bản bên trên.")

# === CỘT PHẢI: PHÂN TÍCH ===
with col_data:
    st.subheader("2. Lịch Sử & Phân Tích")
    
    # Nút xóa
    if st.button("🗑️ Xóa tất cả dữ liệu"):
        st.session_state.lottery_data = []
        st.rerun()
        
    # Hiển thị bảng dữ liệu
    if len(st.session_state.lottery_data) > 0:
        st.info(f"Đang có {len(st.session_state.lottery_data)} kỳ quay trong bộ nhớ.")
        
        # Bảng hiển thị
        df_history = pd.DataFrame(st.session_state.lottery_data, columns=["Kết Quả"])
        st.dataframe(df_history, height=200, use_container_width=True)
        
        st.markdown("---")
        # NÚT CHẠY PHÂN TÍCH
        if st.button("🚀 PHÂN TÍCH NGAY", type="primary", use_container_width=True):
            
            # Tách số thành 3 cột
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
            
            st.success("### ✅ KẾT QUẢ DỰ ĐOÁN")
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric("🔥 CẦU NÓNG (Nên theo)", f"{h_hot} - {t_hot} - {u_hot}")
                st.caption("Các số đang ra nhiều nhất ở từng vị trí")
            with col_res2:
                st.metric("❄️ CẦU GAN (Nuôi)", f"{h_cold} - {t_cold} - {u_cold}")
                st.caption("Các số lâu chưa ra nhất")
                
            st.markdown("**Biểu đồ tần suất:**")
            st.bar_chart(df.apply(pd.Series.value_counts).fillna(0))
            
    else:
        st.warning("👈 Dữ liệu trống. Hãy nhập số liệu ở cột bên trái.")
