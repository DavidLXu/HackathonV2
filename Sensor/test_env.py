#!/usr/bin/env python3
"""
测试虚拟环境和依赖
"""

import sys
import os
import subprocess

def test_virtual_environment():
    """测试虚拟环境"""
    print("🔍 检查虚拟环境...")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 当前在虚拟环境中")
        print(f"   虚拟环境路径: {sys.prefix}")
    else:
        print("⚠️  当前不在虚拟环境中")
    
    # 检查Python路径
    print(f"   Python路径: {sys.executable}")

def test_dependencies():
    """测试依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        'flask',
        'dashscope', 
        'requests',
        'RPi.GPIO'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    else:
        print("\n✅ 所有依赖包都已安装")
        return True

def test_gpio_access():
    """测试GPIO访问权限"""
    print("\n🔌 检查GPIO访问权限...")
    
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.cleanup()
        print("✅ GPIO访问正常")
        return True
    except Exception as e:
        print(f"❌ GPIO访问失败: {e}")
        print("可能需要添加用户到gpio组: sudo usermod -a -G gpio $USER")
        return False

def test_web_server():
    """测试Web服务器"""
    print("\n🌐 检查Web服务器...")
    
    try:
        import requests
        response = requests.get('http://localhost:8080/api/fridge-status', timeout=3)
        if response.status_code == 200:
            print("✅ Web服务器运行正常")
            return True
        else:
            print(f"⚠️  Web服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Web服务器")
        print("请确保Web服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ Web服务器测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 智慧冰箱系统环境测试")
    print("=" * 50)
    
    # 测试虚拟环境
    test_virtual_environment()
    
    # 测试依赖包
    deps_ok = test_dependencies()
    
    # 测试GPIO
    gpio_ok = test_gpio_access()
    
    # 测试Web服务器
    web_ok = test_web_server()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   依赖包: {'✅' if deps_ok else '❌'}")
    print(f"   GPIO访问: {'✅' if gpio_ok else '❌'}")
    print(f"   Web服务器: {'✅' if web_ok else '❌'}")
    
    if deps_ok and gpio_ok:
        print("\n🎉 环境测试通过！可以启动系统了。")
        print("运行命令: python start_system.py")
    else:
        print("\n⚠️  环境测试未通过，请解决上述问题后再启动系统。")

if __name__ == "__main__":
    main() 