from flask import Blueprint, request, session
from extensions import db
from models import ChatSession, Message, User
from utils.response import success, error
from sqlalchemy import or_, and_
from datetime import datetime
import time

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# 简单的内存缓存，用于减少频繁的数据库查询
# 格式: {user_id: {'count': count, 'timestamp': timestamp}}
_unread_cache = {}
CACHE_TTL = 30  # 缓存30秒


# ================= 1. 发起/获取会话 (安全修复) =================
# 对应前端：点击“私聊”按钮时调用
@chat_bp.route('/create_session', methods=['POST'])
def create_session():
    # 1. 身份校验
    my_id = session.get('user_id')
    if not my_id:
        return error(message="请先登录")

    data = request.get_json()
    target_id = data.get('target_id')  # 对方ID

    if not target_id: 
        return error(message="缺少目标用户ID")
    
    if my_id == target_id: 
        return error(message="不能和自己聊天")

    # 2. 确保 Session 唯一性 (始终保持 ID 小的在前，大的在后)
    # 这样 (1, 2) 和 (2, 1) 查出来的都是同一个会话
    u1, u2 = sorted([my_id, target_id])

    chat_session = ChatSession.query.filter_by(user1_id=u1, user2_id=u2).first()

    if not chat_session:
        try:
            # 创建新会话
            chat_session = ChatSession(
                user1_id=u1, 
                user2_id=u2, 
                updated_at=datetime.now()
            )
            db.session.add(chat_session)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return error(message="创建会话失败")

    return success(data={'session_id': chat_session.id})


# ================= 2. 发送消息 (安全修复 + 权限检查) =================
# 对应前端：ChatDetail.vue 发送按钮
@chat_bp.route('/send', methods=['POST'])
def send_message():
    # 1. 身份校验
    sender_id = session.get('user_id')
    if not sender_id:
        return error(message="请先登录")

    data = request.get_json()
    session_id = data.get('session_id')
    content = data.get('content')

    if not content: return error(message="消息不能为空")
    if len(content) > 500: return error(message="消息太长")

    # 2. 获取会话
    chat_session = db.session.get(ChatSession, session_id)
    if not chat_session: 
        return error(message="会话不存在")

    # 3. 【核心安全检查】确保发送者是这个会话的成员
    # 防止恶意用户随便拿一个 session_id 往别人的聊天里插话
    if sender_id != chat_session.user1_id and sender_id != chat_session.user2_id:
        return error(message="您不是该会话的成员，无权发送消息")

    current_time = datetime.now()

    try:
        # 4. 创建消息
        msg = Message(
            session_id=session_id,
            sender_id=sender_id, # 强制使用当前登录用户
            content=content,
            created_at=current_time,
            is_read=False 
        )

        # 5. 更新会话时间 (用于列表排序，把最新的聊天顶上去)
        chat_session.updated_at = current_time

        db.session.add(msg)
        db.session.commit()
        return success(message="发送成功", data=msg.to_dict())
    except Exception as e:
        db.session.rollback()
        return error(message=f"发送失败: {str(e)}")


# ================= 3. 获取消息记录 (隐私保护 + 自动已读) =================
# 对应前端：ChatDetail.vue 加载时调用
@chat_bp.route('/history', methods=['GET'])
def get_history():
    # 1. 身份校验
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")

    session_id = request.args.get('session_id', type=int)
    if not session_id:
        return error(message="缺少 session_id")

    chat_session = db.session.get(ChatSession, session_id)
    if not chat_session:
        return error(message="会话不存在")

    # 2. 【核心隐私检查】只有会话成员才能看记录
    if current_user_id != chat_session.user1_id and current_user_id != chat_session.user2_id:
        return error(message="您无权查看此聊天记录")

    # 3. 查询消息
    messages = Message.query.filter_by(session_id=session_id) \
        .order_by(Message.created_at.asc()).all()

    # 4. 【新增逻辑】标记已读 (Mark as Read)
    # 既然用户获取了历史记录，说明他正在看聊天框，那么对方发给我的未读消息都应该变成“已读”
    # 逻辑：把 session_id 是这个，且 sender_id 不是我，且 is_read 是 False 的消息，全改为 True
    try:
        unread_msgs = Message.query.filter(
            Message.session_id == session_id,
            Message.sender_id != current_user_id, # 别人发给我的
            Message.is_read == False
        ).all()
        
        if unread_msgs:
            for m in unread_msgs:
                m.is_read = True
            db.session.commit() # 提交已读状态更改
            # 清除缓存，确保未读数及时更新
            if current_user_id in _unread_cache:
                _unread_cache.pop(current_user_id, None)
    except Exception as e:
        # 标记已读失败不影响获取消息，记录日志即可
        print(f"标记已读失败: {e}")

    return success(data=[m.to_dict() for m in messages])


