#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单数学工具类 - 原始版本
"""

import math


class MathUtils:
    """数学工具类"""
    
    def __init__(self):
        """初始化"""
        self.pi = math.pi
        self.e = math.e
    
    def add(self, a: float, b: float) -> float:
        """加法运算"""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """减法运算"""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """乘法运算"""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """除法运算"""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    
    def power(self, base: float, exponent: float) -> float:
        """幂运算"""
        return base ** exponent


def main():
    """主函数"""
    math_utils = MathUtils()
    
    # 基本运算测试
    print(f"加法: 2 + 3 = {math_utils.add(2, 3)}")
    print(f"减法: 10 - 4 = {math_utils.subtract(10, 4)}")
    print(f"乘法: 5 * 6 = {math_utils.multiply(5, 6)}")
    print(f"除法: 15 / 3 = {math_utils.divide(15, 3)}")
    print(f"幂运算: 2 ^ 3 = {math_utils.power(2, 3)}")


if __name__ == "__main__":
    main() 