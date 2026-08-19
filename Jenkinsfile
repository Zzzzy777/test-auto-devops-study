pipeline {
    agent any
    stages {
        stage('拉取代码') {
            steps {
                git url: 'shturl.cc/iNakQr7Lq3cO58dJ4BN9THlLsBfyhASPRM1r0tzNm', branch: 'main'
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
                bat 'allure generate allure-results --clean'
            }
        }
    }
    post {
        always {
            allure results: [[path: 'allure-results']]
        }
    }
}
