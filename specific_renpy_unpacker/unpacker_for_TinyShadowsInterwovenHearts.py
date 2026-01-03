import os
import zlib
import pickle

# ========== 配置区 ==========
RPA_FILE = "archive.rpa"      # RPA文件路径
OUTPUT_DIR = "extracted"      # 输出目录
# ===========================

def extract():
    """新版RPAv3解包"""
    print("小小的身影，重叠的内心 RPAv3 解包脚本")
    print("=" * 50)
    
    # 1. 读取RPA文件头
    print("正在读取索引...")
    with open(RPA_FILE, 'rb') as f:
        # 读取头信息
        header = f.read(40)
        
        # 提取偏移和密钥
        offset_hex = header[8:24]  # 16字节偏移
        key_hex = header[25:33]    # 8字节密钥
        
        offset = int(offset_hex, 16)  # 索引位置
        key = int(key_hex, 16)        # XOR密钥
        
        print(f"索引偏移: {offset} (0x{offset:x})")
        print(f"XOR密钥: 0x{key:08x}")
        
        # 跳转到索引位置
        f.seek(offset)
        
        # 解压并加载索引
        compressed = f.read()
        decompressed = zlib.decompress(compressed)
        raw_index = pickle.loads(decompressed)
    
    total_files = len(raw_index)
    print(f"找到 {total_files} 个文件")
    
    # 2. 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 3. 解密索引并提取文件
    print("正在提取文件...")
    success = 0
    
    with open(RPA_FILE, 'rb') as data_file:
        for filename, entries in raw_index.items():
            try:
                # 每个文件只有一个条目
                entry = entries[0]
                
                if len(entry) == 2:
                    enc_offset, enc_length = entry
                    start_bytes = b''
                else:
                    enc_offset, enc_length, start = entry
                    # 转换起始字节
                    if not start:
                        start_bytes = b''
                    elif not isinstance(start, bytes):
                        start_bytes = start.encode('latin-1')
                    else:
                        start_bytes = start
                
                # 解密公式：XOR操作
                offset = enc_offset ^ key
                length = enc_length ^ key
                
                # 创建文件路径
                out_path = os.path.join(OUTPUT_DIR, filename)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                
                # 读取数据
                data_file.seek(offset)
                data = data_file.read(length)
                
                # 写入文件
                with open(out_path, 'wb') as out_file:
                    if start_bytes:
                        out_file.write(start_bytes)
                    out_file.write(data)
                
                success += 1
                
                # 显示进度
                if success % 100 == 0:
                    print(f"进度: {success}/{total_files}")
                    
            except Exception as e:
                print(f"错误: {filename} - {e}")
    
    print(f"\n完成! 成功提取: {success}/{total_files}")
    print(f"输出目录: {OUTPUT_DIR}")

# 运行
if __name__ == "__main__":
    try:
        extract()
    except Exception as e:
        print(f"错误: {e}")
    
    input("\n按回车键退出...")
