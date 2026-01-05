from flask import Blueprint, request, session
from utils.response import success, error

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/session', methods=['GET'])
def check_session():
    """调试端点：检查 Session 状态"""
    user_id = session.get('user_id')
    session_keys = list(session.keys())
    
    return success(data={
        'user_id': user_id,
        'session_keys': session_keys,
        'session_id': session.get('_id', 'N/A'),
        'cookies': dict(request.cookies),
        'headers': {
            'cookie': request.headers.get('Cookie', 'N/A'),
            'origin': request.headers.get('Origin', 'N/A'),
            'referer': request.headers.get('Referer', 'N/A'),
        }
    }, message="Session 调试信息")

