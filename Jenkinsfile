pipeline {
  agent any

  triggers {
    pollSCM('H/2 * * * *')
  }

  environment {
    // Nuke any proxy for kubectl/minikube within this build
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

    stage('Ensure Minikube up (for this Jenkins user)') {
      steps {
        bat '''
        echo ==== Minikube status (expect failure on first run) ====
        minikube status || echo NO-CLUSTER

        echo ==== Start minikube if needed ====
        REM IMPORTANT: Docker Desktop must be running for this account
        IF ERRORLEVEL 1 (
          minikube start --driver=docker --kubernetes-version=v1.29.6 --alsologtostderr -v=1
        )

        echo ==== Point kubectl to minikube context ====
        minikube -p minikube update-context

        kubectl config current-context
        kubectl get nodes
        '''
      }
    }

    stage('Build in Minikube Docker') {
      steps {
        bat '''
        REM Switch Docker client to Minikube’s Docker
        minikube -p minikube docker-env --shell=cmd > docker_env.bat
        call docker_env.bat

        docker info

        REM Build the Django image inside Minikube’s Docker
        docker build -t mydjangoapp:latest .
        '''
      }
    }

    stage('Deploy to Minikube') {
      steps {
        bat '''
        REM Use Minikube’s kubectl to avoid kubeconfig/proxy issues
        minikube kubectl -- apply -f deployment.yaml --validate=false
        minikube kubectl -- apply -f service.yaml --validate=false

        minikube kubectl -- rollout status deployment/django-deployment --timeout=180s
        minikube kubectl -- get pods -o wide
        minikube kubectl -- get svc
        '''
      }
    }
  }

  post {
    always {
      bat '''
      echo ==== Collecting minikube logs (best-effort) ====
      minikube logs --file=minikube-logs.txt || echo SKIP LOGS
      '''
      archiveArtifacts artifacts: 'minikube-logs.txt', allowEmptyArchive: true
    }
  }
}
