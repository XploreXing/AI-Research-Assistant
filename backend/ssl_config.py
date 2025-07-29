"""
SSL 配置模块 - 简化版本
确保在所有网络请求之前正确配置 SSL 设置
"""

import ssl
import os

def configure_ssl():
    """配置 SSL 设置以解决证书验证问题"""
    try:
        import certifi
        cert_path = certifi.where()
        # print(f"使用证书文件: {cert_path}")
        
        # 设置环境变量指向正确的证书文件
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['CURL_CA_BUNDLE'] = cert_path
        
        # 设置默认的 SSL 上下文使用 certifi 的证书
        ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=cert_path)
        
        # 启用证书验证
        os.environ['PYTHONHTTPSVERIFY'] = '1'
        
        print("SSL 配置已应用")
        
    except ImportError:
        print("certifi 不可用，使用系统默认证书")
        print("请检查是否安装了 certifi 包")



# 在模块导入时自动配置 SSL
configure_ssl()
