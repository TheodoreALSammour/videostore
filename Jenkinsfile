pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/TheodoreALSammour/newRepository.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Run Server') {
            steps {
                // Run server on port 8000 in the background
                bat 'start cmd /c "python manage.py runserver 0.0.0.0:8000"'
            }
        }
    }
}
