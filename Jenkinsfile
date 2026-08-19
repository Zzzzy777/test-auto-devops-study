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
                bat 'pytest ./test_case/ --alluredir=allure-results'
            }
        }
    }
    post {
        always {
            allure results: [[path: 'allure-results']]
        }
    }
}
