"""
Stripe 결제 API (관리자 전용)
- /api/admin/payments/checkout [POST]
- /api/admin/payments/history [GET]
- /api/admin/payments/webhook [POST]
"""
from flask import Blueprint, request, jsonify, abort
from middleware.security import admin_required
import os
import stripe

bp = Blueprint('admin_payments_api', __name__, url_prefix='/api/admin/payments')

stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_xxx')

@bp.route('/checkout', methods=['POST'])
@admin_required
def create_checkout():
    """Stripe Checkout 세션 생성"""
    data = request.json
    amount = data.get('amount')
    currency = data.get('currency', 'usd')
    if not amount:
        abort(400, 'amount는 필수입니다.')
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {'name': data.get('description', '서비스 결제')},
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=data.get('success_url', 'https://yourprogram.com/success'),
            cancel_url=data.get('cancel_url', 'https://yourprogram.com/cancel'),
        )
        return jsonify({'checkout_url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@admin_required
def payment_history():
    """결제 내역 조회"""
    try:
        payments = stripe.PaymentIntent.list(limit=30)
        return jsonify({'payments': [
            {
                'id': p.id,
                'amount': p.amount / 100,
                'currency': p.currency,
                'status': p.status,
                'created': p.created,
                'receipt_url': p.charges.data[0].receipt_url if p.charges.data else None
            } for p in payments.data
        ]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Stripe Webhook 이벤트 처리"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    # 이벤트 타입별 처리
    if event['type'] == 'checkout.session.completed':
        # 결제 성공 처리 로직
        pass
    elif event['type'] == 'payment_intent.succeeded':
        # 결제 성공 처리 로직
        pass
    # ... 기타 이벤트 처리
    return jsonify({'status': 'ok'}) 