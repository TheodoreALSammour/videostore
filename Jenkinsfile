pipeline {
  agent any

  /* ======== Parameters (editable in Jenkins UI) ======== */
  parameters {
    string(name: 'GIT_URL',    defaultValue: 'https://github.com/TheodoreALSammour/videostore.git', description: 'Repository URL')
    string(name: 'GIT_BRANCH', defaultValue: 'main', description: 'Branch to build')

    string(name: 'DJANGO_PORT', defaultValue: '8001', description: 'Port for Django dev server')

    booleanParam(name: 'ADD_ALIAS', defaultValue: true, description: 'Add a secondary IP alias before starting server')
    string(name: 'IFACE_NAME',  defaultValue: 'Wi-Fi', description: 'Interface name (from "netsh interface ipv4 show interfaces")')
    string(name: 'SECOND_IP',   defaultValue: '10.10.10.10', description: 'Secondary local IP to add')
    string(name: 'SUBNET_MASK', defaultValue: '255.255.255.0', description: 'Subnet mask for the secondary IP')
  }

  environment {
    // Use the job workspace dynamically (no hard-coded paths)
    WORKDIR = "${env.WORKSPACE}"
    VENV_PY = "${env.WORKSPACE}\\.venv\\Scripts\\python.exe"
  }

  stages {

    stage('Checkout') {
      steps {
        // Clones into ${WORKSPACE}
        git branch: "${params.GIT_BRANCH}", url: "${params.GIT_URL}"
      }
    }

    stage('Python Env & Migrate') {
      steps {
        bat """
          cd "%WORKDIR%"
          py -3 -m venv .venv
          .venv\\Scripts\\python -m pip install --upgrade pip
          .venv\\Scripts\\pip install -r requirements.txt
          .venv\\Scripts\\python manage.py migrate
        """
      }
    }

    stage('Allow Firewall (first time only)') {
      steps {
        bat """
          netsh advfirewall firewall show rule name="Videostore-%DJANGO_PORT%" >NUL 2>&1
          if errorlevel 1 netsh advfirewall firewall add rule name="Videostore-%DJANGO_PORT%" dir=in action=allow protocol=TCP localport=%DJANGO_PORT%
        """
      }
    }

    stage('Add Secondary IP (optional)') {
      when { expression { return params.ADD_ALIAS } }
      steps {
        bat """
          netsh interface ipv4 show interfaces
          netsh interface ipv4 add address name="${params.IFACE_NAME}" address=${params.SECOND_IP} mask=${params.SUBNET_MASK} skipassource=true
        """
      }
    }

    stage('Free Port if Busy') {
      steps {
        powershell '''
          $port = "${env.DJANGO_PORT}"
          $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
          if ($conn) {
            $pid = $conn.OwningProcess
            Write-Host "Killing process on port $port (PID=$pid)"
            Stop-Process -Id $pid -Force
            Start-Sleep -Seconds 2
          } else {
            Write-Host "Port $port is free."
          }
        '''
      }
    }

    stage('Start Django (Detached)') {
      steps {
        powershell '''
          $proj = "${env.WORKDIR}"
          $py   = "${env.VENV_PY}"
          $args = @("manage.py","runserver","0.0.0.0:${env.DJANGO_PORT}")
          Write-Host "Starting Videostore on 0.0.0.0:${env.DJANGO_PORT} ..."
          Start-Process -FilePath $py -ArgumentList $args -WorkingDirectory $proj -WindowStyle Hidden
        '''
      }
    }

    stage('Show Addresses') {
      steps {
        bat """
          echo ===== Active IPv4 addresses =====
          for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /R /C:"IPv4 Address"') do @echo %%A
          echo.
          echo Open these in your browser:
          echo   http://127.0.0.1:%DJANGO_PORT%
          echo   http://${params.SECOND_IP}:%DJANGO_PORT%   (if alias added)
        """
      }
    }
  }
}
