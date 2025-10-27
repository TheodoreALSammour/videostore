pipeline {
  agent any

  triggers {
    // Poll GitHub every 2 minutes
    pollSCM('H/2 * * * *')
  }

  // Make sure kubectl does NOT go through any proxy
  environment {
    HTTP_PROXY = ''
    HTTPS_PROXY = ''
    http_proxy = ''
    https_proxy = ''
    // Bypass proxy for local/cluster addresses
    NO_PROXY   = '127.0.0.1,localhost,::1,.svc,cluster.local,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/TheodoreALSammour/videostore.git'
      }
    }

    stage('Prepare K8s Context') {
      steps {
        bat '''
        REM Ensure Jenkins is talking to the Minikube context
        minikube -p minikube update-context
        kubectl config current-context
        kubectl get nodes
        '''
      }
    }

    stage('Build in Minikube Docker') {
      steps {
        bat '''
        REM === Switch Docker to Minikube Docker (CMD script) ===
        minikube -p minikube docker-env --shell=cmd > docker_env.bat
        call docker_env.bat

        REM Sanity check we are pointing at the Minikube Docker daemon
        docker info

        REM === Build Django image inside Minikube's Docker ===
        docker build -t mydjangoapp:latest .
        '''
      }
    }

    stage('Deploy to Minikube') {
      steps {
        bat '''
        REM Use Minikube's kubectl to avoid kubeconfig/proxy issues
        minikube kubectl -- apply -f deployment.yaml --validate=false
        minikube kubectl -- apply -f service.yaml --validate=false

        REM Wait for rollout and then show services
        minikube kubectl -- rollout status deployment/django-deployment --timeout=180s
        minikube kubectl -- get pods -o wide
        minikube kubectl -- get svc
        '''
      }
    }
  }

  post {
    always {
      bat 'minikube logs --file=minikube-logs.txt'
      archiveArtifacts artifacts: 'minikube-logs.txt', allowEmptyArchive: true
    }
  }
}
