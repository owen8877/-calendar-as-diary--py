module.exports = {
  apps : [{
    name: 'calendar-as-diary-py',
    cmd: 'main.py',
    autorestart: false,
    pid_file: '/home/webhookd/.pm2/pids/calendar-as-diary-py-0.pid',
    watch: false,
    interpreter: 'python',
  }],
};
