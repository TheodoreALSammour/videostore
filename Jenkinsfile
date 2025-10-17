pipeline {
  agent any

  environment {
    PY = '.venv\\Scripts\\python.exe'
    PIP = '.venv\\Scripts\\pip.exe'
    DJ   = '.venv\\Scripts\\django-admin.exe'
    PORT = '8000'
    HOST = '0.0.0.0'
  }

  stages {
    stage('Checkout') {
      steps {
        git 'https://github.com/TheodoreALSammour/newRepository.git'
      }
    }

    stage('Python venv') {
      steps {
        bat 'if not exist .venv ( py -3 -m venv .venv )'
        bat '%PIP% --version'
      }
    }

    stage('Install requirements') {
      steps {
        bat '%PIP% install --upgrade pip'
        bat '%PIP% install -r requirements.txt'
      }
    }

    stage('Django setup') {
      steps {
        // set DJANGO_SETTINGS_MODULE if you need to, e.g. setx DJANGO_SETTINGS_MODULE myproj.settings
        bat '%PY% manage.py migrate --noinput'
        bat '%PY% manage.py collectstatic --noinput'
      }
    }

    stage('Stop old server on 8000 (if any)') {
      steps {
        // Find PID listening on 8000 and kill it (ignore errors if none)
        bat '''
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
  echo Killing PID %%a on port %PORT%
  taskkill /PID %%a /F
)
'''
      }
    }

    stage('Run Django server') {
      steps {
        // Run detached so it survives after the pipeline ends
        bat 'start "django-runserver" cmd /c "%PY% manage.py runserver %HOST%:%PORT%"'
      }
    }
  }

  post {
    success {
      echo "Django should now be running at http://localhost:${PORT}/"
    }
    failure {
      echo "Build failed. Check console output for details."
    }
  }
}
