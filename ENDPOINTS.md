API Endpoints:
- POST /api/method/whatsapp_superapp.api.webhook (guest allowed) -> receive webhooks from Meta
- GET /api/method/whatsapp_superapp.api.list_conversations
- GET /api/method/whatsapp_superapp.api.list_messages?conversation=<name>
- POST /api/method/whatsapp_superapp.api.send_template?contact=<contact>&template_name=<template>
- Standard Frappe REST resources available for doctypes (CSIS Contact, CSIS Whatsapp Message, etc.)
