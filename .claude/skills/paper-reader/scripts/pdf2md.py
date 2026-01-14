#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown文档格式化工具

功能：
1. 去除中文字符之间多余的空格
2. 去除多余的换行符和空白行
3. 去除"参考文献"及其后面的文本
4. 支持将PDF转换为MD（使用MarkItDown）
5. 支持批量处理目录下的PDF文件（并行处理）

性能优化：
- 预编译正则表达式
- 并行处理多个PDF文件
- 移除重复的conda进程调用

使用方式：
  # 先激活包含markitdown的环境
  conda activate markitdown

  # 转换并格式化PDF
  python pdf2md.py input.pdf                    # 生成同名的md文件并格式化
  python pdf2md.py input.pdf -o output.md       # 转换并指定输出md路径
  python pdf2md.py input.pdf --inplace          # 原地替换

  # 提取指定页码范围
  python pdf2md.py input.pdf --pages 5          # 只提取前5页
  python pdf2md.py input.pdf --pages 1-3        # 提取第1-3页
  python pdf2md.py input.pdf --pages 1,3,5      # 提取第1、3、5页
  python pdf2md.py input.pdf --pages 1-3,5,7-9  # 提取第1-3页、第5页、第7-9页

  # 批量处理目录
  python pdf2md.py ./papers/                    # 转换目录下所有PDF
  python pdf2md.py ./papers/ -o ./outputs/      # 指定输出目录

  # 只格式化MD
  python pdf2md.py input.md                    # 生成input_formatted.md
  python pdf2md.py input.md -o output.md       # 指定输出文件
  python pdf2md.py input.md --inplace          # 直接替换原文件

  # 只转换PDF（不格式化）
  python pdf2md.py input.pdf --pdf-only        # 只转换不格式化
  python pdf2md.py ./papers/ --pdf-only        # 批量只转换不格式化

  # 并行处理目录（默认4个进程）
  python pdf2md.py ./papers/ --workers 8       # 使用8个进程
  python pdf2md.py ./papers/ --workers 0       # 使用全部CPU核心
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Union
from functools import partial

# 预编译正则表达式，提升性能
CHINESE_SPACE_PATTERN = re.compile(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])')
MULTIPLE_NEWLINES_PATTERN = re.compile(r'\n{3,}')
REFERENCE_PATTERNS = [
    re.compile(r'参考文\s*献.*', re.DOTALL),
    re.compile(r'参考文献.*', re.DOTALL),
    re.compile(r'参考\s*文\s*献.*', re.DOTALL),
]

# 句末标点符号
END_PUNCTUATIONS = set('。！？；:;、）)》\"\'。?')


def parse_page_range(page_spec: str, total_pages: int) -> List[int]:
    """解析页码范围字符串，返回页码列表

    支持的格式:
    - "5"        -> [1, 2, 3, 4, 5] (前N页)
    - "1-3"      -> [1, 2, 3]
    - "1,3,5"    -> [1, 3, 5]
    - "1-3,5,7-9" -> [1, 2, 3, 5, 7, 8, 9]

    Args:
        page_spec: 页码范围字符串
        total_pages: PDF总页数

    Returns:
        排序后的页码列表（从1开始）
    """
    pages = set()

    # 如果只是一个数字，表示前N页
    if page_spec.isdigit():
        n = int(page_spec)
        return list(range(1, min(n, total_pages) + 1))

    # 解析范围和单个页码
    parts = page_spec.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            # 范围: "1-3"
            start, end = part.split('-')
            start = int(start.strip())
            end = int(end.strip())
            pages.update(range(start, end + 1))
        else:
            # 单个页码
            pages.add(int(part))

    # 过滤无效页码并排序
    result = sorted([p for p in pages if 1 <= p <= total_pages])
    return result


