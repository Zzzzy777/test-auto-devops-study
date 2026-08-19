pipeline {
    agent any
    stages {
        stage('拉取代码') {
            steps {
                git url: 'https://gitee.com/zzzzy7/test-auto-devops-study.git', branch: 'main'
            }
        }
        stage('安装依赖') {
            steps {
                bat 'pip install pytest allure-pytest'
            }
        }
        stage('执行自动化接口测试') {
            steps {
                bat 'pytest ./test_case/ --alluredir=allure-results'
            }
        }
        stage('生成Allure测试报告') {
            steps {
                allure generate allure-results --clean
            }
        }
    }
    post {
        always {
            allure results: [[path: 'allure-results']]
        }
    }
}
