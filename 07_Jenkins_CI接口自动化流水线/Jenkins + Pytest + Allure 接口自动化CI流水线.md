# Jenkins + Pytest + Allure 接口自动化CI流水线
## 一、学习目标
搭建极简持续集成流水线，绕开复杂Docker环境，使用Windows本地Jenkins完成整套CI流程：
提交代码 → Jenkins拉取GitHub源码 → 执行pytest自动化用例 → 自动生成Allure可视化测试报告

## 二、技术栈
Jenkins、Git、Python3、Pytest、Allure-pytest、Requests

## 三、环境说明
1. Jenkins：Windows本地msi安装部署，不使用Docker Compose
2. 代码仓库：GitHub托管全套自动化脚本与笔记
3. 项目目录：独立英文目录 `api_auto_ci_demo`，规避中文路径编码乱码问题
4. 报告工具：Allure，生成可视化HTML测试报告

## 四、完整实操流程
### 1. 前置准备
- Windows安装Jenkins、Git、Python、Allure命令行工具，配置环境变量
- 安装Python依赖：`pip install pytest requests allure-pytest`
- 编写接口自动化测试脚本，拆分用例：正常接口、Cookie/Header、Token鉴权、负向异常场景
- 编写Jenkinsfile流水线脚本，定义完整执行步骤

### 2. Jenkins流水线核心步骤
1. 配置GitHub仓库地址，配置Git凭证，拉取远程源码
2. 切换项目工作目录
3. 执行pytest命令运行接口自动化用例，生成allure结果数据
4. Jenkins内置Allure插件，自动解析结果生成可视化报告

> 流水线核心Jenkinsfile
```groovy
pipeline {
    agent any
    stages {
        stage('拉取源码') {
            steps {
                git url: 'https://github.com/xxx/xxx.git', branch: 'main'
            }
        }
        stage('执行自动化用例') {
            steps {
                bat 'pytest api_auto_ci_demo/ --alluredir=allure-results'
            }
        }
    }
    post {
        always {
            allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
        }
    }
}
```

### 3. 执行结果
#### 本次构建 #10，流水线执行成功：
- 总共 10 条接口自动化用例，执行通过率 100%
- 用例分类：基础接口请求、请求头 Cookie 校验、Token 鉴权、异常场景
- 自动生成 Allure 可视化报告，Jenkins 页面可直接在线查看