# --- TÌM ĐOẠN CODE CŨ NÀY ---
# text = pytesseract.image_to_string(image)

# --- VÀ THAY BẰNG ĐOẠN MỚI NÀY ---
# 1. Chuyển ảnh sang đen trắng (Grayscale) để máy dễ đọc hơn
gray_image = image.convert('L') 

# 2. Cấu hình "Thần thánh":
# --psm 6: Coi cả cục văn bản là một khối thống nhất (xử lý tốt cột dọc)
# -c tessedit_char_whitelist=0123456789: QUAN TRỌNG NHẤT -> Chỉ cho phép nhận diện số từ 0 đến 9
custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'

# 3. Quét với cấu hình mới
text = pytesseract.image_to_string(gray_image, config=custom_config)
