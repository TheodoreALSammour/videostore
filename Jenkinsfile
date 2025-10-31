pipeline {
  agent any

  triggers {
    // Poll GitHub every 2 minutes
    pollSCM('H/2 * * * *')
  }

  environment {
    // Avoid proxying
    HTTP_PROXY = ''
    HTTPS_PROXY = ''
    http_proxy = ''
    https_proxy = ''
    NO_PROXY   = '127.0.0.1,localhost,::1,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/TheodoreALSammour/videostore.git'
      }
    }

    stage('Python Env & Migrate') {
      steps {
        bat '''
        echo ===== Setting up virtual environment =====
        cd "C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\Videostore - main"
        py -3 -m venv .venv
        .venv\\Scripts\\python -m pip install --upgrade pip
        .venv\\Scripts\\pip install -r requirements.txt
        .venv\\Scripts\\python manage.py migrate
        '''
      }
    }

    stage('Allow Firewall') {
      steps {
        bat '''
        echo ===== Allowing port 8001 through Windows Firewall =====
        netsh advfirewall firewall show rule name="Videostore-8001" >NUL 2>&1
        if errorlevel 1 netsh advfirewall firewall add rule name="Videostore-8001" dir=in action=allow protocol=TCP localport=8001
        '''
      }
    }

    stage('Add Secondary IP') {
      steps {
        powershell '''
        $secondIp = "10.10.10.10"
        $subnetMask = "255.255.255.0"

        # Auto-detect first active Wi-Fi or Ethernet adapter
        $nic = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and ($_.Name -like "Wi-Fi*" -or $_.Name -like "Ethernet*") } | Select-Object -First 1
        if (-not $nic) {
          Write-Error "No active network adapter found!"
          exit 1
        }

        $name = $nic.Name
        Write-Host "Adding IP $secondIp to interface: $name"
        $cmd = "netsh interface ipv4 add address name=""$name"" address=$secondIp mask=$subnetMask skipassource=true"
        cmd.exe /c $cmd
        '''
      }
    }

    stage('Free Port if Busy') {
      steps {
        powershell '''
        $port = 8001
        $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($conn) {
          $pid = $conn.OwningProcess
          Write-Host "Port $port is busy. Killing PID $pid..."
          Stop-Process -Id $pid -Force
          Start-Sleep -Seconds 2
        } else {
          Write-Host "Port $port is free."
        }
        '''
      }
    }

    stage('Start Django') {
      steps {
        powershell '''
        Write-Host "Starting Videostore on 0.0.0.0:8001 ..."
        $proj = "C:\\ProgramData\\Jenkins\\.jenkins\\workspace\\Videostore - main"
        $py = "$proj\\.venv\\Scripts\\python.exe"
        $args = @("manage.py","runserver","0.0.0.0:8001")
        Start-Process -FilePath $py -ArgumentList $args -WorkingDirectory $proj -WindowStyle Hidden
        '''
      }
    }

    stage('Show Addresses') {
      steps {
        bat '''
        echo ===== Active IPv4 addresses =====
        for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /R /C:"IPv4 Address"') do @echo %%A
        echo.
        echo Open your app in browser:
        echo   http://127.0.0.1:8001
        echo   http://10.10.10.10:8001
        '''
      }
    }
  }
}
