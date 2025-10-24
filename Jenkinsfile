pipeline {
  agent any
  options { timestamps() }

  environment {
    PROFILE       = 'jenkins'
    MINIKUBE_HOME = 'C:\\ProgramData\\Jenkins\\.minikube'
    KUBECONFIG    = 'C:\\ProgramData\\Jenkins\\.kube\\config'
  }

  stages {
    stage('Who am I?') {
      steps {
        bat 'whoami & echo MINIKUBE_HOME=%MINIKUBE_HOME% & echo KUBECONFIG=%KUBECONFIG%'
      }
    }

    stage('Checkout') {
      steps {
        checkout([$class: 'GitSCM',
          branches: [[name: '*/main']],
          userRemoteConfigs: [[url: 'https://github.com/TheodoreALSammour/videostore.git']]
        ])
      }
    }

    stage('Start Minikube (service profile)') {
      steps {
        bat '''
          REM Ensure dirs exist (idempotent)
          if not exist "%MINIKUBE_HOME%" mkdir "%MINIKUBE_HOME%"
          if not exist "%~dp0" echo. > nul
          
          REM Start or ensure running (driver must match your machine - docker is common)
          minikube -p %PROFILE% status || minikube -p %PROFILE% start --driver=docker
          
          REM Update kube context in the service's KUBECONFIG
          minikube -p %PROFILE% update-context
          
          REM Show status/context for debugging
          kubectl config get-contexts
          kubectl config use-context %PROFILE%
          kubectl cluster-info
        '''
      }
    }

    stage('Build in Minikube Docker') {
      steps {
        bat '''
          REM Apply docker-env inline for THIS profile (NO temp .bat files)
          for /f "tokens=* delims=" %%i in ('minikube -p %PROFILE% docker-env --shell=cmd') do %%i

          docker version
          docker build -t mydjangoapp:latest .
        '''
      }
    }

    stage('Deploy to Minikube') {
      steps {
        bat '''
          REM Clear any poison that points kubectl to Jenkins :8080
          set KUBERNETES_MASTER=
          set K8S_MASTER=
          set HTTP_PROXY=
          set HTTPS_PROXY=

          REM Use the service profile's kube context
          kubectl config use-context %PROFILE%

          REM Print the server address (must be https://..., not http://localhost:8080)
          kubectl config view --minify -o jsonpath="{.clusters[0].cluster.server}" & echo.
          kubectl cluster-info

          REM Apply and wait
          kubectl apply -f deployment.yaml
          kubectl apply -f service.yaml
          kubectl rollout status deployment/django-deployment
        '''
      }
    }

    stage('Show Service URL') {
      steps {
        bat 'minikube -p %PROFILE% service django-service --url'
      }
    }
  }
}
