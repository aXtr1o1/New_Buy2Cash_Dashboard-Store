module.exports = {
    apps: [
      {
        name: "buy2cash-api",
  
        // Run uvicorn directly
        script: "venv/bin/uvicorn",
        args: "main:app --host 0.0.0.0 --port 8000",
  
        // VERY IMPORTANT FOR PYTHON
        interpreter: "none",
        exec_mode: "fork",
        instances: 1,
  
        cwd: "/opt/buy2cash/New_Buy2Cash_Dashboard-Store/backend",
  
        autorestart: true,
        watch: false,
        max_memory_restart: "1G",
  
        env: {
          ENV: "production",
          PYTHONUNBUFFERED: "1"
        },
  
        error_file: "./logs/err.log",
        out_file: "./logs/out.log",
        log_date_format: "YYYY-MM-DD HH:mm:ss Z",
        merge_logs: true
      }
    ]
  };
  