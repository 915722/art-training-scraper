#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
山东省艺术培训机构信息采集工具
使用高德地图API采集数据
"""

import requests
import pandas as pd
import time
import re
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import json

class ShandongTrainingScraper:
    def __init__(self, amap_key):
        """
        初始化爬虫
        :param amap_key: 高德地图API密钥
        """
        self.amap_key = amap_key
        self.base_url = "https://restapi.amap.com/v3/place/text"
        
        # 山东省所有地级市
        self.cities = [
            '济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市',
            '潍坊市', '济宁市', '泰安市', '威海市', '日照市', '临沂市',
            '德州市', '聊城市', '滨州市', '菏泽市'
        ]
        
        # 专业类别和对应的搜索关键词
        self.categories = {
            '声乐': ['声乐培训', '唱歌培训', '声乐教学'],
            '器乐': ['器乐培训', '乐器培训'],
            '口才': ['口才培训', '演讲培训', '主持培训'],
            '吉他': ['吉他培训', '吉他教学'],
            '古筝': ['古筝培训', '古筝教学'],
            '二胡': ['二胡培训', '二胡教学'],
            '舞蹈': ['舞蹈培训', '舞蹈学校'],
            '语言': ['语言培训', '语言艺术'],
            '朗诵': ['朗诵培训', '朗诵教学'],
            '拉丁舞': ['拉丁舞培训', '拉丁舞教学'],
            '民族舞': ['民族舞培训', '民族舞教学'],
            '现代舞': ['现代舞培训', '现代舞教学'],
            '美术': ['美术培训', '绘画培训', '美术教学'],
            '书法': ['书法培训', '书法教学']
        }
        
        # 存储所有数据
        self.all_data = {}
        
    def search_poi(self, city, keyword, page=1):
        """
        使用高德地图POI搜索API搜索
        :param city: 城市名称
        :param keyword: 搜索关键词
        :param page: 页码
        :return: 搜索结果
        """
        params = {
            'key': self.amap_key,
            'keywords': keyword,
            'city': city,
            'citylimit': 'true',
            'offset': 20,  # 每页20条
            'page': page,
            'extensions': 'all'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == '1':
                    return data
            return None
        except Exception as e:
            print(f"请求出错: {e}")
            return None
    
    def extract_phone(self, tel_str):
        """
        提取11位手机号
        :param tel_str: 电话字符串
        :return: 手机号列表
        """
        if not tel_str:
            return []
        
        # 匹配11位手机号
        phone_pattern = r'1[3-9]\d{9}'
        phones = re.findall(phone_pattern, tel_str)
        return list(set(phones))  # 去重
    
    def parse_result(self, result, category):
        """
        解析搜索结果
        :param result: API返回的结果
        :param category: 专业类别
        :return: 解析后的数据列表
        """
        data_list = []
        
        if not result or 'pois' not in result:
            return data_list
        
        for poi in result['pois']:
            # 提取基本信息
            name = poi.get('name', '')
            tel = poi.get('tel', '')
            address = poi.get('address', '')
            district = poi.get('adname', '')  # 区县
            cityname = poi.get('cityname', '')
            
            # 提取手机号
            phones = self.extract_phone(tel)
            
            if phones:
                # 如果有多个手机号，每个号码单独一行
                for phone in phones:
                    data_list.append({
                        '城市': f"{cityname}{district}" if district else cityname,
                        '专业': category,
                        '机构名称': name,
                        '手机号': phone
                    })
            else:
                # 没有手机号也记录（方便后续人工补充）
                data_list.append({
                    '城市': f"{cityname}{district}" if district else cityname,
                    '专业': category,
                    '机构名称': name,
                    '手机号': tel if tel else '暂无'
                })
        
        return data_list
    
    def scrape_city(self, city):
        """
        爬取某个城市的所有数据
        :param city: 城市名称
        :return: 该城市的所有数据
        """
        print(f"\n开始爬取 {city} 的数据...")
        city_data = []
        
        for category, keywords in self.categories.items():
            print(f"  正在搜索 {category} 相关机构...")
            
            for keyword in keywords:
                page = 1
                while page <= 10:  # 最多搜索10页
                    result = self.search_poi(city, keyword, page)
                    
                    if result:
                        count = result.get('count', '0')
                        pois = result.get('pois', [])
                        
                        if not pois:
                            break
                        
                        # 解析数据
                        parsed_data = self.parse_result(result, category)
                        city_data.extend(parsed_data)
                        
                        print(f"    {keyword} - 第{page}页: 找到 {len(pois)} 条数据")
                        
                        page += 1
                        time.sleep(0.2)  # 避免请求过快
                    else:
                        break
                
                time.sleep(0.3)
        
        print(f"{city} 爬取完成，共获取 {len(city_data)} 条数据")
        return city_data
    
    def remove_duplicates(self, data):
        """
        去除重复数据
        :param data: 数据列表
        :return: 去重后的数据
        """
        if not data:
            return []
        
        df = pd.DataFrame(data)
        # 根据机构名称和手机号去重
        df_unique = df.drop_duplicates(subset=['机构名称', '手机号'], keep='first')
        return df_unique.to_dict('records')
    
    def scrape_all_cities(self):
        """
        爬取所有城市的数据
        """
        print("=" * 60)
        print("开始采集山东省所有城市的艺术培训机构数据")
        print("=" * 60)
        
        for city in self.cities:
            city_data = self.scrape_city(city)
            # 去重
            city_data = self.remove_duplicates(city_data)
            self.all_data[city] = city_data
            
            # 每个城市之间暂停一下
            time.sleep(1)
        
        print("\n" + "=" * 60)
        print("所有城市数据采集完成！")
        print("=" * 60)
    
    def save_to_excel(self, filename='山东省艺术培训机构数据.xlsx'):
        """
        保存数据到Excel，每个城市一个sheet
        :param filename: 文件名
        """
        print(f"\n正在保存数据到 {filename}...")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for city, data in self.all_data.items():
                if data:
                    df = pd.DataFrame(data)
                    # 清理sheet名称（Excel sheet名称有长度限制）
                    sheet_name = city.replace('市', '')[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"  {city}: {len(data)} 条数据已保存")
        
        print(f"\n数据已成功保存到 {filename}")
        
    def generate_summary(self):
        """
        生成数据统计摘要
        """
        print("\n" + "=" * 60)
        print("数据统计摘要")
        print("=" * 60)
        
        total_count = 0
        for city, data in self.all_data.items():
            count = len(data)
            total_count += count
            print(f"{city:8s}: {count:4d} 条")
        
        print("-" * 60)
        print(f"总计: {total_count} 条数据")
        print("=" * 60)


def main():
    """
    主函数
    """
    print("\n" + "=" * 60)
    print("山东省艺术培训机构信息采集工具")
    print("=" * 60)
    
    # 使用提供的API Key
    amap_key = "d7e3918b8b1582ed4b2fcea4f9bd1b62"
    
    # 创建爬虫实例
    scraper = ShandongTrainingScraper(amap_key)
    
    # 开始爬取
    scraper.scrape_all_cities()
    
    # 保存数据
    scraper.save_to_excel()
    
    # 显示统计信息
    scraper.generate_summary()
    
    print("\n任务完成！")


if __name__ == '__main__':
    main()

