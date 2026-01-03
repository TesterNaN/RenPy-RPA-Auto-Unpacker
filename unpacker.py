#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RenPy-RPA-Auto-Unpacker - 全自动的 Ren'Py RPA 解包工具
Copyright (C) 2025 TesterNaN

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import re
import os, glob


def find_rpa_file():
    files = glob.glob(".\\game\\*.rpa")
    if files:
        return files[0].replace(".\\game\\","")
    return None

code_part_1 =r"""import os
import zlib
import pickle
import io
from typing import List, Tuple, Dict

def loads(data):
    return pickle.loads(data)

class RenpyConfig:
    def __init__(self):
        self.archives = []

class RWopsIO(io.RawIOBase):
    def __init__(self, filename, mode="rb", base=0, length=None):
        super().__init__()
        self.filename = filename
        self.mode = mode
        self.base = base
        self.length = length
        self.file = None
        self.position = 0
        self.total_size = 0
        
    @staticmethod
    def from_buffer(data, name=""):
        return io.BytesIO(data)
    
    @staticmethod
    def from_split(a, b, name=""):
        data1 = a.read()
        data2 = b.read()
        return io.BytesIO(data1 + data2)
    
    def _open_file(self):
        if self.file is None:
            self.file = open(self.filename, self.mode)
            if self.base:
                self.file.seek(self.base)
            
            # 获取文件总大小
            if self.length is None:
                current = self.file.tell()
                self.file.seek(0, 2)
                self.total_size = self.file.tell()
                self.file.seek(current)
    
    def seekable(self):
        return True
    
    def readable(self):
        return True
    
    def seek(self, offset, whence=0):
        self._open_file()
        
        if whence == 0:
            new_pos = offset
        elif whence == 1:
            new_pos = self.position + offset
        elif whence == 2:
            new_pos = self.total_size + offset
        else:
            raise ValueError("Invalid whence value")
        
        if self.length is not None:
            if new_pos < 0:
                new_pos = 0
            elif new_pos > self.length:
                new_pos = self.length
        
        self.position = new_pos
        self.file.seek(self.base + new_pos)
        return self.position
    
    def tell(self):
        return self.position
    
    def read(self, size=-1):
        self._open_file()
        
        if self.length is not None:
            remaining = self.length - self.position
            if remaining <= 0:
                return b""
            if size == -1 or size > remaining:
                size = remaining
        
        if size == 0:
            return b""
        
        data = self.file.read(size)
        self.position += len(data)
        return data
    
    def readinto(self, buffer):
        data = self.read(len(buffer))
        if not data:
            return 0
        buffer[:len(data)] = data
        return len(data)
    
    def close(self):
        if self.file is not None:
            self.file.close()
            self.file = None
        super().close()

renpy = type('Renpy', (), {'config': RenpyConfig()})()

arc_files: List[Tuple[str, str, str]] = [
    ('"""+find_rpa_file().replace(".rpa","")+"""', '.rpa', '"""+os.getcwd().replace("\\","\\\\")+"""\\\\game/"""+find_rpa_file()+"""')
]
archives: List[Tuple[str, Dict]] = []
lower_map: Dict[str, str] = {}

# A list containing archive handlers.
archive_handlers = None

class ArchiveHandlers:
    def __init__(self):
        self.exts = {}
        self.peek = {}

    def append(self, handler):
        candidates = []
        header_sizes = []

        for header in handler.get_supported_headers():
            candidates.append((header, handler))
            header_sizes.append(len(header))

        peek = max(header_sizes)

        for ext in handler.get_supported_extensions():
            self.exts.setdefault(ext, []).extend(candidates)
            self.peek[ext] = max(self.peek.get(ext, 0), peek)

    def spec(self, ext):
        return self.peek[ext], self.exts[ext]


# A list containing archive handlers.
archive_handlers = ArchiveHandlers()

"""
with open('core.py', 'w', encoding='utf-8') as f:
    f.write(code_part_1+'\n')


# 配置
loader = r".\renpy\loader.py"

