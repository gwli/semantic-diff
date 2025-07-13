#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例代码 - 旧版本
一个简单的计算器类，用于演示语义diff工具
"""

import math


class Calculator:
    """简单的计算器类"""
    
    def __init__(self):
        """初始化计算器"""
        self.history = []
        self.last_result = 0
    
    def add(self, a, b):
        """加法运算"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        self.last_result = result
        return result
    
    def subtract(self, a, b):
        """减法运算"""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        self.last_result = result
        return result
    
    def multiply(self, a, b):
        """乘法运算"""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        self.last_result = result
        return result
    
    def divide(self, a, b):
        """除法运算"""
        if b == 0:
            raise ValueError("除数不能为零")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        self.last_result = result
        return result
    
    def power(self, base, exponent):
        """幂运算"""
        result = base ** exponent
        self.history.append(f"{base} ^ {exponent} = {result}")
        self.last_result = result
        return result
    
    def sqrt(self, number):
        """平方根运算"""
        if number < 0:
            raise ValueError("负数不能开平方根")
        result = math.sqrt(number)
        self.history.append(f"sqrt({number}) = {result}")
        self.last_result = result
        return result
    
    def get_history(self):
        """获取计算历史"""
        return self.history.copy()
    
    def clear_history(self):
        """清除计算历史"""
        self.history = []
        self.last_result = 0
    
    def get_last_result(self):
        """获取最后一次计算结果"""
        return self.last_result


def main():
    """主函数，演示计算器使用"""
    calc = Calculator()
    
    # 执行一些计算
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"5 * 6 = {calc.multiply(5, 6)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
    print(f"2 ^ 8 = {calc.power(2, 8)}")
    print(f"sqrt(16) = {calc.sqrt(16)}")
    
    # 显示历史
    print("\n计算历史:")
    for record in calc.get_history():
        print(f"  {record}")
    
    print(f"\n最后结果: {calc.get_last_result()}")


if __name__ == "__main__":
    main() 