# ================= 4. 获取聊天列表 (列表页) =================
# 对应前端：ChatList.vue
@chat_bp.route('/list', methods=['GET'])
def get_chat_list():
    # 1. 身份校验
    user_id = session.get('user_id')
    if not user_id: 
        return error(message="请先登录")

    # 2. 查询我有份参与的所有会话 (按时间倒序)
    sessions = ChatSession.query.filter(
        or_(ChatSession.user1_id == user_id, ChatSession.user2_id == user_id)
    ).order_by(ChatSession.updated_at.desc()).all()

    result = []
    for s in sessions:
        # 3. 确定“对方”是谁
        target_user = s.user2 if s.user1_id == user_id else s.user1
        
        # 4. 计算未读数 (别人发给我的，且未读的)
        unread_count = Message.query.filter_by(session_id=s.id, is_read=False) \
            .filter(Message.sender_id != user_id).count()

        # 5. 获取最后一条消息 (用于列表展示简略)
        last_msg = Message.query.filter_by(session_id=s.id) \
            .order_by(Message.created_at.desc()).first()

        time_str = s.updated_at.strftime('%Y-%m-%d %H:%M:%S') if s.updated_at else ""

        result.append({
            'session_id': s.id,
            'target_user': target_user.to_dict(), # 包含头像、名字，前端 ChatList.vue 需要用
            'unread_count': unread_count,         # 前端显示红点
            'last_message': last_msg.content if last_msg else "[图片/空]",
            'updated_at': time_str
        })

    return success(data=result)

# ================= 5. 【新增】全局未读消息计数 =================
# 对应前端：放在底部导航栏或者顶栏，显示总共有多少条未读
@chat_bp.route('/unread_total', methods=['GET'])
def get_global_unread():
    user_id = session.get('user_id')
    if not user_id:
        return error(message="未登录")
    
    # 检查缓存
    current_time = time.time()
    if user_id in _unread_cache:
        cached_data = _unread_cache[user_id]
        # 如果缓存未过期（30秒内），直接返回缓存值
        if current_time - cached_data['timestamp'] < CACHE_TTL:
            return success(data={'total_unread': cached_data['count']})
    
    # 缓存过期或不存在，查询数据库
    # 逻辑：查找所有 ChatSession 里我参与的 -> 查找 Message 里发给我的未读
    # 优化：使用 JOIN 查询提高性能
    try:
        # 使用 JOIN 优化查询，一次性获取结果
        total = db.session.query(Message.id).join(
            ChatSession,
            Message.session_id == ChatSession.id
        ).filter(
            or_(ChatSession.user1_id == user_id, ChatSession.user2_id == user_id),
            Message.sender_id != user_id,
            Message.is_read == False
        ).count()
    except Exception as e:
        # 如果 JOIN 查询失败，回退到原来的方法
        my_sessions = db.session.query(ChatSession.id).filter(
            or_(ChatSession.user1_id == user_id, ChatSession.user2_id == user_id)
        ).all()
        session_ids = [s[0] for s in my_sessions]

        if not session_ids:
            total = 0
        else:
            total = Message.query.filter(
                Message.session_id.in_(session_ids),
                Message.sender_id != user_id,
                Message.is_read == False
            ).count()
    
    # 更新缓存
    _unread_cache[user_id] = {
        'count': total,
        'timestamp': current_time
    }
    
    # 清理过期缓存（避免内存泄漏）
    if len(_unread_cache) > 1000:  # 如果缓存项超过1000，清理过期项
        expired_keys = [
            uid for uid, data in _unread_cache.items()
            if current_time - data['timestamp'] >= CACHE_TTL
        ]
        for key in expired_keys:
            _unread_cache.pop(key, None)

    return success(data={'total_unread': total})