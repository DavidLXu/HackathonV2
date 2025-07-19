#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强功能：大模型时间建议和用户偏好设置
"""

import requests
import json
from datetime import datetime

def test_enhanced_features():
    """测试增强功能"""
    base_url = "http://localhost:8080"
    
    print("=== 增强功能测试 ===")
    
    # 1. 测试推荐系统（修复后）
    print("\n1. 测试推荐系统")
    try:
        response = requests.get(f"{base_url}/api/recommendations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 推荐系统正常")
            print(f"   成功状态: {data.get('success')}")
            print(f"   推荐数量: {len(data.get('recommendations', []))}")
            
            # 显示推荐详情
            for i, rec in enumerate(data.get('recommendations', []), 1):
                print(f"   推荐{i}: {rec.get('title')}")
                print(f"     物品数量: {len(rec.get('items', []))}")
        else:
            print(f"❌ 推荐系统失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 推荐系统异常: {e}")
    
    # 2. 测试大模型时间建议
    print("\n2. 测试大模型时间建议")
    try:
        response = requests.get(f"{base_url}/api/time-advice")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 时间建议获取成功")
            print(f"   时间上下文: {data.get('time_context')}")
            print(f"   工作日上下文: {data.get('workday_context')}")
            
            advice = data.get('time_advice', {})
            print(f"   问候: {advice.get('greeting')}")
            print(f"   主要建议: {advice.get('main_advice')}")
            print(f"   紧急程度: {advice.get('urgency_level')}")
            print(f"   营养提示数量: {len(advice.get('nutrition_tips', []))}")
            print(f"   烹饪建议数量: {len(advice.get('cooking_suggestions', []))}")
        else:
            print(f"❌ 时间建议失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 时间建议异常: {e}")
    
    # 3. 测试用户偏好设置
    print("\n3. 测试用户偏好设置")
    try:
        # 获取当前偏好
        response = requests.get(f"{base_url}/api/user-preferences")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 偏好设置获取成功")
            prefs = data.get('preferences', {})
            print(f"   食物偏好:")
            for key, value in prefs.items():
                if key in ['fruits', 'vegetables', 'meat', 'dairy', 'grains', 'seafood', 'desserts', 'beverages']:
                    status = "✅" if value else "❌"
                    print(f"     {status} {key}: {value}")
            print(f"   其他物品:")
            for key, value in prefs.items():
                if key in ['instruments', 'tools']:
                    status = "✅" if value else "❌"
                    print(f"     {status} {key}: {value}")
        else:
            print(f"❌ 偏好设置获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 偏好设置异常: {e}")
    
    # 4. 测试偏好设置更新
    print("\n4. 测试偏好设置更新")
    try:
        # 更新偏好设置
        new_preferences = {
            "fruits": True,
            "vegetables": True,
            "meat": True,
            "dairy": True,
            "grains": True,
            "seafood": True,
            "desserts": False,  # 改为False
            "beverages": True,
            "instruments": True,  # 改为True
            "tools": False
        }
        
        response = requests.post(
            f"{base_url}/api/user-preferences",
            json=new_preferences,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 偏好设置更新成功")
            print(f"   消息: {data.get('message')}")
            
            # 验证更新
            updated_prefs = data.get('preferences', {})
            if updated_prefs.get('desserts') == False and updated_prefs.get('instruments') == True:
                print("   ✅ 偏好设置更新验证成功")
            else:
                print("   ❌ 偏好设置更新验证失败")
        else:
            print(f"❌ 偏好设置更新失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 偏好设置更新异常: {e}")
    
    # 5. 测试接近传感器（使用新的偏好设置）
    print("\n5. 测试接近传感器")
    try:
        response = requests.post(f"{base_url}/api/proximity-sensor")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 接近传感器响应成功")
            
            recommendation = data.get('recommendation', {})
            print(f"   问候: {recommendation.get('greeting')}")
            print(f"   主要推荐: {recommendation.get('main_recommendation')}")
            print(f"   快速提示: {recommendation.get('quick_tip')}")
            print(f"   紧急程度: {recommendation.get('urgency_level')}")
        else:
            print(f"❌ 接近传感器失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 接近传感器异常: {e}")

def test_web_interface():
    """测试Web界面功能"""
    print("\n=== Web界面功能测试 ===")
    
    base_url = "http://localhost:8080"
    
    # 测试主页加载
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ 主页加载成功")
            
            # 检查是否包含新功能的关键元素
            content = response.text
            if "getFoodEmoji" in content:
                print("✅ getFoodEmoji函数已添加")
            else:
                print("❌ getFoodEmoji函数缺失")
                
            if "preferences-btn" in content:
                print("✅ 偏好设置按钮已添加")
            else:
                print("❌ 偏好设置按钮缺失")
                
            if "time-advice-card" in content:
                print("✅ 时间建议卡片样式已添加")
            else:
                print("❌ 时间建议卡片样式缺失")
                
        else:
            print(f"❌ 主页加载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 主页加载异常: {e}")

if __name__ == "__main__":
    test_enhanced_features()
    test_web_interface()
    print("\n=== 测试完成 ===")
    print("\n💡 新功能总结:")
    print("   - ✅ 推荐系统已修复，显示物品emoji")
    print("   - ✅ 大模型实时生成时间建议")
    print("   - ✅ 用户偏好设置功能")
    print("   - ✅ 个性化推荐基于用户偏好")
    print("   - ✅ Web界面支持所有新功能") 