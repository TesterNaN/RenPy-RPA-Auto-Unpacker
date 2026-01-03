import os
import zlib
import pickle

# ========== 配置区 ==========
RPA_FILE = "new_archive.rpa"      # RPA文件路径
ZIP_FILE = "new_archive.zip"      # 数据文件路径
OUTPUT_DIR = "extracted"  # 输出目录
# ============================

def correct_extract():
    print("=" * 60)
    print("黄莓C HuangmeiC RPAv3 解包脚本")
    print("=" * 60)
    
    # 1. 读取索引
    print("正在读取索引...")
    with open(RPA_FILE, 'rb') as f:
        header = f.read(40)
        key = int(header[25:33], 16)
        print(f"XOR密钥: 0x{key:08x}")
        
        compressed = f.read()
        decompressed = zlib.decompress(compressed)
        raw_index = pickle.loads(decompressed)
    
    total_files = len(raw_index)
    print(f"找到 {total_files} 个文件")
    
    # 2. 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 3. 提取文件
    print("正在提取文件...")
    success = 0
    
    with open(ZIP_FILE, 'rb') as data_file:
        for filename, entries in raw_index.items():
            try:
                entry = entries[0]  # 每个文件只有一个条目
                
                if len(entry) == 2:
                    enc_offset, enc_length = entry
                    start_bytes = b''
                else:
                    enc_offset, enc_length, start_bytes = entry
                
                # 正确的解密公式：先XOR，再减33
                offset = (enc_offset ^ key) - 33
                length = enc_length ^ key
                
                # 创建文件路径
                out_path = os.path.join(OUTPUT_DIR, filename)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                
                # 读取数据
                data_file.seek(offset)
                data = data_file.read(length)
                
                # 如果有起始字节，添加到前面
                if start_bytes:
                    data = start_bytes + data
                
                # 写入文件
                with open(out_path, 'wb') as out_file:
                    out_file.write(data)
                
                success += 1
                
                # 每100个文件显示进度
                if success % 100 == 0:
                    print(f"进度: {success}/{total_files}")
                    
            except Exception as e:
                print(f"错误: {filename} - {e}")
    
    print(f"\n完成! 成功提取: {success}/{total_files}")
    print(f"输出目录: {OUTPUT_DIR}")
    

# 运行
if __name__ == "__main__":
    try:
        correct_extract()
    except Exception as e:
        print(f"错误: {e}")
    
    input("\n按回车键退出...")