# 读取文件
with open(loader, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 提取RPAv3ArchiveHandler类
start1 = content.find('class RPAv3ArchiveHandler(object):')
if start1 == -1:
    start1 = content.find('class RPAv3ArchiveHandler:')

# 查找return index
if start1 != -1:
    # 查找从start1开始的第一个return index
    return_idx = content.find('return index', start1)
    if return_idx != -1:
        # 找到return index所在行的末尾
        line_end = content.find('\n', return_idx)
        if line_end != -1:
            code1 = content[start1:line_end+1]
            with open('core.py', 'a', encoding='utf-8') as f:
                f.write(code1+'\n')

# 2. 提取index_archives函数
start2 = content.find('def index_archives():')

if start2 != -1:
    # 查找renpy.config.archives.append(stem)
    append_idx = content.find('break', start2)
    
    if append_idx != -1:
        # 找到该行末尾
        line_end = content.find('\n', append_idx)
        if line_end != -1:
            code2 = content[start2:line_end+1]
            with open('core.py', 'a', encoding='utf-8') as f:
                f.write(code2+'\n')


# 2. 提取index_archives函数
start3 = content.find('def load_from_archive(name):')

if start3 != -1:
    # 查找renpy.config.archives.append(stem)
    append_idx = content.find('return None', start3)
    
    if append_idx != -1:
        # 找到该行末尾
        line_end = content.find('\n', append_idx)
        if line_end != -1:
            code3 = content[start3:line_end+1]
            with open('core.py', 'a', encoding='utf-8') as f:
                f.write(code3)

code_part_2 = r"""
def extract_files(output_dir="extracted"):
    os.makedirs(output_dir, exist_ok=True)
    
    total_files = 0
    
    if not archives:
        print("错误: 没有找到任何存档索引")
        return 0
    
    all_files = []
    for data_file_path, index in archives:
        print(f"\n处理存档: {os.path.basename(data_file_path)}")
        print(f"索引中的文件数量: {len(index)}")
        all_files.extend(index.keys())
    
    unique_files = list(set(all_files))
    print(f"\n总共发现 {len(unique_files)} 个唯一文件")
    
    success_count = 0
    
    for i, filename in enumerate(unique_files, 1):
        try:
            output_path = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            file_obj = load_from_archive(filename)
            
            if file_obj is None:
                print(f"警告: 无法加载文件 {filename}")
                continue
            
            file_data = file_obj.read()
            
            file_obj.close()
            
            with open(output_path, "wb") as out_file:
                out_file.write(file_data)
            
            success_count += 1
            total_files += 1
            
            if success_count % 50 == 0:
                print(f"已提取: {success_count}/{len(unique_files)}")
                
        except Exception as e:
            print(f"提取文件失败 {filename}: {e}")
    
    print(f"\n总共提取了 {success_count}/{len(unique_files)} 个文件到目录: {output_dir}")
    return success_count


def main():
    global archive_handlers
    
    print("=" * 60)
    print("Ren'Py RPAv3 解包工具")
    print("=" * 60)
    
    archive_handlers = ArchiveHandlers()
    
    archive_handlers.append(RPAv3ArchiveHandler)
    
    missing_files = []
    for _, _, fn in arc_files:
        if not os.path.exists(fn):
            missing_files.append(fn)
    
    if missing_files:
        print("\n错误: 以下RPA文件不存在:")
        for f in missing_files:
            print(f"  - {f}")
        print("\n请修改arc_files变量中的文件路径")
        return
    
    print(f"\n找到 {len(arc_files)} 个RPA文件:")
    for stem, ext, fn in arc_files:
        print(f"  - {stem}{ext}: {fn}")
    

    print("\n正在读取RPA文件索引...")
    index_archives()
    
    if not archives:
        print("错误: 无法读取任何RPA文件索引")
        return
    
    print(f"成功读取 {len(archives)} 个RPA文件的索引")
    

    print("\n存档信息:")
    for i, (data_file_path, index) in enumerate(archives, 1):
        data_file_name = os.path.basename(data_file_path)
        print(f"{i}. 数据文件: {data_file_name}")
        print(f"   包含 {len(index)} 个文件索引")
        
        if not os.path.exists(data_file_path):
            print(f"   错误: 无法找到数据文件")
        
    
    print("开始提取文件...")
    output_dir = "extracted_files"
    success = extract_files(output_dir)
    
    if success > 0:
        print(f"\n提取完成！成功提取 {success} 个文件")
    else:
        print("\n提取失败！")

"""
with open('core.py', 'a', encoding='utf-8') as f:
    f.write(code_part_2+'\n')
from core import main
main()

