#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单数学工具类 - 新版本 (增加了新函数)
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
    
    def sqrt(self, number: float) -> float:
        """平方根运算 - 新增函数"""
        if number < 0:
            raise ValueError("负数不能开平方根")
        return math.sqrt(number)
    
    def factorial(self, n: int) -> int:
        """阶乘运算 - 新增函数"""
        if n < 0:
            raise ValueError("负数不能计算阶乘")
        if n == 0 or n == 1:
            return 1
        return math.factorial(n)
    
    def sin(self, angle: float) -> float:
        """正弦函数 - 新增函数"""
        return math.sin(angle)
    
    def cos(self, angle: float) -> float:
        """余弦函数 - 新增函数"""
        return math.cos(angle)
    
    def log(self, number: float, base: float = None) -> float:
        """对数函数 - 新增函数"""
        if number <= 0:
            raise ValueError("对数的真数必须大于0")
        if base is None:
            return math.log(number)
        if base <= 0 or base == 1:
            raise ValueError("对数的底数必须大于0且不等于1")
        return math.log(number, base)


def main():
    """主函数"""
    math_utils = MathUtils()
    
    # 基本运算测试
    print(f"加法: 2 + 3 = {math_utils.add(2, 3)}")
    print(f"减法: 10 - 4 = {math_utils.subtract(10, 4)}")
    print(f"乘法: 5 * 6 = {math_utils.multiply(5, 6)}")
    print(f"除法: 15 / 3 = {math_utils.divide(15, 3)}")
    print(f"幂运算: 2 ^ 3 = {math_utils.power(2, 3)}")
    
    # 新增函数测试
    print(f"平方根: sqrt(16) = {math_utils.sqrt(16)}")
    print(f"阶乘: 5! = {math_utils.factorial(5)}")
    print(f"正弦: sin(π/2) = {math_utils.sin(math.pi/2)}")
    print(f"余弦: cos(0) = {math_utils.cos(0)}")
    print(f"对数: log(10) = {math_utils.log(10)}")


if __name__ == "__main__":
    main() 