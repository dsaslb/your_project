# Operator Manual

## 1. System Overview
- your_program management system: notices, notifications, orders, inventory, staff, schedule, stats, etc.

## 2. Role/Account Management
- Super Admin: manage all stores/accounts/settings/stats/permissions
- Store Manager: manage own store, staff/orders/inventory/schedule
- Staff: access only own tasks
- Menu/function split by permission, PermissionGuard applied

## 3. Error Handling
- Check logs for server/frontend errors: logs/app.log, Sentry, Slack notifications
- For DB/network errors: restart, use backup/restore menu
- See FAQ for main error codes/messages

## 4. Deployment/Operation
- Auto-deploy on main branch push via Github Actions
- .env.production for environment variables, keep secrets secure
- logrotate, Sentry, Slack for monitoring

## 5. Live Monitoring/Charts
- Check traffic, notifications, errors, stats at /admin/dashboard/monitor
- Server/DB/network status, notification/error/traffic charts, recent event logs
- Real-time charts with react-chartjs-2, customizable colors/options

## 6. Data/Backup/Restore
- Regular backups, use backup management menu
- Data export/restore features provided

## 7. FAQ/Help
- See FAQ.md, /faq, /guide, /help pages
- For more, contact dev team or system admin 
