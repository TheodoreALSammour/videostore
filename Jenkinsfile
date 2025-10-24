pipeline {
  agent any
  options { timestamps() }

  environment {
    PROFILE       = 'jenkins'   // your service-account profile (option 2)
    MINIKUBE_HOME = 'C:\\ProgramData\\Jenkins\\.minikube'
    KUBECONFIG    = 'C:\\ProgramData\\Jenkins\\.kube\\config'
  }

  stages {
    stage('Start Minikube (service profile)') {
      options { timeout(time: 8, unit: 'MINUTES') }   // <- cap this
      steps {
        bat '''
          echo === Ensure dirs ===
          if not exist "%MINIKUBE_HOME%" mkdir "%MINIKUBE_HOME%"
          if not exist "%KUBECONFIG%" ( if not exist "C:\\ProgramData\\Jenkins\\.kube" mkdir "C:\\ProgramData\\Jenkins\\.kube" )

          echo === Start/ensure Minikube ===
          minikube -p %PROFILE% status || minikube -p %PROFILE% start --driver=docker --wait=apiserver,system_pods,default_sa --wait-timeout=6m

          echo === Update context & show cluster ===
          minikube -p %PROFILE% update-context
          kubectl config use-context %PROFILE%
          kubectl config view --minify -o jsonpath="{.clusters[0].cluster.server}" & echo.
          kubectl cluster-info
        '''
      }
      post {
        failure {
          bat '''
            echo === DEBUG: Minikube logs (last 400 lines) ===
            minikube -p %PROFILE% logs --length=400
          '''
        }
      }
    }

    stage('Build in Minikube Docker') {
      options { timeout(time: 10, unit: 'MINUTES') }  // <- cap build
      steps {
        bat '''
          echo === Point Docker CLI to Minikube Docker ===
          for /f "tokens=* delims=" %%i in ('minikube -p %PROFILE% docker-env --shell=cmd') do %%i

          docker version
          docker build --progress=plain -t mydjangoapp:latest .
        '''
      }
    }

    stage('Deploy to Minikube') {
      options { timeout(time: 10, unit: 'MINUTES') }  // <- cap deploy
      steps {
        bat '''
          echo === Clear env overrides that force :8080 ===
          set KUBERNETES_MASTER=
          set K8S_MASTER=
          set HTTP_PROXY=
          set HTTPS_PROXY=

          echo === Confirm context & API URL ===
          kubectl config use-context %PROFILE%
          kubectl config view --minify -o jsonpath="{.clusters[0].cluster.server}" & echo.
          kubectl cluster-info

          echo === Apply manifests ===
          kubectl apply -f deployment.yaml --validate=false
          kubectl apply -f service.yaml --validate=false

          echo === Wait for rollout (bounded) ===
          kubectl rollout status deployment/django-deployment --timeout=180s
        '''
      }
      post {
        unsuccessful {
          bat '''
            echo === DEBUG: Pods, Events, and Describes ===
            kubectl get pods -o wide
            kubectl get events --sort-by=.lastTimestamp -A | tail -n 100
            kubectl describe deploy django-deployment
            for /f "tokens=1" %%p in ('kubectl get pods -o name') do kubectl describe %%p
            kubectl get svc -o wide
          '''
        }
      }
    }

    stage('Show Service URL') {
      options { timeout(time: 2, unit: 'MINUTES') }
      steps {
        bat 'minikube -p %PROFILE% service django-service --url'
      }
    }
  }
}
