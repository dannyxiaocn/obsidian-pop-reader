#!/usr/bin/env python
"""
Obsidian文件阅读器 - 专门用于读取Obsidian格式的markdown文件
支持处理 "- [ ] 内容" 格式的条目
"""

import os
import sys
import random
import re
import argparse
import webbrowser
import platform
import datetime
from colorama import init, Fore, Style, Back

# 初始化colorama
init()

class ObsidianReader:
    """Obsidian文件阅读器类"""
    
    def __init__(self, md_file_path=None, reader_type=None):
        """初始化Obsidian阅读器
        
        Args:
            md_file_path: Obsidian文件路径
            reader_type: 读取器类型，可以是't' (todo), 'r' (read), 'q' (ques) 或 None
        """
        if md_file_path is None:
            print(f"{Fore.RED}错误：必须指定Obsidian文件路径{Style.RESET_ALL}")
            sys.exit(1)
        else:
            # 检查提供的路径是否为绝对路径
            if os.path.isabs(md_file_path):
                self.md_file_path = md_file_path
            else:
                # 如果是相对路径，转换为绝对路径
                self.md_file_path = os.path.abspath(md_file_path)
        
        # 设置读取器类型
        self.reader_type = reader_type
        
        # 检查文件是否存在
        if not os.path.exists(self.md_file_path):
            print(f"{Fore.RED}错误：文件不存在 - {self.md_file_path}{Style.RESET_ALL}")
            sys.exit(1)
            
        self.items = self.parse_obsidian_file()
        self.title = os.path.basename(self.md_file_path).replace('.md', '')
    
    def parse_obsidian_file(self):
        """解析Obsidian文件并返回条目列表，包括父条目及其子条目"""
        try:
            print(f"{Fore.GREEN}正在读取文件: {self.md_file_path}{Style.RESET_ALL}")
            with open(self.md_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            items = []
            
            # 处理每一行
            i = 0
            while i < len(lines):
                line = lines[i].rstrip()
                
                # 检查是否是顶级条目
                parent_match = re.match(r'^- \[([ x])\] (.+)$', line)
                if parent_match:
                    checked = parent_match.group(1) == 'x'
                    parent_text = parent_match.group(2).strip()
                    
                    # 检查是否有链接
                    link_match = re.search(r'\[(.*?)\]\((.*?)\)', parent_text)
                    if link_match:
                        title = link_match.group(1)
                        url = link_match.group(2)
                        parent_item = (parent_text, title, url, checked)
                    else:
                        parent_item = (parent_text, None, None, checked)
                    
                    # 查找子条目
                    sub_items = []
                    j = i + 1
                    while j < len(lines):
                        sub_line = lines[j].rstrip()
                        # 检查是否是子条目（由缩进标识）
                        sub_match = re.match(r'^\s+- \[([ x])\] (.+)$', sub_line)
                        if sub_match:
                            sub_checked = sub_match.group(1) == 'x'
                            sub_text = sub_match.group(2).strip()
                            
                            # 检查子条目是否有链接
                            sub_link_match = re.search(r'\[(.*?)\]\((.*?)\)', sub_text)
                            if sub_link_match:
                                sub_title = sub_link_match.group(1)
                                sub_url = sub_link_match.group(2)
                                sub_items.append((sub_text, sub_title, sub_url, sub_checked))
                            else:
                                sub_items.append((sub_text, None, None, sub_checked))
                            j += 1
                        else:
                            # 如果不是子条目，则结束子条目循环
                            break
                    
                    # 将父条目及其子条目添加到列表中
                    items.append((parent_item, sub_items))
                    
                    # 更新索引以跳过已处理的子条目
                    i = j
                else:
                    # 如果不是顶级条目，则跳过
                    i += 1
            
            return items
        except Exception as e:
            print(f"{Fore.RED}错误：无法解析Obsidian文件: {e}{Style.RESET_ALL}")
            return []
    
    def get_random_item(self):
        """获取随机条目及其子条目，只返回未完成的父条目"""
        if not self.items:
            return None, None
        
        # 从未完成的父条目中随机选择一个
        unchecked_items = [item for item in self.items if not item[0][3]]
        
        if unchecked_items:
            return random.choice(unchecked_items)
        else:
            # 如果没有未完成的父条目，则返回空
            print(f"{Fore.YELLOW}所有父条目均已完成！{Style.RESET_ALL}")
            return None, None
    
    def display_item(self, parent_item, sub_items, show_welcome=True):
        """在终端中显示父条目及其子条目
        
        Args:
            parent_item: 父条目
            sub_items: 子条目列表
            show_welcome: 是否显示欢迎界面，默认为True
        """
        # 解析父条目
        parent_text, parent_title, parent_url, parent_checked = parent_item
        
        # 清屏
        self.clear_screen()
        
        # 始终显示欢迎界面
        display_welcome_banner(self.reader_type)
        
        # 显示标题
        print(f"\n{Back.BLUE}{Fore.WHITE} 今日{self.title}建议 {Style.RESET_ALL}\n")
        
        # 显示父条目状态
        status = f"{Fore.GREEN}[已完成]{Style.RESET_ALL}" if parent_checked else f"{Fore.YELLOW}[待完成]{Style.RESET_ALL}"
        
        # 如果父条目有标题和URL，优先显示标题
        if parent_title and parent_url:
            print(f"{status} {Fore.WHITE}{parent_title}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}链接: {parent_url}{Style.RESET_ALL}")
        else:
            print(f"{status} {Fore.WHITE}{parent_text}{Style.RESET_ALL}")
        
        # 显示子条目（如果有）
        if sub_items:
            print(f"\n{Fore.BLUE}相关子条目:{Style.RESET_ALL}")
            for i, (sub_text, sub_title, sub_url, sub_checked) in enumerate(sub_items):
                # 子条目状态与父条目使用相同格式
                sub_status = f"{Fore.GREEN}[已完成]{Style.RESET_ALL}" if sub_checked else f"{Fore.YELLOW}[待完成]{Style.RESET_ALL}"
                
                if sub_title and sub_url:
                    print(f"  {i+1}. {sub_status} {Fore.WHITE}{sub_title}{Style.RESET_ALL}")
                    print(f"     {Fore.CYAN}链接: {sub_url}{Style.RESET_ALL}")
                else:
                    print(f"  {i+1}. {sub_status} {Fore.WHITE}{sub_text}{Style.RESET_ALL}")
        
        # 如果父条目有URL，提示可以打开
        if parent_url:
            print(f"\n提示: 输入 {Fore.GREEN}o{Style.RESET_ALL} 可以在浏览器中打开父条目链接")
            
        # 如果有子条目并且有URL，提示可以打开子条目链接
        has_sub_url = any(sub[2] for sub in sub_items)
        if has_sub_url:
            print(f"输入 {Fore.GREEN}o1{Style.RESET_ALL}, {Fore.GREEN}o2{Style.RESET_ALL} 等可以打开相应子条目链接")
    
    def clear_screen(self):
        """清屏"""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
    
    def open_url(self, url, index=None):
        """在浏览器中打开URL
        
        Args:
            url: 要打开的URL
            index: 可选，用于显示打开的是第几个子条目的URL
        """
        if url:
            try:
                webbrowser.open(url)
                if index is not None:
                    print(f"{Fore.GREEN}已在浏览器中打开子条目 {index} 的链接{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}已在浏览器中打开链接{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}无法打开链接: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}没有可打开的链接{Style.RESET_ALL}")
    
    def list_all_items(self):
        """列出所有父条目及其子条目"""
        self.clear_screen()
        
        # 始终显示欢迎界面
        display_welcome_banner(self.reader_type)
        
        print(f"\n{Back.BLUE}{Fore.WHITE} {self.title} - 所有条目 {Style.RESET_ALL}\n")
        
        if self.items:
            for i, (parent_item, sub_items) in enumerate(self.items):
                parent_text, parent_title, parent_url, parent_checked = parent_item
                status = f"{Fore.GREEN}[已完成]{Style.RESET_ALL}" if parent_checked else f"{Fore.YELLOW}[待完成]{Style.RESET_ALL}"
                
                # 显示父条目
                if parent_title and parent_url:
                    print(f"{i+1}. {status} {Fore.WHITE}{parent_title}{Style.RESET_ALL}")
                    print(f"   {Fore.CYAN}链接: {parent_url}{Style.RESET_ALL}")
                else:
                    print(f"{i+1}. {status} {Fore.WHITE}{parent_text}{Style.RESET_ALL}")
                
                # 显示子条目（如果有）
                if sub_items:
                    for j, (sub_text, sub_title, sub_url, sub_checked) in enumerate(sub_items):
                        sub_status = f"{Fore.GREEN}[已完成]{Style.RESET_ALL}" if sub_checked else f"{Fore.YELLOW}[待完成]{Style.RESET_ALL}"
                        
                        if sub_title and sub_url:
                            print(f"   {j+1}) {sub_status} {Fore.WHITE}{sub_title}{Style.RESET_ALL}")
                            print(f"      {Fore.CYAN}链接: {sub_url}{Style.RESET_ALL}")
                        else:
                            print(f"   {j+1}) {sub_status} {Fore.WHITE}{sub_text}{Style.RESET_ALL}")
                
                print()  # 添加空行以提高可读性
        else:
            print(f"{Fore.RED}没有找到任何条目{Style.RESET_ALL}")
    

    
    def run_interactive(self):
        """运行交互式模式"""
        parent_and_subs = self.get_random_item()
        
        if parent_and_subs:
            parent_item, sub_items = parent_and_subs
            self.display_item(parent_item, sub_items)
            
            # 提取父条目的URL
            _, _, parent_url, _ = parent_item
            
            # 提取子条目的URL列表
            sub_urls = [sub[2] for sub in sub_items if sub[2]]
            
            while True:
                print(f"\n{Fore.GREEN}命令:{Style.RESET_ALL}")
                print(f"  {Fore.GREEN}n{Style.RESET_ALL} - 下一条")
                if parent_url:
                    print(f"  {Fore.GREEN}o{Style.RESET_ALL} - 打开父条目链接")
                if sub_urls:
                    print(f"  {Fore.GREEN}o1{Style.RESET_ALL}, {Fore.GREEN}o2{Style.RESET_ALL}... - 打开对应子条目链接")
                print(f"  {Fore.GREEN}l{Style.RESET_ALL} - 列出所有条目")
                print(f"  {Fore.GREEN}q{Style.RESET_ALL} - 退出")
                
                choice = input(f"\n{Fore.GREEN}请输入命令: {Style.RESET_ALL}").strip().lower()
                
                if choice == 'n':
                    parent_and_subs = self.get_random_item()
                    if parent_and_subs:
                        parent_item, sub_items = parent_and_subs
                        # 始终显示欢迎界面
                        self.display_item(parent_item, sub_items)
                        # 更新URL
                        _, _, parent_url, _ = parent_item
                        sub_urls = [sub[2] for sub in sub_items if sub[2]]
                    else:
                        # 如果没有未完成的条目，则返回主菜单
                        continue
                elif choice == 'o' and parent_url:
                    self.open_url(parent_url)
                elif choice.startswith('o') and len(choice) > 1:
                    try:
                        # 尝试提取子条目索引
                        sub_index = int(choice[1:]) - 1
                        if 0 <= sub_index < len(sub_urls):
                            self.open_url(sub_urls[sub_index], sub_index + 1)
                        else:
                            print(f"{Fore.RED}无效的子条目索引{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}无效的命令格式{Style.RESET_ALL}")
                elif choice == 'l':
                    # 清屏并显示欢迎界面
                    self.clear_screen()
                    display_welcome_banner(self.reader_type)
                    
                    self.list_all_items()
                    input(f"\n{Fore.GREEN}按Enter键返回...{Style.RESET_ALL}")
                    self.display_item(parent_item, sub_items)
                elif choice == 'q':
                    print(f"\n{Fore.YELLOW}感谢使用，再见！{Style.RESET_ALL}")
                    break
                else:
                    print(f"\n{Fore.RED}无效的命令，请重试{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}没有找到任何未完成的条目{Style.RESET_ALL}")

def display_welcome_banner(reader_type=None):
    """显示欢迎界面
    
    Args:
        reader_type: 读取器类型，可以是't' (todo), 'r' (read), 'q' (ques) 或 None
    """
    # 当前日期
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 根据类型选择颜色和标志
    if reader_type == 't':
        color = Fore.GREEN
        type_full = "todo"
        logo = [
            "    ___  ___  ___    ",
            "   / _ \/ _ \/ _ \   ",
            "  / /__/ // / ___/   ",
            " /_/  /____/_/       ",
            "  _____         _      ",
            " |_   _|__   __| | ___ ",
            "   | |/ _ \\ / _` |/ _ \\",
            "   | | (_) | (_| | (_) |",
            "   |_|\\___/ \\__,_|\\___/ "
        ]
    elif reader_type == 'r':
        color = Fore.BLUE
        type_full = "read"
        logo = [
            "    ___  ___  ___    ",
            "   / _ \/ _ \/ _ \   ",
            "  / /__/ // / ___/   ",
            " /_/  /____/_/       ",
            "  ____                _ ",
            " |  _ \\ ___  __ _  __| |",
            " | |_) / _ \ /_` |/ _` |",
            " |  _ <  __/ (_| | (_| |",
            " |_| \_\___|\__,_|\__,_|"
        ]
    elif reader_type == 'q':
        color = Fore.YELLOW
        type_full = "ques"
        logo = [
            "    ___  ___  ___    ",
            "   / _ \/ _ \/ _ \   ",
            "  / /__/ // / ___/   ",
            " /_/  /____/_/       ",
            "   ___                  ",
            "  / _ \ _   _  ___  ___ ",
            " | | | | | | |/ _ \/ __|",
            " | |_| | |_| |  __/\__ \\",
            "  \__\_\\__\\__|\___||___/"
        ]
    else:
        color = Fore.CYAN
        type_full = "reader"
        logo = [
            "    ___  ___  ___    ",
            "   / _ \/ _ \/ _ \   ",
            "  / /__/ // / ___/   ",
            " /_/  /____/_/       ",
            "  ____                _           ",
            " |  _ \ ___  __ _  __| | ___ _ __ ",
            " | |_) / _ \/ _` |/ _` |/ _ \ '__|",
            " |  _ <  __/ (_| | (_| |  __/ |   ",
            " |_| \_\___|\__,_|\__,_|\___|_|   "
        ]
    
    # 右侧信息
    info = [
        f"| Obsidian {type_full.capitalize()} v1.0.0",
        f"| 日期: {current_date}",
        f"| 作者: bocheng & windsurf",
    ]
    
    # 计算最长的行长度
    max_logo_len = max(len(line) for line in logo)
    max_info_len = max(len(line) for line in info)
    
    # 打印标志和信息
    print("\n")
    for i in range(max(len(logo), len(info))):
        logo_line = color + logo[i] + Style.RESET_ALL if i < len(logo) else " " * max_logo_len
        info_line = info[i] if i < len(info) else ""
        padding = " " * (max_logo_len - len(logo[i]) if i < len(logo) else max_logo_len)
        print(f"{logo_line}{padding}  {info_line}")
    print("\n")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Obsidian文件阅读器')
    parser.add_argument('--file', help='指定Obsidian文件路径')
    parser.add_argument('-r', '--random', action='store_true', help='显示一个随机条目并退出')
    parser.add_argument('-l', '--list', action='store_true', help='列出所有条目并退出')
    parser.add_argument('--type', choices=['t', 'r', 'q'], help='指定读取器类型，可以是t (todo), r (read), q (ques)')
    
    args = parser.parse_args()
    
    reader = ObsidianReader(args.file, args.type)
    
    if args.random:
        parent_and_subs = reader.get_random_item()
        if parent_and_subs:
            parent_item, sub_items = parent_and_subs
            reader.display_item(parent_item, sub_items)
        else:
            # 清屏并显示欢迎界面
            os.system('clear' if platform.system() != 'Windows' else 'cls')
            display_welcome_banner(args.type)
            print(f"\n{Fore.RED}没有找到任何条目{Style.RESET_ALL}")
    elif args.list:
        # 清屏并显示欢迎界面
        os.system('clear' if platform.system() != 'Windows' else 'cls')
        display_welcome_banner(args.type)
        
        reader.list_all_items()
    else:
        reader.run_interactive()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}程序被中断，再见！{Style.RESET_ALL}")
        sys.exit(0)
