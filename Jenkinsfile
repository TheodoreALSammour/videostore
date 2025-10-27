pipeline {
  agent any

  triggers {
    // Poll GitHub every 2 minutes
    pollSCM('H/2 * * * *')
  }

  environment {
    // Avoid proxying kubectl/minikube
    HTTP_PROXY = ''
    HTTPS_PROXY = ''
    http_proxy = ''
    https_proxy = ''
    NO_PROXY   = '127.0.0.1,localhost,::1,.svc,cluster.local,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12'
    K8S_VERSION = 'v1.34.0'  // match your existing cluster
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/TheodoreALSammour/videostore.git'
      }
    }

    stage('Ensure clusters up (minikube + mini2)') {
      steps {
        bat '''
        echo ===== Ensure profile: minikube =====
        minikube -p minikube status >NUL 2>&1
        IF ERRORLEVEL 1 (
          minikube start -p minikube --driver=docker --kubernetes-version=%K8S_VERSION% --alsologtostderr -v=1
        ) ELSE (
          for /f "tokens=2 delims=:" %%v in ('minikube -p minikube status ^| findstr /I "host:"') do set S=%%v
          set S=%S: =%
          IF /I "%S%"=="Stopped" (
            minikube start -p minikube --driver=docker --kubernetes-version=%K8S_VERSION% --alsologtostderr -v=1
          )
        )
        minikube -p minikube update-context

        echo ===== Ensure profile: mini2 =====
        minikube -p mini2 status >NUL 2>&1
        IF ERRORLEVEL 1 (
          minikube start -p mini2 --driver=docker --kubernetes-version=%K8S_VERSION% --alsologtostderr -v=1
        ) ELSE (
          for /f "tokens=2 delims=:" %%v in ('minikube -p mini2 status ^| findstr /I "host:"') do set S2=%%v
          set S2=%S2: =%
          IF /I "%S2%"=="Stopped" (
            minikube start -p mini2 --driver=docker --kubernetes-version=%K8S_VERSION% --alsologtostderr -v=1
          )
        )
        minikube -p mini2 update-context

        echo -- minikube nodes --
        kubectl config use-context minikube
        kubectl get nodes -o wide

        echo -- mini2 nodes --
        kubectl config use-context mini2
        kubectl get nodes -o wide
        '''
      }
    }

    stage('Build images into each profile') {
      steps {
        bat '''
        echo ===== Build (profile: minikube) =====
        minikube -p minikube image build -t mydjangoapp:latest .
        echo ===== Build (profile: mini2) =====
        minikube -p mini2 image build -t mydjangoapp:v2 .
        '''
      }
    }

    stage('Deploy v1 to minikube') {
      steps {
        bat '''
        minikube -p minikube kubectl -- apply -f deployment.yaml --validate=false
        minikube -p minikube kubectl -- apply -f service.yaml --validate=false

        minikube -p minikube kubectl -- rollout status deployment/django-deployment --timeout=180s
        minikube -p minikube kubectl -- get deploy,svc,pods -o wide

        for /f %%i in ('minikube -p minikube ip') do set IP1=%%i
        echo MINIKUBE_IP=%IP1%
        echo V1 URL: http://%IP1%:30080
        '''
      }
    }

    stage('Deploy v2 to mini2') {
      steps {
        bat '''
        minikube -p mini2 kubectl -- apply -f deployment-v2.yaml --validate=false
        minikube -p mini2 kubectl -- apply -f service-v2.yaml --validate=false

        minikube -p mini2 kubectl -- rollout status deployment/django-deployment-v2 --timeout=180s
        minikube -p mini2 kubectl -- get deploy,svc,pods -o wide

        for /f %%i in ('minikube -p mini2 ip') do set IP2=%%i
        echo MINI2_IP=%IP2%
        echo V2 URL: http://%IP2%:30080
        '''
      }
    }
  }

  post {
    always {
      bat '''
      minikube -p minikube logs --file=minikube-logs-1.txt  || echo SKIP LOGS 1
      minikube -p mini2    logs --file=minikube-logs-2.txt  || echo SKIP LOGS 2
      '''
      archiveArtifacts artifacts: 'minikube-logs-*.txt', allowEmptyArchive: true
    }
  }
}
