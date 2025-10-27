pipeline {
  agent any

  triggers {
    // Poll GitHub every 2 minutes
    pollSCM('H/2 * * * *')
  }

  environment {
    // Ensure kubectl/minikube are NOT proxied inside builds
    HTTP_PROXY = ''
    HTTPS_PROXY = ''
    http_proxy = ''
    https_proxy = ''
    NO_PROXY   = '127.0.0.1,localhost,::1,.svc,cluster.local,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/TheodoreALSammour/videostore.git'
      }
    }

    stage('Ensure Minikube up (K8s v1.34.0)') {
      steps {
        bat '''
        echo ===== Checking minikube status =====
        minikube status >NUL 2>&1
        IF ERRORLEVEL 1 (
          echo ===== Starting minikube (v1.34.0) =====
          minikube start --driver=docker --kubernetes-version=v1.34.0 --alsologtostderr -v=1
        ) ELSE (
          for /f "tokens=2 delims=:" %%v in ('minikube status ^| findstr /I "host:"') do set STATE=%%v
          set STATE=%STATE: =%
          echo Current state: %STATE%
          IF /I "%STATE%"=="Stopped" (
            echo ===== Starting stopped cluster (v1.34.0) =====
            minikube start --driver=docker --kubernetes-version=v1.34.0 --alsologtostderr -v=1
          )
        )

        echo ===== Point kubectl to minikube context =====
        minikube -p minikube update-context

        echo Current context:
        kubectl config current-context

        echo Nodes:
        kubectl get nodes -o wide
        '''
      }
    }

    stage('Build images inside Minikube') {
      steps {
        bat '''
        echo ===== Building v1 image (mydjangoapp:latest) =====
        rem Build directly into Minikube’s image store
        minikube image build -t mydjangoapp:latest .

        echo ===== Building v2 image (mydjangoapp:v2) =====
        minikube image build -t mydjangoapp:v2 .
        '''
      }
    }

    stage('Deploy v1 & v2 to Minikube') {
      steps {
        bat '''
        echo ===== Apply v1 manifests =====
        minikube kubectl -- apply -f deployment.yaml --validate=false
        minikube kubectl -- apply -f service.yaml --validate=false

        echo ===== Apply v2 manifests =====
        minikube kubectl -- apply -f deployment-v2.yaml --validate=false
        minikube kubectl -- apply -f service-v2.yaml --validate=false

        echo ===== Wait for rollouts =====
        minikube kubectl -- rollout status deployment/django-deployment --timeout=180s
        minikube kubectl -- rollout status deployment/django-deployment-v2 --timeout=180s

        echo ===== Show resources =====
        minikube kubectl -- get deploy,svc,pods -o wide

        echo ===== Print access URLs =====
        for /f %%i in ('minikube ip') do set MINIIP=%%i
        echo V1 URL:  http://%MINIIP%:30080
        echo V2 URL:  http://%MINIIP%:30081
        '''
      }
    }
  }

  post {
    always {
      bat '''
      echo ===== Collecting minikube logs (best effort) =====
      minikube logs --file=minikube-logs.txt || echo SKIP LOGS
      '''
      archiveArtifacts artifacts: 'minikube-logs.txt', allowEmptyArchive: true
    }
  }
}
