pipeline {
    agent any
    stages {
        stage('拉取代码') {
            steps {
                checkout scm
            }
        }
        stage('安装依赖') {
            steps {
                bat '''
                python -m pip install --upgrade pip
                pip install pytest requests allure-pytest
                '''
            }
        }
        stage('执行自动化测试') {
            steps {
                bat 'pytest ./05_Python接口自动化/ -s -v --allure-report=allure-results'
            }
        }
        stage('生成Allure测试报告') {
            steps {
                allure includeResults: false, results: [[path: 'allure-results']]
            }
        }
    }
    post {
        always {
            echo '流水线执行完成，请查看Allure测试报告'
        }
    }
}
