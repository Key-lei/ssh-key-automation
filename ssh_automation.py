"""
SSH自动化部署工具
提供用户友好的界面，支持SSH密钥的生成、部署和验证
"""
import os
import sys
import time
from ssh_utils import SSHKeyManager
from ui_manager import UIManager
import paramiko
from config import SSH_CONFIG
import logging

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SSHAutomation:
    def __init__(self):
        """初始化SSH自动化工具"""
        self.ui = UIManager()
        self.ssh_manager = SSHKeyManager()
        self.conn_info = None

    def run(self):
        """运行主程序"""
        try:
            self.ui.show_banner()
            self.ui.show_platform_specific_info()
            
            while True:
                choice = self.ui.show_menu()
                
                if choice == '0':
                    print("\n感谢使用！再见！")
                    break
                    
                self.handle_choice(choice)
                
                input("\n按回车键继续...")
                self.ui.show_banner()
                
        except KeyboardInterrupt:
            print("\n\n程序已被用户中断。")
        except Exception as e:
            logger.error(f"发生错误: {str(e)}")
            print("\n程序遇到错误，请查看日志获取详细信息。")

    def handle_choice(self, choice: str):
        """处理用户菜单选择"""
        handlers = {
            '1': self.check_environment,
            '2': self.test_connection,
            '3': self.deploy_ssh_key,
            '4': self.check_remote_config,
            '5': self.show_current_config,
            '6': self.update_config
        }
        
        handler = handlers.get(choice)
        if handler:
            handler()

    def check_environment(self):
        """检查环境配置"""
        self.ui.check_environment()

    def test_connection(self):
        """测试远程连接"""
        if not self.conn_info:
            self.conn_info = self.ui.get_connection_info()
        
        if self.ui.test_connection(self.conn_info):
            try:
                # 尝试SSH连接
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    self.conn_info['hostname'],
                    self.conn_info['port'],
                    self.conn_info['username'],
                    self.conn_info['password']
                )
                print("✅ SSH连接测试成功")
                ssh.close()
            except Exception as e:
                print(f"❌ SSH连接失败: {str(e)}")

    def deploy_ssh_key(self):
        """部署SSH密钥"""
        if not self.conn_info:
            self.conn_info = self.ui.get_connection_info()
        
        self.ui.show_progress("正在生成密钥对")
        
        if self.ssh_manager.deploy_public_key(
            self.conn_info['hostname'],
            self.conn_info['username'],
            self.conn_info['password'],
            self.conn_info['port']
        ):
            self.ui.show_progress("正在验证部署")
            if self.ssh_manager.verify_connection(
                self.conn_info['hostname'],
                self.conn_info['username'],
                self.conn_info['port']
            ):
                print("\n✅ SSH密钥部署成功！")
                print(f"\n使用以下命令登录服务器：")
                print(f"ssh {self.conn_info['username']}@{self.conn_info['hostname']}" + 
                      (f" -p {self.conn_info['port']}" if self.conn_info['port'] != 22 else ""))
            else:
                print("\n❌ SSH密钥认证验证失败")
        else:
            print("\n❌ SSH密钥部署失败")

    def check_remote_config(self):
        """检查远程服务器配置"""
        if not self.conn_info:
            self.conn_info = self.ui.get_connection_info()
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.conn_info['hostname'],
                self.conn_info['port'],
                self.conn_info['username'],
                self.conn_info['password']
            )
            
            self.ui.check_remote_config(ssh)
            ssh.close()
            
        except Exception as e:
            print(f"❌ 无法连接到远程服务器: {str(e)}")

    def show_current_config(self):
        """显示当前配置"""
        self.ui.show_current_config()

    def update_config(self):
        """更新配置"""
        self.conn_info = self.ui.get_connection_info()
        # 更新全局配置
        SSH_CONFIG.update({
            'remote_host': self.conn_info['hostname'],
            'remote_port': self.conn_info['port'],
            'username': self.conn_info['username'],
            'password': self.conn_info['password']
        })
        print("\n✅ 配置已更新")

def main():
    """程序入口"""
    automation = SSHAutomation()
    automation.run()

if __name__ == "__main__":
    main() 