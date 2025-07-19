#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试推荐系统功能
"""

import requests
import json
import time
from datetime import datetime

def test_recommendation_system():
    """测试推荐系统"""
    base_url = "http://localhost:8080"
    
    print("=== 推荐系统测试 ===")
    
    # 1. 测试获取推荐
    print("\n1. 测试获取推荐")
    try:
        response = requests.get(f"{base_url}/api/recommendations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 推荐获取成功")
            print(f"   成功状态: {data.get('success')}")
            print(f"   推荐数量: {len(data.get('recommendations', []))}")
            print(f"   更新时间: {data.get('last_update')}")
            
            # 显示推荐详情
            for i, rec in enumerate(data.get('recommendations', []), 1):
                print(f"   推荐{i}: {rec.get('title')}")
                print(f"     类型: {rec.get('type')}")
                print(f"     消息: {rec.get('message')}")
                print(f"     行动: {rec.get('action')}")
        else:
            print(f"❌ 推荐获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 推荐获取异常: {e}")
    
    # 2. 测试接近传感器
    print("\n2. 测试接近传感器")
    try:
        response = requests.post(f"{base_url}/api/proximity-sensor")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 接近传感器响应成功")
            print(f"   成功状态: {data.get('success')}")
            print(f"   时间上下文: {data.get('time_context')}")
            print(f"   工作日上下文: {data.get('workday_context')}")
            
            recommendation = data.get('recommendation', {})
            print(f"   问候: {recommendation.get('greeting')}")
            print(f"   主要推荐: {recommendation.get('main_recommendation')}")
            print(f"   快速提示: {recommendation.get('quick_tip')}")
            print(f"   紧急程度: {recommendation.get('urgency_level')}")
        else:
            print(f"❌ 接近传感器失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 接近传感器异常: {e}")
    
    # 3. 测试冰箱状态
    print("\n3. 测试冰箱状态")
    try:
        response = requests.get(f"{base_url}/api/fridge-status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 冰箱状态获取成功")
            print(f"   成功状态: {data.get('success')}")
            print(f"   物品数量: {len(data.get('items', []))}")
            
            stats = data.get('stats', {})
            print(f"   总物品数: {stats.get('total_items', 0)}")
            print(f"   新鲜物品: {stats.get('fresh_items', 0)}")
            print(f"   长期保存: {stats.get('long_term_items', 0)}")
            print(f"   即将过期: {stats.get('expiring_soon', 0)}")
            print(f"   已过期: {stats.get('expired_items', 0)}")
        else:
            print(f"❌ 冰箱状态获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 冰箱状态获取异常: {e}")
    
    # 4. 测试推荐刷新
    print("\n4. 测试推荐刷新")
    try:
        # 获取第一次推荐
        response1 = requests.get(f"{base_url}/api/recommendations")
        data1 = response1.json()
        time1 = data1.get('last_update')
        print(f"   第一次更新时间: {time1}")
        
        # 等待几秒
        time.sleep(3)
        
        # 获取第二次推荐
        response2 = requests.get(f"{base_url}/api/recommendations")
        data2 = response2.json()
        time2 = data2.get('last_update')
        print(f"   第二次更新时间: {time2}")
        
        if time1 == time2:
            print("   ✅ 推荐缓存正常工作（时间相同表示使用了缓存）")
        else:
            print("   ⚠️  推荐已更新（时间不同表示重新生成了推荐）")
            
    except Exception as e:
        print(f"❌ 推荐刷新测试异常: {e}")

def test_recommendation_consistency():
    """测试推荐一致性"""
    print("\n=== 推荐一致性测试 ===")
    
    base_url = "http://localhost:8080"
    
    try:
        # 连续获取推荐，检查是否一致
        recommendations = []
        for i in range(3):
            response = requests.get(f"{base_url}/api/recommendations")
            if response.status_code == 200:
                data = response.json()
                recommendations.append(data)
                print(f"   第{i+1}次推荐数量: {len(data.get('recommendations', []))}")
            time.sleep(1)
        
        # 检查推荐数量是否一致
        rec_counts = [len(rec.get('recommendations', [])) for rec in recommendations]
        if len(set(rec_counts)) == 1:
            print("   ✅ 推荐数量一致")
        else:
            print("   ⚠️  推荐数量不一致")
            
    except Exception as e:
        print(f"❌ 推荐一致性测试异常: {e}")

if __name__ == "__main__":
    test_recommendation_system()
    test_recommendation_consistency()
    print("\n=== 测试完成 ===") 