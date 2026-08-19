pipeline {
    agent any
    stages {
        stage('安装依赖') {
            steps {
                bat 'pip install pytest allure-pytest'
            }
        }
        stage('执行自动化接口测试') {
            steps {
                bat 'pytest ./05_Python接口自动化/03_完整项目/pytest_api_demo/test_cases/ --alluredir=allure-results'
            }
        }
    }
    post {
        always {
            allure results: [[path: 'allure-results']]
        }
    }
}
