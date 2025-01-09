"""
SSH自动化配置文件
包含连接远程服务器所需的基本配置信息
"""

# SSH连接配置
SSH_CONFIG = {
    'remote_host': '',  # 远程服务器IP或域名
    'remote_port': 22,  # SSH端口号
    'username': '',     # 用户名
    'password': ''      # 密码
}

# SSH密钥配置
KEY_CONFIG = {
    'key_filename': 'id_rsa',     # 密钥文件名
    'key_type': 'rsa',           # 密钥类型
    'key_bits': 4096,            # 密钥位数（改为4096位）
    'key_comment': ''            # 密钥注释
}

# 文件路径配置
PATH_CONFIG = {
    'ssh_dir': '~/.ssh',                    # SSH配置目录
    'authorized_keys': '~/.ssh/authorized_keys'  # 授权密钥文件
}

# 权限配置
PERMISSION_CONFIG = {
    'ssh_dir': 0o700,           # .ssh目录权限
    'private_key': 0o600,       # 私钥文件权限
    'public_key': 0o644,        # 公钥文件权限
    'authorized_keys': 0o600    # authorized_keys文件权限
} 