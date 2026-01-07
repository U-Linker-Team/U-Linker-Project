from flask import Blueprint, request, session
from extensions import db
from models import ChatSession, Message, User
from utils.response import success, error
from sqlalchemy import or_, and_
from datetime import datetime
import time
import os
from werkzeug.utils import secure_filename

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


# ================= 2. 发送消息 (安全修复 + 权限检查 + 文件上传) =================
# 对应前端：ChatDetail.vue 发送按钮
@chat_bp.route('/send', methods=['POST'])
def send_message():
    # 1. 身份校验
    sender_id = session.get('user_id')
    if not sender_id:
        return error(message="请先登录")

    # 2. 获取会话
    if request.is_json:
        data = request.get_json()
        session_id = data.get('session_id')
    else:
        session_id = request.form.get('session_id')
    
    if not session_id:
        return error(message="缺少session_id")
    
    try:
        session_id = int(session_id)
    except (ValueError, TypeError):
        return error(message="session_id格式错误")
    chat_session = db.session.get(ChatSession, session_id)
    if not chat_session: 
        return error(message="会话不存在")

    # 3. 【核心安全检查】确保发送者是这个会话的成员
    if sender_id != chat_session.user1_id and sender_id != chat_session.user2_id:
        return error(message="您不是该会话的成员，无权发送消息")

    current_time = datetime.now()

    try:
        # 4. 检查是否有文件上传
        message_type = 'text'
        content = None
        file_url = None
        file_name = None
        file_size = None

        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                # 文件上传
                original_filename = file.filename
                # 先提取原始扩展名（在secure_filename之前）
                original_ext = os.path.splitext(original_filename)[1].lower()
                
                # 验证文件类型（基于原始文件名，避免secure_filename改变扩展名）
                allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.avi', '.webm', '.mkv'}
                
                # 检查原始扩展名
                if original_ext not in allowed_extensions:
                    print(f"❌ 文件类型验证失败: 原始文件名={original_filename}, 扩展名={original_ext}, 允许的扩展名={allowed_extensions}")
                    return error(message=f"不支持的文件类型（{original_ext}），仅支持图片和视频")
                
                # 使用secure_filename处理文件名（保留扩展名）
                safe_name = secure_filename(original_filename)
                # 如果secure_filename改变了文件名，使用原始扩展名重新构建
                safe_ext = os.path.splitext(safe_name)[1].lower()
                if safe_ext != original_ext:
                    print(f"⚠️ secure_filename改变了扩展名: {safe_ext} -> {original_ext}, 使用原始扩展名")
                    safe_name = os.path.splitext(safe_name)[0] + original_ext
                
                filename = safe_name
                
                # 根据扩展名或MIME类型确定消息类型
                if original_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    message_type = 'image'
                elif original_ext in ['.mp4', '.mov', '.avi', '.webm', '.mkv']:
                    message_type = 'video'
                elif file.content_type.startswith('image/'):
                    message_type = 'image'
                elif file.content_type.startswith('video/'):
                    message_type = 'video'
                else:
                    message_type = 'file'
                
                print(f"✅ 文件验证通过: 文件名={filename}, 扩展名={original_ext}, 类型={message_type}, MIME={file.content_type}")
                
                # 验证文件大小（最大20MB）
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > 20 * 1024 * 1024:  # 20MB
                    return error(message="文件大小不能超过20MB")
                
                # 保存文件
                upload_folder = os.path.join(os.getcwd(), 'uploads', 'chat')
                os.makedirs(upload_folder, exist_ok=True)
                
                # 生成唯一文件名
                timestamp = int(current_time.timestamp())
                unique_filename = f"{sender_id}_{timestamp}_{filename}"
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                
                # 生成访问URL
                file_url = f"/uploads/chat/{unique_filename}"
                file_name = filename
        else:
            # 文本消息
            if request.is_json:
                data = request.get_json()
                content = data.get('content', '').strip()
            else:
                content = request.form.get('content', '').strip()
            
            if not content:
                return error(message="消息不能为空")
            if len(content) > 500:
                return error(message="消息太长")

        # 5. 创建消息
        msg = Message(
            session_id=session_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            created_at=current_time,
            is_read=False 
        )

        # 6. 更新会话时间
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


# ================= 6. 【新增】获取积分规则 =================
# 注意：这个路由虽然放在chat模块，但实际是通用的积分规则接口
@chat_bp.route('/points_rules', methods=['GET'])
def get_points_rules():
    """获取积分规则"""
    rules = [
        {
            'title': '积分冻结规则',
            'description': '发布悬赏任务时，积分会被冻结，任务完成后转给帮助者。',
            'icon': 'mdi:lock-outline',
            'color': 'red'
        },
        {
            'title': '积分退还规则',
            'description': '任务取消后，冻结的积分将退还到您的账户。',
            'icon': 'mdi:refresh-circle-outline',
            'color': 'green'
        },
        {
            'title': '服务交易规则',
            'description': '购买服务时，积分会被冻结，服务完成确认后转给卖家。',
            'icon': 'mdi:currency-usd',
            'color': 'blue'
        },
        {
            'title': '积分使用范围',
            'description': '积分不可提现，仅限平台内使用，可用于发布悬赏、购买服务等。',
            'icon': 'mdi:bank-outline',
            'color': 'purple'
        },
        {
            'title': '违规处理规则',
            'description': '如有违规行为，平台有权扣除相应积分，严重者可能封禁账号。',
            'icon': 'mdi:alert-circle-outline',
            'color': 'orange'
        },
        {
            'title': '积分有效期',
            'description': '积分有效期为一年，每年12月31日清零，请及时使用。',
            'icon': 'mdi:star-circle-outline',
            'color': 'yellow'
        }
    ]
    return success(data={'rules': rules})
