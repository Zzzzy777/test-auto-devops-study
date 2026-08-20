pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                bat '''
                    python -V
                    pip install -r api_auto_ci_demo/requirements.txt
                '''
            }
        }
        stage('Run Tests') {
            steps {
                bat '''
                    cd /d api_auto_ci_demo
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
