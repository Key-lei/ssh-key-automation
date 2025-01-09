"""
SSH工具类
提供SSH密钥生成、部署和验证的核心功能
"""
import os
import sys
import paramiko
from pathlib import Path
from typing import Tuple, Optional
import logging
from config import SSH_CONFIG, KEY_CONFIG, PATH_CONFIG, PERMISSION_CONFIG

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SSHKeyManager:
    def __init__(self):
        """初始化SSH密钥管理器"""
        self.ssh_dir = os.path.expanduser(PATH_CONFIG['ssh_dir'])
        self.private_key_path = os.path.join(self.ssh_dir, KEY_CONFIG['key_filename'])
        self.public_key_path = f"{self.private_key_path}.pub"
        
    def ensure_ssh_directory(self) -> None:
        """确保SSH目录存在且权限正确"""
        try:
            if not os.path.exists(self.ssh_dir):
                os.makedirs(self.ssh_dir, mode=PERMISSION_CONFIG['ssh_dir'])
                logger.info(f"创建SSH目录: {self.ssh_dir}")
            os.chmod(self.ssh_dir, PERMISSION_CONFIG['ssh_dir'])
        except Exception as e:
            logger.error(f"创建SSH目录失败: {str(e)}")
            raise

    def generate_key_pair(self) -> Tuple[str, str]:
        """使用系统ssh-keygen生成SSH密钥对"""
        try:
            self.ensure_ssh_directory()
            if os.path.exists(self.private_key_path):
                logger.info("SSH密钥对已存在")
                with open(self.public_key_path, 'r') as f:
                    public_key = f.read().strip()
                return self.private_key_path, public_key

            # 使用ssh-keygen命令生成密钥对
            import subprocess
            cmd = [
                'ssh-keygen',
                '-t', KEY_CONFIG['key_type'],
                '-b', str(KEY_CONFIG['key_bits']),
                '-f', self.private_key_path,
                '-N', ''  # 空密码短语
            ]
            
            if KEY_CONFIG['key_comment']:
                cmd.extend(['-C', KEY_CONFIG['key_comment']])
            
            # 执行ssh-keygen命令
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode != 0:
                raise Exception(f"ssh-keygen失败: {process.stderr}")
            
            # 设置正确的文件权限
            os.chmod(self.private_key_path, PERMISSION_CONFIG['private_key'])
            os.chmod(self.public_key_path, PERMISSION_CONFIG['public_key'])
            
            # 读取生成的公钥
            with open(self.public_key_path, 'r') as f:
                public_key = f.read().strip()
            
            logger.info("成功生成新的SSH密钥对")
            return self.private_key_path, public_key
            
        except Exception as e:
            logger.error(f"生成SSH密钥对失败: {str(e)}")
            raise

    def deploy_public_key(self, hostname: str, username: str, password: str, port: int = 22) -> bool:
        """部署公钥到远程服务器"""
        try:
            _, public_key = self.generate_key_pair()
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, port, username, password)
            
            # 检查并设置用户主目录权限
            commands = [
                # 检查并创建.ssh目录
                'mkdir -p ~/.ssh',
                
                # 设置正确的权限
                'chmod 700 ~',  # 用户主目录权限
                'chmod 700 ~/.ssh',
                'chmod 600 ~/.ssh/authorized_keys 2>/dev/null || true',
                
                # 备份现有的authorized_keys（如果存在）
                'cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak 2>/dev/null || true',
                
                # 添加新的公钥
                f'echo "{public_key}" >> ~/.ssh/authorized_keys',
                
                # 设置最终权限
                'chmod 600 ~/.ssh/authorized_keys',
                
                # 检查SELinux上下文（如果存在）
                'command -v restorecon >/dev/null && restorecon -R -v ~/.ssh 2>/dev/null || true',
                
                # 显示最终权限以供验证
                'ls -la ~/.ssh/authorized_keys',
                'ls -la ~/.ssh',
                'ls -ld ~'
            ]
            
            # 执行命令并收集输出
            for cmd in commands:
                stdin, stdout, stderr = ssh.exec_command(cmd)
                err = stderr.read().decode().strip()
                out = stdout.read().decode().strip()
                if err:
                    logger.warning(f"执行命令时出现警告: {cmd}\n错误信息: {err}")
                if out:
                    logger.info(f"命令输出: {cmd}\n{out}")
            
            # 验证authorized_keys文件内容
            stdin, stdout, stderr = ssh.exec_command('cat ~/.ssh/authorized_keys')
            content = stdout.read().decode().strip()
            if public_key not in content:
                raise Exception("公钥未能正确写入authorized_keys文件")
            
            ssh.close()
            logger.info("成功部署公钥到远程服务器")
            return True
            
        except Exception as e:
            logger.error(f"部署公钥失败: {str(e)}")
            return False

    def verify_connection(self, hostname: str, username: str, port: int = 22) -> bool:
        """验证SSH密钥认证是否成功"""
        try:
            import subprocess
            # 构建SSH命令
            cmd = [
                'ssh',
                '-i', self.private_key_path,  # 指定私钥
                '-o', 'PasswordAuthentication=no',  # 禁用密码认证
                '-o', 'StrictHostKeyChecking=no',  # 禁用主机密钥检查
                '-o', 'BatchMode=yes',  # 禁用交互式提示
                '-p', str(port),  # 指定端口
                f'{username}@{hostname}',
                'echo "Connection successful"'  # 测试命令
            ]
            
            # 执行SSH连接测试
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10  # 设置超时时间
            )
            
            if process.returncode == 0:
                logger.info("SSH密钥认证验证成功")
                return True
            else:
                logger.error(f"SSH密钥认证验证失败: {process.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("SSH连接超时")
            return False
        except Exception as e:
            logger.error(f"SSH密钥认证验证失败: {str(e)}")
            return False 