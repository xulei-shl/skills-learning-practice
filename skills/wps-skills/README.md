# WPS文件上传脚本

基于WPS开放平台API的文件上传工具，支持单文件上传和批量上传。

## 脚本说明

| 脚本文件 | 说明 | 授权方式 |
|---------|------|---------|
| `wps_upload.py` | 基础上传脚本 | 应用授权（需在WPS开放平台后台配置权限） |
| `wps_upload_oauth.py` | OAuth2用户授权版本 | 用户授权（推荐使用） |
| `wps_upload_batch.py` | 批量上传工具 | 需配合对应授权方式使用 |

> **推荐使用 `wps_upload_oauth.py`** - 应用授权需要WPS开放平台管理员配置权限，而OAuth2用户授权无需后台配置即可使用。

## 功能特性

- 支持单文件上传
- 支持批量文件上传
- 支持目录上传（递归可选）
- 自动计算文件哈希值（MD5/SHA256）
- 文件名冲突处理（重命名/覆盖/失败）
- 详细的上传进度和结果显示

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制配置文件模板：
```bash
copy config.example.py config.py
```

2. 编辑 `config.py`，填入你的WPS开放平台应用信息：

```python
APP_ID = "your_app_id_here"
APP_SECRET = "your_app_secret_here"
DRIVE_ID = "default"  # 或具体的网盘ID
PARENT_ID = "root"    # 或具体的文件夹ID
```

## 使用方法

### 方法1: 使用基础脚本 (wps_upload.py)

```bash
python wps_upload.py
```

运行后会提示输入文件路径。

### 方法2: 使用批量上传脚本 (wps_upload_batch.py)

```bash
# 上传单个文件
python wps_upload_batch.py file1.docx

# 上传多个文件
python wps_upload_batch.py file1.docx file2.pdf

# 上传整个目录
python wps_upload_batch.py -d "C:\Documents"

# 递归上传目录
python wps_upload_batch.py -d "C:\Documents" -r

# 指定文件类型
python wps_upload_batch.py -d "C:\Documents" -p "*.pdf"

# 交互模式
python wps_upload_batch.py
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `files` | 要上传的文件路径 |
| `-d, --directory` | 上传整个目录 |
| `-r, --recursive` | 递归上传子目录 |
| `-p, --pattern` | 文件匹配模式 (默认: *) |
| `-c, --config` | 配置文件路径 (默认: config.py) |
| `--conflict` | 文件名冲突处理方式 (fail/rename/overwrite/replace) |

## API说明

### 上传流程

上传文件分为三个步骤：

1. **请求文件上传信息** - 获取上传地址和upload_id
2. **上传实体文件** - 将文件内容上传到云存储
3. **提交上传完成** - 提交上传信息完成整个流程

### 获取drive_id和parent_id

- `drive_id`: 网盘ID，默认为 "default"
- `parent_id`: 父文件夹ID，根目录为 "root"

如需获取具体的ID值，请参考WPS开放平台文档。

## 示例

```python
from wps_upload import WPSFileUploader

# 创建上传器
uploader = WPSFileUploader(
    app_id="your_app_id",
    app_secret="your_app_secret",
    drive_id="default",
    parent_id="root"
)

# 上传文件
result = uploader.upload_file("example.docx")
print(f"上传成功! 文件ID: {result['id']}")
```

## 错误处理

- 文件不存在：会抛出 `FileNotFoundError`
- API调用失败：会抛出包含错误信息的 `Exception`
- Token过期：脚本会自动重新获取token

## 注意事项

1. 确保WPS开放平台应用有 `kso.file.readwrite` 权限
2. access_token有效期为2小时，脚本会自动管理
3. 大文件上传可能需要较长时间，请耐心等待
4. 文件名冲突时，默认会自动重命名

## 许可

MIT License
