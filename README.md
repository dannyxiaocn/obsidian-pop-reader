# Obsidian Pop Reader

这是一个命令行工具，用于从Obsidian笔记中随机展示和管理您的阅读内容、待办事项和问题。它提供了美观的命令行界面，让您可以轻松浏览和管理Markdown文件中的内容。

## 功能

- 从Obsidian Markdown文件中读取内容
- 支持三种模式：阅读(read)、待办事项(todo)和问题(ques)
- 美观的命令行界面，包含ASCII艺术字体的欢迎界面
- 支持交互式命令，如下一项、列出所有项目、打开链接等
- 彩色输出，提高可读性

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

可以使用以下三个脚本来启动不同模式的阅读器：

```bash
# 阅读模式
./popr.sh [markdown文件路径]

# 待办事项模式
./popt.sh [markdown文件路径]

# 问题模式
./popq.sh [markdown文件路径]
```

也可以直接使用Python脚本：

```bash
python obsidian_reader.py -f [markdown文件路径] -t [类型:r/t/q]
```

## 交互式命令

在运行程序后，您可以使用以下命令：

- `n` - 显示下一项
- `l` - 列出所有项目
- `o` - 打开当前项目的链接（如果有）
- `q` - 退出程序

## 自定义设置

您可以编辑 `obsidian_aliases.sh` 文件来设置别名，方便在任何目录下使用这些命令。

## 示例

```bash
# 查看Obsidian中的待办事项
./popt.sh ~/Documents/Obsidian/tasks.md

# 查看阅读列表
./popr.sh ~/Documents/Obsidian/reading_list.md
```
