import os
import requests
from pathspec import PathSpec
from tqdm import tqdm

# FastAPI 服务端地址
SERVER_URL = "http://localhost:7001"

# 类似 .gitignore 的文件路径
IGNORE_FILE = ".gitignore"

# 内建黑名单文件内容
DEFAULT_IGNORE_CONTENT = """
.git
.svn
.venv
__pycache__
*.pyc
.DS_Store
"""

def load_ignore_patterns(ignore_content=None):
    """加载 .gitignore 风格的忽略模式."""
    
    combined_ignore_content = DEFAULT_IGNORE_CONTENT
    if ignore_content:
        combined_ignore_content += "\n" + ignore_content

    try:
        with open(IGNORE_FILE, "r") as f:
            file_content = f.read().strip()
            if file_content:
                combined_ignore_content += "\n" + file_content
    except FileNotFoundError:
        print(f"Warning: {IGNORE_FILE} not found. Using default ignore patterns.")

    spec = PathSpec.from_lines("gitwildmatch", combined_ignore_content.strip().splitlines())
    return spec

def should_ignore_dir(dir_name, spec):
    """
    Checks if a directory should be ignored based on its name and the PathSpec.
    """
    # Check for exact match first (e.g., ".git")
    if spec.match_file(dir_name):
        return True

    # Check for patterns that would match subdirectories of ignored directories
    # (e.g., .git/objects, .git/refs)
    if spec.match_file(os.path.join(".", dir_name)):
        return True

    return False

def index_files(project_name="default"):
    """
    索引当前目录下的文件（包括子文件夹）。
    自动排除黑名单中的文件夹和 .ignore 文件中匹配的文件。
    """

    # 加载忽略模式
    spec = load_ignore_patterns()

    # 获取文件总数用于进度显示
    total_files = 0
    for root, dirs, files in os.walk("."):
        # Filter out blacklisted directories
        dirs[:] = [d for d in dirs if not should_ignore_dir(d, spec)]
        total_files += len(files)

    with tqdm(total=total_files, desc="索引文件") as pbar:
        # 遍历目录
        for root, dirs, files in os.walk("."):
            # Filter out blacklisted directories
            dirs[:] = [d for d in dirs if not should_ignore_dir(d, spec)]

            for file in files:
                file_path = os.path.join(root, file)

                # 过滤文件
                if not spec.match_file(file_path):
                    try:
                        # 上传文件
                        with open(file_path, "rb") as f:
                            response = requests.post(
                                f"{SERVER_URL}/index_files",
                                files={"files": f},
                                data={"project_name": project_name},
                            )

                        # 检查响应状态码
                        response.raise_for_status()
                        print(f"文件 {file_path} 索引成功！")
                    except requests.exceptions.RequestException as e:
                        print(f"文件 {file_path} 索引失败：{e}")
                    except FileNotFoundError:
                        print(f"Error: File {file_path} not found.")
                    finally:
                        pbar.update(1)


if __name__ == "__main__":
    index_files()