def extract_pdf_pages(pdf_path: str, pages: List[int], output_path: str) -> str:
    """从PDF中提取指定页面，保存为新PDF

    Args:
        pdf_path: 原PDF文件路径
        pages: 要提取的页码列表（从1开始）
        output_path: 输出PDF文件路径

    Returns:
        输出文件路径
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("错误: 未安装 PyMuPDF 库。请运行: pip install pymupdf")
        sys.exit(1)

    source_doc = fitz.open(pdf_path)

    # 创建新文档
    new_doc = fitz.open()

    # 复制指定页面（PyMuPDF使用0-based索引）
    for page_num in pages:
        if 1 <= page_num <= len(source_doc):
            new_doc.insert_pdf(source_doc, from_page=page_num - 1, to_page=page_num - 1)

    # 保存新PDF
    new_doc.save(output_path)
    new_doc.close()
    source_doc.close()

    return output_path


def remove_extra_spaces(text: str) -> str:
    """去除中文字符之间多余的空格，保留英文和数字周围的空格"""
    return CHINESE_SPACE_PATTERN.sub('', text)


def remove_extra_newlines(text: str) -> str:
    """去除多余的换行符和空白行，保留段落分隔"""
    # 步骤1: 将连续的空行合并为单个空行
    result = MULTIPLE_NEWLINES_PATTERN.sub('\n\n', text)

    # 步骤2: 处理段落内的换行
    lines = result.split('\n')
    final_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            # 空行保留作为段落分隔
            final_lines.append('')
        elif i > 0 and lines[i-1].strip():
            # 前一行非空，判断是否在同一段落
            prev_stripped = lines[i-1].strip()
            if prev_stripped[-1] in END_PUNCTUATIONS:
                # 以句末标点结尾，保留换行
                final_lines.append(stripped)
            else:
                # 同一段落内，合并到前一行
                final_lines[-1] = prev_stripped + ' ' + stripped
        else:
            final_lines.append(stripped)

    return '\n'.join(final_lines)


def remove_references(text: str) -> str:
    """去除'参考文献'及其后面的所有文本"""
    for pattern in REFERENCE_PATTERNS:
        text = pattern.sub('', text)
    return text.strip()


def format_md_content(text: str) -> str:
    """格式化markdown内容"""
    # 1. 先去除参考文献
    text = remove_references(text)

    # 2. 去除多余空格
    text = remove_extra_spaces(text)

    # 3. 去除多余换行符
    text = remove_extra_newlines(text)

    return text


def process_file(input_path: str, output_path: str = None, inplace: bool = False) -> None:
    """处理markdown文件"""
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"错误: 文件不存在 - {input_path}")
        sys.exit(1)

    if not input_file.suffix.lower() == '.md':
        print(f"警告: 文件扩展名不是.md - {input_path}")

    # 读取文件内容，尝试多种编码
    encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'gbk', 'gb2312', 'gb18030', 'latin1']
    content = None
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if content is None:
        # 尝试使用二进制模式读取，然后解码
        try:
            with open(input_file, 'rb') as f:
                raw_data = f.read()
            # 尝试从BOM检测编码
            if raw_data.startswith(b'\xff\xfe'):
                content = raw_data.decode('utf-16-le')
            elif raw_data.startswith(b'\xfe\xff'):
                content = raw_data.decode('utf-16-be')
            else:
                # 使用 errors='replace' 处理无法解码的字符
                content = raw_data.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"错误: 读取文件失败 - {e}")
            sys.exit(1)
    
    if not content:
        print(f"错误: 文件内容为空 - {input_path}")
        sys.exit(1)

    # 格式化内容
    formatted_content = format_md_content(content)

    # 确定输出路径
    if inplace:
        output_path = input_path
    elif output_path is None:
        # 默认输出到原文件同级目录，文件名加_formatted后缀
        output_path = input_file.with_name(input_file.stem + '_formatted' + input_file.suffix)

    # 写入文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        print(f"格式化完成！")
        print(f"输入文件: {input_file.absolute()}")
        print(f"输出文件: {Path(output_path).absolute()}")
    except Exception as e:
        print(f"错误: 写入文件失败 - {e}")
        sys.exit(1)


def convert_pdf_to_md(pdf_path: str, output_path: str = None, pages: str = None, verbose: bool = False) -> str:
    """使用MarkItDown将PDF转换为MD文件

    Args:
        pdf_path: PDF文件路径
        output_path: 输出MD文件路径
        pages: 页码范围（如 "5", "1-3", "1,3,5", "1-3,5,7-9"）
        verbose: 是否显示详细信息
    """
    try:
        from markitdown import MarkItDown
    except ImportError:
        print("错误: 未安装 markitdown 库。请先激活包含markitdown的环境，或运行: pip install markitdown")
        sys.exit(1)

    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        print(f"错误: PDF文件不存在 - {pdf_path}")
        sys.exit(1)

    # 确定输出路径
    if output_path is None:
        default_output_dir = Path('outputs')
        if not default_output_dir.exists():
            default_output_dir = pdf_file.parent
        output_path = str(default_output_dir / (pdf_file.stem + '.md'))

    # 处理页码范围
    source_pdf_path = pdf_path
    temp_pdf_path = None

    if pages:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            print("错误: 使用 --pages 参数需要安装 PyMuPDF 库。请运行: pip install pymupdf")
            sys.exit(1)

        # 获取PDF总页数
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()

        # 解析页码范围
        page_list = parse_page_range(pages, total_pages)

        if verbose:
            print(f"提取页码: {page_list}")

        # 如果需要提取页面，创建临时PDF
        if len(page_list) < total_pages:
            import tempfile
            temp_fd, temp_pdf_path = tempfile.mkstemp(suffix='.pdf')
            import os
            os.close(temp_fd)

            extract_pdf_pages(pdf_path, page_list, temp_pdf_path)
            source_pdf_path = temp_pdf_path

            if verbose:
                print(f"已创建临时PDF: {temp_pdf_path}")

    try:
        if verbose:
            print(f"正在转换: {pdf_file.absolute()}")

        md_converter = MarkItDown()
        result = md_converter.convert(str(source_pdf_path))
        content = result.text_content

        # 如果提取了页面，添加页码信息
        if pages and temp_pdf_path:
            content = f"<!-- 从原PDF提取的页码: {pages} -->\n\n{content}"

        # 写入MD文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        if verbose:
            print(f"已生成: {output_path}")

        # 清理临时文件
        if temp_pdf_path and Path(temp_pdf_path).exists():
            import os
            os.unlink(temp_pdf_path)
            if verbose:
                print(f"已清理临时文件: {temp_pdf_path}")

        return output_path
    except Exception as e:
        print(f"错误: PDF转换失败 - {e}")
        # 清理临时文件
        if temp_pdf_path and Path(temp_pdf_path).exists():
            import os
            os.unlink(temp_pdf_path)
        sys.exit(1)


def process_single_pdf_task(pdf_file: Path, output_path: Path, pdf_only: bool, pages: str, verbose: bool) -> tuple[bool, str]:
    """处理单个PDF，返回(是否成功, 消息)

    注意：这个函数必须在模块级别，以便在Windows上能够被pickle。
    """
    try:
        md_output_path = str(output_path / (pdf_file.stem + '.md'))

        if verbose:
            print(f"\n处理: {pdf_file.name}")

        convert_pdf_to_md(str(pdf_file), md_output_path, pages=pages, verbose=False)

        if not pdf_only:
            # 读取并格式化
            with open(md_output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            formatted = format_md_content(content)
            with open(md_output_path, 'w', encoding='utf-8') as f:
                f.write(formatted)

        return True, f"✓ {pdf_file.name}"
    except Exception as e:
        return False, f"✗ {pdf_file.name}: {e}"


def process_pdf_file(pdf_path: str, output_path: str = None, inplace: bool = False, pdf_only: bool = False, pages: str = None, verbose: bool = False) -> None:
    """处理PDF文件：转换并可选格式化

    Args:
        pdf_path: PDF文件路径
        output_path: 输出MD文件路径
        inplace: 是否原地替换
        pdf_only: 是否只转换不格式化
        pages: 页码范围（如 "5", "1-3", "1,3,5", "1-3,5,7-9"）
        verbose: 是否显示详细信息
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        print(f"错误: PDF文件不存在 - {pdf_path}")
        sys.exit(1)

    # 确定转换后的MD文件路径
    if inplace:
        md_output_path = str(pdf_file.with_suffix('.md'))
    elif output_path:
        md_output_path = output_path
    else:
        # 默认输出到 outputs 目录
        output_dir = Path('outputs')
        output_dir.mkdir(exist_ok=True)
        md_output_path = str(output_dir / (pdf_file.stem + '.md'))

    # 转换PDF为MD
    convert_pdf_to_md(pdf_path, md_output_path, pages=pages, verbose=verbose)

    # 如果不是只转换模式，则格式化MD
    if not pdf_only:
        if verbose:
            print(f"开始格式化: {md_output_path}")
        process_file(md_output_path, inplace=True)


