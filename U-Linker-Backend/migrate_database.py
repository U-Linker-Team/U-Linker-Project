#!/usr/bin/env python3
"""
数据库迁移脚本
用于在修改models.py后更新数据库表结构

使用方法：
1. 直接运行：python migrate_database.py
2. 在Docker容器内运行：docker exec u-linker-web python /app/migrate_database.py
"""

from app import create_app
from extensions import db
from models import Message
from sqlalchemy import inspect, text
import sys

def migrate_messages_table():
    """迁移messages表，添加新字段"""
    app = create_app()
    
    with app.app_context():
        # 检查表是否存在
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'messages' not in tables:
            print("messages表不存在，将创建新表...")
            db.create_all()
            print("✅ messages表已创建")
            return True
        
        # 检查现有列
        columns = [col['name'] for col in inspector.get_columns('messages')]
        print(f"当前messages表的列: {columns}")
        
        # 需要添加的列
        new_columns = {
            'message_type': 'VARCHAR(20) DEFAULT "text"',
            'file_url': 'VARCHAR(500)',
            'file_name': 'VARCHAR(200)',
            'file_size': 'INTEGER'
        }
        
        # 检查并添加缺失的列
        added_columns = []
        for col_name, col_definition in new_columns.items():
            if col_name not in columns:
                try:
                    # 使用ALTER TABLE添加列
                    if col_name == 'message_type':
                        # message_type需要NOT NULL，但有默认值
                        sql = f"ALTER TABLE messages ADD COLUMN {col_name} VARCHAR(20) DEFAULT 'text' NOT NULL"
                    else:
                        # 其他列可以为NULL
                        sql = f"ALTER TABLE messages ADD COLUMN {col_name} {col_definition}"
                    
                    db.session.execute(text(sql))
                    added_columns.append(col_name)
                    print(f"✅ 已添加列: {col_name}")
                except Exception as e:
                    print(f"❌ 添加列 {col_name} 失败: {str(e)}")
                    # 继续尝试其他列
                    continue
        
        if added_columns:
            try:
                db.session.commit()
                print(f"✅ 成功添加以下列: {', '.join(added_columns)}")
            except Exception as e:
                db.session.rollback()
                print(f"❌ 提交失败: {str(e)}")
                return False
        else:
            print("✅ messages表已包含所有需要的列")
        
        # 修复content列：确保允许NULL（支持只发图片/视频）
        print("\n步骤 3: 检查并修复content列...")
        try:
            # MySQL语法：修改content列允许NULL
            sql = "ALTER TABLE messages MODIFY COLUMN content VARCHAR(500) NULL"
            db.session.execute(text(sql))
            db.session.commit()
            print("✅ content列已修改为允许NULL（支持纯图片/视频消息）")
        except Exception as e:
            # 如果已经是NULL或其他原因失败，不影响整体迁移
            print(f"⚠️ 修改content列时: {str(e)}")
            print("  （如果提示列已经允许NULL，可以忽略此警告）")
        
        return True

def check_database_status():
    """检查数据库连接状态"""
    app = create_app()
    
    try:
        with app.app_context():
            # 测试数据库连接
            db.session.execute(text('SELECT 1'))
            print("✅ 数据库连接正常")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("数据库迁移脚本")
    print("=" * 60)
    print()
    
    # 1. 检查数据库连接
    print("步骤 1: 检查数据库连接...")
    if not check_database_status():
        print("❌ 数据库连接失败，请检查配置")
        sys.exit(1)
    print()
    
    # 2. 迁移messages表
    print("步骤 2: 迁移messages表...")
    if migrate_messages_table():
        print()
        print("=" * 60)
        print("✅ 数据库迁移完成！")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("❌ 数据库迁移失败，请检查错误信息")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()

