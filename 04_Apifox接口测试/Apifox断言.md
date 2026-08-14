# Apifox 断言
## 一、什么是断言
断言：接口发送完成之后，**自动校验返回结果是否符合预期**，代替人工肉眼看返回数据。
如果实际结果 = 预期结果 → 断言✅通过；不相等 → ❌失败。
接口自动化核心，面试高频考点。

## 二、Apifox新版本断言对象对照表
| 断言对象 | 作用 |
|---|---|
| HTTP Code | 校验响应状态码（200、400、500） |
| Response JSON | 校验返回json里面的字段，使用JSONPath |
| Response Text | 校验整个返回原始文本内容 |
| Response Header | 校验响应头信息 |
| Response Cookie | 校验Cookie |
| 环境变量 / 全局变量 | 校验已经存好的变量 |

>注意：旧版本叫Response Status Code，新版本改名为 HTTP Code。

## 三、常用断言条件
- 等于：实际值和预期完全一模一样
- 不等于：和预期不一样
- 包含：返回内容里面包含某一段文字（不需要完全相等）
- 不包含
- 大于 / 小于：用于数字
- 为空 / 不为空：判断字段有没有返回

## 四、实操示例（httpbin.org/get）
1. HTTP Code 等于 200 ：校验接口请求成功
2. Response JSON，JSONPath:`$.url`，包含 `httpbin.org`：校验返回的url地址
3. Response Text 包含 `get`：校验返回文本里面含有get字符串

## 五、JSONPath简单语法（针对Response‑JSON断言）
- `$.url`  获取根节点下url字段
- `$.args.name` 获取args对象下面name
- `$.data[0].id` 获取数组第1个元素的id

>💡小技巧：Apifox输入JSONPath输入框右边有小扳手图标，可以点选返回的json字段自动生成表达式，不用手写。

## 六、断言失败排查思路（面试题）
1. 看断言结果，对比【实际值】和【预期值】
2. 检查断言对象有没有选错（比如状态码不要选成Response JSON）
3. JSONPath大小写严格区分，字段写错直接拿不到值
4. 区分`等于`和`包含`，不要混用
5. 看接口本身返回的数据是否发生变化

## 七、常见踩坑
1. 复制JSONPath多打空格，匹配失败
2. 把状态码断言选成Response JSON，一直报错
3. 预期值多了空格换行，导致“看起来一样但是断言失败”