def process_directory(input_dir: str, output_dir: str = None, pdf_only: bool = False, workers: int = None, pages: str = None, verbose: bool = False) -> None:
    """处理目录下所有PDF文件，支持并行处理

    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        pdf_only: 是否只转换不格式化
        workers: 并行进程数
        pages: 页码范围（如 "5", "1-3", "1,3,5", "1-3,5,7-9"）
        verbose: 是否显示详细信息
    """
    input_path = Path(input_dir)

    if not input_path.exists() or not input_path.is_dir():
        print(f"错误: 目录不存在 - {input_dir}")
        sys.exit(1)

    # 收集所有PDF文件
    pdf_files = sorted(input_path.glob('*.pdf'))

    if not pdf_files:
        print(f"警告: 目录中没有找到PDF文件 - {input_dir}")
        return

    print(f"找到 {len(pdf_files)} 个PDF文件")

    # 确定输出目录
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path / 'outputs'

    output_path.mkdir(exist_ok=True)

    # 使用并行处理
    if workers is None:
        workers = min(4, len(pdf_files))  # 默认最多4个进程
    elif workers <= 0:
        workers = len(pdf_files)  # 0或负数表示使用全部

    print(f"使用 {workers} 个进程并行处理...")

    # 使用 functools.partial 创建可 pickle 的函数
    from concurrent.futures import ProcessPoolExecutor, as_completed
    task_func = partial(process_single_pdf_task, output_path=output_path, pdf_only=pdf_only, pages=pages, verbose=verbose)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(task_func, pdf): pdf for pdf in pdf_files}

        for future in as_completed(futures):
            success, message = future.result()
            print(message)

    print(f"\n完成！共处理 {len(pdf_files)} 个PDF文件")


