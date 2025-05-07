import os
import re

# ##########################################################
# 옵션 설정

path1 = "C:/Users/anjen/Downloads/인키노-이안/5star" # 셀렉 파일들이 위치한 폴더 경로 입력
path2 = 'C:/Users/anjen/Downloads/촬영/jpg' # 더미 jpg 파일들이 저장될 폴더 경로 입력
exc = '인키노스튜디오-' or None # 제외할 문자열 입력 # exc = None # 제외할 문자열이 없을 경우 None으로 설정
make_dummy_jpg = None # 더미 jpg 파일 생성 여부 (True/False)
file_name = "output.txt" # 저장할 파일 이름 설정
# ##########################################################

def get_file_names(product_path):
    file_names = set()
    counter = 0
    for root, _, files in os.walk(product_path):
        for file in files:
            f_name = os.path.splitext(file)[0]
            f_name = f_name.replace(exc, '')
            file_names.add(f_name)
            counter += 1
    return file_names, counter

def extract_number(value):
    match = re.search(r"\d+", value)
    return int(match.group()) if match else float('inf')

def save_sorted_filenames(file_path, sorted_data, counter):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"Jack님-미사-셀렉\n")
        f.write(f"Total files: {counter}\n")
        for name in sorted_data:
            f.write(name + "\n")
    print(f"Sorted filenames saved to {file_path}")

def create_dummy_files(file_path, sorted_data):
    for name in sorted_data:       
        dummy_file_path = os.path.join(file_path, f"{name}.jpg")
        with open(dummy_file_path, "wb") as f:
            f.write(os.urandom(1024))  # Create a dummy file of 1KB

names, counter = get_file_names(path1)
sorted_data = sorted(names, key=extract_number)
save_sorted_filenames(file_name, sorted_data, counter)
create_dummy_files(path2, sorted_data) if make_dummy_jpg else None