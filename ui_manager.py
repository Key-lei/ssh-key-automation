"""
用户界面管理模块
提供跨平台的用户界面和交互功能
"""
import os
import sys
import platform
import socket
import time
from typing import Dict, Optional
import getpass
from config import SSH_CONFIG, PATH_CONFIG
import shutil

class Colors:
    """终端颜色定义"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class UIManager:
    def __init__(self):
        """初始化用户界面管理器"""
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.ssh_dir = self._get_ssh_dir()
        # Windows系统启用彩色输出
        if self.is_windows:
            os.system('color')
        self.terminal_width = shutil.get_terminal_size().columns

    def _get_ssh_dir(self) -> str:
        """获取SSH配置目录的平台相关路径"""
        if self.is_windows:
            return os.path.expandvars(r"%USERPROFILE%\.ssh")
        return os.path.expanduser("~/.ssh")

    def clear_screen(self):
        """清除屏幕"""
        os.system('cls' if self.is_windows else 'clear')

    def show_banner(self):
        """显示欢迎界面"""
        self.clear_screen()
        banner = [
            "╔══════════════════════════════════════════════════════════╗",
            "║                SSH密钥自动化部署工具                     ║",
            "╚══════════════════════════════════════════════════════════╝"
        ]
        
        # 居中显示banner
        for line in banner:
            padding = (self.terminal_width - len(line)) // 2
            print(" " * padding + Colors.BOLD + Colors.BLUE + line + Colors.ENDC)
        
        print(f"\n{Colors.BOLD}系统信息:{Colors.ENDC}")
        print(f"├─ 系统类型: {Colors.GREEN}{self.system}{Colors.ENDC}")
        print(f"├─ SSH目录: {Colors.GREEN}{self.ssh_dir}{Colors.ENDC}")
        print(f"└─ Python版本: {Colors.GREEN}{platform.python_version()}{Colors.ENDC}")
        print("\n" + "═" * self.terminal_width)

    def show_menu(self) -> str:
        """显示主菜单并获取用户选择"""
        menu_items = [
            ("1", "检测环境配置", "检查Python版本、依赖包和权限"),
            ("2", "测试远程连接", "测试网络连接和SSH服务"),
            ("3", "部署SSH密钥", "生成并部署SSH密钥"),
            ("4", "检查远程服务器配置", "检查SSH服务和安全设置"),
            ("5", "查看当前配置", "显示当前的连接配置"),
            ("6", "修改配置", "更新服务器连接信息"),
            ("0", "退出程序", "保存配置并退出")
        ]
        
        print(f"\n{Colors.BOLD}可用操作：{Colors.ENDC}")
        for num, title, desc in menu_items:
            print(f"{Colors.BLUE}[{num}]{Colors.ENDC} {Colors.BOLD}{title}{Colors.ENDC}")
            print(f"    {Colors.WARNING}{desc}{Colors.ENDC}")
        
        while True:
            choice = input(f"\n{Colors.BOLD}请输入选项编号 [0-6]: {Colors.ENDC}").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6']:
                return choice
            print(f"{Colors.FAIL}无效的选项，请重新输入！{Colors.ENDC}")

    def get_connection_info(self) -> Dict[str, any]:
        """获取连接信息"""
        print(f"\n{Colors.BOLD}远程服务器配置{Colors.ENDC}")
        print("─" * self.terminal_width)
        
        hostname = input(f"服务器地址 {Colors.WARNING}(当前: {SSH_CONFIG['remote_host'] or '未设置'}){Colors.ENDC}: ").strip()
        hostname = hostname or SSH_CONFIG['remote_host']
        
        port_str = input(f"SSH端口 {Colors.WARNING}(当前: {SSH_CONFIG['remote_port']}){Colors.ENDC}: ").strip()
        port = int(port_str) if port_str.isdigit() else SSH_CONFIG['remote_port']
        
        username = input(f"用户名 {Colors.WARNING}(当前: {SSH_CONFIG['username'] or '未设置'}){Colors.ENDC}: ").strip()
        username = username or SSH_CONFIG['username']
        
        password = getpass.getpass(f"密码 {Colors.WARNING}(留空使用当前配置){Colors.ENDC}: ").strip()
        password = password or SSH_CONFIG['password']
        
        print("─" * self.terminal_width)
        return {
            'hostname': hostname,
            'port': port,
            'username': username,
            'password': password
        }

    def check_environment(self) -> bool:
        """检查环境配置"""
        print(f"\n{Colors.BOLD}环境检测{Colors.ENDC}")
        print("─" * self.terminal_width)
        
        checks = [
            ("Python版本检查", self._check_python_version()),
            ("SSH目录权限检查", self._check_ssh_dir_permissions()),
            ("系统依赖检查", self._check_system_dependencies())
        ]
        
        all_passed = True
        for name, passed in checks:
            self.show_progress(f"正在检查 {name}", 1)
            status = f"{Colors.GREEN}✓{Colors.ENDC}" if passed else f"{Colors.FAIL}✗{Colors.ENDC}"
            print(f"{status} {name}")
            all_passed = all_passed and passed
        
        print("─" * self.terminal_width)
        return all_passed

    def show_progress_bar(self, iteration, total, prefix='', suffix='', length=50):
        """显示进度条"""
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = '█' * filled_length + '░' * (length - filled_length)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
        if iteration == total:
            print()

    def test_connection(self, conn_info: Dict[str, any]) -> bool:
        """测试远程连接"""
        print(f"\n{Colors.BOLD}连接测试{Colors.ENDC}")
        print("─" * self.terminal_width)
        
        try:
            print(f"正在连接 {Colors.BLUE}{conn_info['username']}@{conn_info['hostname']}:{conn_info['port']}{Colors.ENDC}")
            
            # 显示连接进度
            for i in range(101):
                self.show_progress_bar(i, 100, prefix='连接进度:', suffix='完成')
                time.sleep(0.01)
            
            # 测试TCP连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((conn_info['hostname'], conn_info['port']))
            sock.close()
            
            if result != 0:
                print(f"{Colors.FAIL}✗ 无法连接到服务器，请检查网络连接和防火墙设置。{Colors.ENDC}")
                return False
            
            print(f"{Colors.GREEN}✓ 网络连接正常{Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}✗ 连接测试失败: {str(e)}{Colors.ENDC}")
            return False

    def show_progress(self, message: str, duration: int = 3):
        """显示进度动画"""
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        for i in range(duration * 10):
            print(f"\r{Colors.BLUE}{spinner[i % len(spinner)]}{Colors.ENDC} {message}", end='', flush=True)
            time.sleep(0.1)
        print()

    def show_current_config(self):
        """显示当前配置"""
        print(f"\n{Colors.BOLD}当前配置信息{Colors.ENDC}")
        print("─" * self.terminal_width)
        
        configs = [
            ("远程服务器", SSH_CONFIG['remote_host'] or '未设置'),
            ("SSH端口", SSH_CONFIG['remote_port']),
            ("用户名", SSH_CONFIG['username'] or '未设置'),
            ("SSH目录", self.ssh_dir)
        ]
        
        for key, value in configs:
            print(f"{Colors.BLUE}{key}:{Colors.ENDC} {Colors.GREEN}{value}{Colors.ENDC}")
        
        print("─" * self.terminal_width)

    def show_platform_specific_info(self):
        """显示平台特定信息"""
        print(f"\n{Colors.BOLD}平台特定信息{Colors.ENDC}")
        if self.is_windows:
            print(f"{Colors.WARNING}Windows系统注意事项：{Colors.ENDC}")
            print("1. 确保PowerShell或CMD具有管理员权限")
            print("2. SSH密钥存储在 %USERPROFILE%\\.ssh 目录")
            print("3. 如遇到权限问题，请检查文件夹访问权限")
        else:
            print(f"{Colors.WARNING}Unix/Linux/MacOS系统注意事项：{Colors.ENDC}")
            print("1. 确保~/.ssh目录权限为700")
            print("2. 确保私钥文件权限为600")
            print("3. 确保public key文件权限为644")
            print(f"4. SSH密钥存储在 {self.ssh_dir} 目录")
        print("─" * self.terminal_width)

    def _check_python_version(self) -> bool:
        """检查Python版本"""
        return sys.version_info >= (3, 6)

    def _check_ssh_dir_permissions(self) -> bool:
        """检查SSH目录权限"""
        try:
            if not os.path.exists(self.ssh_dir):
                os.makedirs(self.ssh_dir, mode=0o700)
            return True
        except Exception:
            return False

    def _check_system_dependencies(self) -> bool:
        """检查系统依赖"""
        try:
            import paramiko
            import cryptography
            import bcrypt
            return True
        except ImportError:
            return False

    def check_remote_config(self, ssh_client) -> bool:
        """检查远程服务器配置"""
        print("\n正在检查远程服务器配置...")
        
        try:
            # 检查 sshd_config
            stdin, stdout, stderr = ssh_client.exec_command(
                "grep -E '^PubkeyAuthentication|^PasswordAuthentication' /etc/ssh/sshd_config"
            )
            config = stdout.read().decode()
            
            checks = {
                "PubkeyAuthentication": ("yes" in config.lower(), "是否启用公钥认证"),
                "PasswordAuthentication": ("yes" in config.lower(), "是否启用密码认证")
            }
            
            all_passed = True
            for key, (passed, desc) in checks.items():
                status = "✅" if passed else "❌"
                print(f"{status} {desc} ({key})")
                all_passed = all_passed and passed
            
            return all_passed
            
        except Exception as e:
            print(f"❌ 检查失败: {str(e)}")
            return False 