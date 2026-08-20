pipeline {
    agent any
    stages {
        stage('拉取GitHub源码') {
            steps {
                checkout scm
            }
        }
        stage('安装Python依赖') {
            steps {
                bat '''
                    python -V
                    pip install -r api_auto_ci_demo/requirements.txt
                '''
            }
        }
        stage('执行自动化接口测试') {
            steps {
                bat '''
                    cd api_auto_ci_demo
                    pytest test_cases/ --alluredir=../allure-results
                '''
            }
        }
    }
    post {
        always {
            allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
        }
    }
}