def main():
    parser = argparse.ArgumentParser(
        description='Markdown文档格式化工具（支持PDF转MD）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('input', help='输入的md文件路径、pdf文件路径或目录路径')
    parser.add_argument('-o', '--output', help='输出的md文件路径或输出目录路径（默认: outputs目录）')
    parser.add_argument('--inplace', action='store_true', help='直接替换原文件（仅对单个文件有效）')
    parser.add_argument('--pdf-only', action='store_true', help='只转换PDF为MD，不进行格式化')
    parser.add_argument('--pages', type=str, default=None, help='提取指定页码范围（如: "5" 前5页, "1-3" 第1-3页, "1,3,5" 第1/3/5页, "1-3,5,7-9" 组合）')
    parser.add_argument('--workers', type=int, default=None, help='并行处理时使用的进程数（默认: 4，0表示使用全部核心）')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')

    args = parser.parse_args()

    if args.verbose:
        print(f"输入路径: {args.input}")
        print(f"输出路径: {args.output if args.output else 'outputs目录'}")
        if args.pages:
            print(f"页码范围: {args.pages}")

    input_path = Path(args.input)

    # 判断输入类型并处理
    if input_path.is_file():
        input_lower = input_path.suffix.lower()
        if input_lower == '.md':
            # 处理MD文件
            if args.pdf_only:
                print("错误: --pdf-only 参数不能用于MD文件")
                sys.exit(1)
            if args.pages:
                print("错误: --pages 参数不能用于MD文件")
                sys.exit(1)
            process_file(args.input, args.output, args.inplace)
        elif input_lower == '.pdf':
            # 处理单个PDF文件
            process_pdf_file(args.input, args.output, args.inplace, args.pdf_only, args.pages, args.verbose)
        else:
            print(f"错误: 不支持的文件格式 - {input_lower}")
            sys.exit(1)
    elif input_path.is_dir():
        # 处理目录（批量处理PDF）
        process_directory(args.input, args.output, args.pdf_only, args.workers, args.pages, args.verbose)
    else:
        print(f"错误: 路径不存在 - {args.input}")
        sys.exit(1)


if __name__ == '__main__':
    main()