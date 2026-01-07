// PM2 Ecosystem configuration for Buy2Cash API
module.exports = {
  apps: [{
    name: 'buy2cash-api',
    script: 'venv/bin/uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000 --workers 4',
    cwd: '/opt/buy2cash/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
};

