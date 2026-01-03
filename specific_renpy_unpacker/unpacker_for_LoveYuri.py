import os
import zlib
import pickle

# ========== 配置区 ==========
RPA_FILE = "game_files.rpa"      # RPA文件路径
OUTPUT_DIR = "extracted"      # 输出目录
# ===========================

def extract():
    print("要来点百合吗 Love Yuri RPAv3 解包脚本")
    print("=" * 50)
    
    # 1. 读取索引
    print("正在读取索引...")
    with open(RPA_FILE, 'rb') as f:
        # 读取文件头
        header = f.read(40)
        
        # 提取偏移和密钥
        offset = int(header[8:24], 16)  # 索引偏移
        key = int(header[25:33], 16)    # XOR密钥
        
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
    
    # 2. 解密索引
    print("正在解密索引...")
    decrypted_index = {}
    
    for filename, entries in raw_index.items():
        decrypted_entries = []
        
        for entry in entries:
            if len(entry) == 2:
                # 2元组: (offset, dlen)
                enc_offset, enc_dlen = entry
                offset = enc_offset ^ key
                dlen = enc_dlen ^ key
                decrypted_entries.append((offset, dlen))
            else:
                # 3元组: (offset, dlen, start)
                enc_offset, enc_dlen, start = entry
                offset = enc_offset ^ key
                dlen = enc_dlen ^ key
                
                # 转换起始字节
                if not start:
                    start_bytes = b''
                elif not isinstance(start, bytes):
                    start_bytes = start.encode("latin-1")
                else:
                    start_bytes = start
                
                decrypted_entries.append((offset, dlen, start_bytes))
        
        decrypted_index[filename] = decrypted_entries
    
    # 3. 提取文件
    print("正在提取文件...")
    success = 0
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(RPA_FILE, 'rb') as data_file:
        for filename, entries in decrypted_index.items():
            try:
                # 创建文件路径
                out_path = os.path.join(OUTPUT_DIR, filename)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                
                # 写入文件
                with open(out_path, 'wb') as out_file:
                    for entry in entries:
                        if len(entry) == 2:
                            offset, dlen = entry
                            start_bytes = b''
                        else:
                            offset, dlen, start_bytes = entry
                        
                        if start_bytes:
                            out_file.write(start_bytes)
                        
                        data_file.seek(offset)
                        data = data_file.read(dlen)
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
