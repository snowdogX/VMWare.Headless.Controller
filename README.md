# VMware 无界面虚拟机管理器

一个基于 VMware REST API 的 Python 虚拟机管理工具，支持虚拟机的启动、关闭、状态查询等功能。

## 功能特性

- ✅ **图形界面（GUI）** - 用户友好的图形界面
- ✅ **命令行界面（CLI）** - 支持脚本自动化
- ✅ 列出所有虚拟机
- ✅ 查看虚拟机详细状态
- ✅ 启动虚拟机
- ✅ 强制关闭虚拟机
- ✅ 优雅关闭虚拟机（需要 VMware Tools）
- ✅ 挂起虚拟机
- ✅ 自动刷新虚拟机状态
- ✅ 实时操作日志
- ✅ 彩色状态显示

## 系统要求

- Python 3.7+
- VMware Workstation Pro 或 VMware Player
- 已启用 VMware REST API

## 启用 VMware REST API

### Windows

1. 编辑 VMware 配置文件（通常位于 `C:\ProgramData\VMware\VMware Workstation\config.ini`）
2. 添加以下配置：

```ini
[WSSDK]
enabled = "TRUE"
port = "8697"
```

3. 重启 VMware Workstation

### Linux

1. 编辑配置文件 `~/.vmware/preferences`
2. 添加以下配置：

```
webServer.enabled = "TRUE"
webServer.port = "8697"
```

3. 重启 VMware

## 安装

1. 克隆或下载此项目

```bash
git clone <repository-url>
cd VMWare.Headless.Controller
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置连接信息

```bash
# 复制配置文件模板
cp config.example.yaml config.yaml

# 编辑配置文件，填入你的 VMware 连接信息
# 使用你喜欢的编辑器编辑 config.yaml
```

## 配置说明

编辑 `config.yaml` 文件：

```yaml
vmware:
  host: "localhost"          # VMware REST API 地址
  port: 8697                 # VMware REST API 端口
  username: "your_username"  # 用户名
  password: "your_password"  # 密码
  verify_ssl: false          # 是否验证 SSL 证书
  timeout: 30                # 连接超时时间（秒）
```

## 使用方法

### 图形界面（推荐）

#### Windows

双击运行 `start_gui.bat` 文件，或者在命令行中执行：

```bash
.\venv\Scripts\python.exe gui.py
```

#### Linux/Mac

```bash
./venv/bin/python gui.py
```

#### GUI 功能说明

- **虚拟机列表**：显示所有虚拟机及其状态（绿色=运行中，红色=已关闭，橙色=已挂起）
- **刷新按钮**：手动刷新虚拟机列表
- **自动刷新**：勾选后每 5 秒自动刷新虚拟机状态
- **虚拟机信息**：选择虚拟机后显示详细信息
- **控制按钮**：
  - ▶ 启动：启动选中的虚拟机
  - ⏹ 强制关闭：立即关闭虚拟机（可能导致数据丢失）
  - 🔌 优雅关闭：通过 VMware Tools 优雅关闭虚拟机
  - ⏸ 挂起：挂起虚拟机
- **操作日志**：显示所有操作的实时日志

### 命令行界面

#### 测试连接

```bash
python main.py test
```

### 列出所有虚拟机

```bash
python main.py list
```

### 查看虚拟机状态

```bash
python main.py status <vm_id>
```

### 启动虚拟机

```bash
python main.py start <vm_id>
```

### 强制关闭虚拟机

```bash
python main.py stop <vm_id>
```

### 优雅关闭虚拟机

需要虚拟机安装了 VMware Tools：

```bash
python main.py shutdown <vm_id>
```

### 挂起虚拟机

```bash
python main.py suspend <vm_id>
```

### 使用自定义配置文件

```bash
python main.py -c /path/to/config.yaml list
```

## 示例

```bash
# 测试 API 连接
$ python main.py test
ℹ 正在加载配置文件...
✓ 配置文件加载成功
ℹ 正在连接 VMware REST API...
✓ API 连接成功
✓ API 连接测试成功

# 列出所有虚拟机
$ python main.py list
ℹ 正在加载配置文件...
✓ 配置文件加载成功
ℹ 正在连接 VMware REST API...
✓ API 连接成功
+-------------+---------------------------+---------+
| 虚拟机 ID   | 路径                      | 状态    |
+=============+===========================+=========+
| VM001       | /path/to/vm1.vmx          | 运行中  |
+-------------+---------------------------+---------+
| VM002       | /path/to/vm2.vmx          | 已关闭  |
+-------------+---------------------------+---------+

# 启动虚拟机
$ python main.py start VM002
ℹ 正在加载配置文件...
✓ 配置文件加载成功
ℹ 正在连接 VMware REST API...
✓ API 连接成功
ℹ 正在启动虚拟机 VM002...
✓ 虚拟机 VM002 已启动
```

## 项目结构

```
VMWare.Headless.Controller/
├── gui.py                  # 图形界面程序
├── main.py                 # 命令行程序入口
├── vmware_client.py        # VMware REST API 客户端
├── vm_manager.py           # 虚拟机管理器
├── config_loader.py        # 配置文件加载器
├── start_gui.bat           # Windows GUI 启动脚本
├── requirements.txt        # Python 依赖
├── config.example.yaml     # 配置文件示例
├── config.yaml            # 实际配置文件（需自行创建）
└── README.md              # 项目说明文档
```

## 故障排除

### 连接失败

1. 确认 VMware REST API 已启用
2. 检查端口是否正确（默认 8697）
3. 确认用户名和密码正确
4. 检查防火墙设置

### 虚拟机 ID 获取

使用 `python main.py list` 命令查看所有虚拟机的 ID

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

