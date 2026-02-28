"""
自动回复规则相关API
"""

from typing import Optional

import aiosqlite
from fastapi import APIRouter, Depends, Query

from ..core.database import get_database
from ..core.responses import error_response, success_response
from ..services.reply_engine import ReplyEngine, ReplyRuleService

router = APIRouter(prefix="/api/hr/reply-rules", tags=["reply-rules"])


@router.post("/", response_model=dict)
async def create_rule(
    hr_account_id: int = Query(..., description="HR账户ID"),
    trigger_keywords: str = Query(..., description="触发关键词，逗号分隔"),
    reply_template: str = Query(..., description="回复模板"),
    auto_invite: bool = Query(False, description="是否自动打招呼"),
    priority: int = Query(0, description="优先级"),
    is_active: bool = Query(True, description="是否启用"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """创建自动回复规则"""
    try:
        service = ReplyRuleService(db)
        rule = await service.create(
            hr_account_id=hr_account_id,
            trigger_keywords=trigger_keywords,
            reply_template=reply_template,
            auto_invite=auto_invite,
            priority=priority,
            is_active=is_active,
        )

        return success_response(
            data={
                "id": rule.id,
                "hr_account_id": rule.hr_account_id,
                "trigger_keywords": rule.trigger_keywords,
                "reply_template": rule.reply_template,
                "auto_invite": rule.auto_invite,
                "priority": rule.priority,
                "is_active": rule.is_active,
            },
            message="规则创建成功",
        )
    except Exception as e:
        return error_response(message=f"创建失败: {str(e)}", code=500)


@router.get("/", response_model=dict)
async def get_rules(
    hr_account_id: Optional[int] = Query(None, description="HR账户ID"),
    is_active: Optional[bool] = Query(None, description="是否只获取启用的规则"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """获取回复规则列表"""
    service = ReplyRuleService(db)
    rules = await service.get_list(hr_account_id=hr_account_id, is_active=is_active)

    return success_response(
        data=[
            {
                "id": rule.id,
                "hr_account_id": rule.hr_account_id,
                "trigger_keywords": rule.trigger_keywords,
                "reply_template": rule.reply_template,
                "auto_invite": rule.auto_invite,
                "priority": rule.priority,
                "is_active": rule.is_active,
            }
            for rule in rules
        ]
    )


@router.get("/{rule_id}", response_model=dict)
async def get_rule(rule_id: int, db: aiosqlite.Connection = Depends(get_database)):
    """获取规则详情"""
    service = ReplyRuleService(db)
    rule = await service.get_by_id(rule_id)

    if not rule:
        return error_response(message="规则不存在", code=404)

    return success_response(
        data={
            "id": rule.id,
            "hr_account_id": rule.hr_account_id,
            "trigger_keywords": rule.trigger_keywords,
            "reply_template": rule.reply_template,
            "auto_invite": rule.auto_invite,
            "priority": rule.priority,
            "is_active": rule.is_active,
        }
    )


@router.put("/{rule_id}", response_model=dict)
async def update_rule(
    rule_id: int,
    trigger_keywords: Optional[str] = None,
    reply_template: Optional[str] = None,
    auto_invite: Optional[bool] = None,
    priority: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: aiosqlite.Connection = Depends(get_database),
):
    """更新规则"""
    service = ReplyRuleService(db)
    rule = await service.update(
        rule_id=rule_id,
        trigger_keywords=trigger_keywords,
        reply_template=reply_template,
        auto_invite=auto_invite,
        priority=priority,
        is_active=is_active,
    )

    if not rule:
        return error_response(message="规则不存在", code=404)

    return success_response(data={"id": rule.id}, message="规则更新成功")


@router.delete("/{rule_id}", response_model=dict)
async def delete_rule(rule_id: int, db: aiosqlite.Connection = Depends(get_database)):
    """删除规则"""
    service = ReplyRuleService(db)
    success = await service.delete(rule_id)

    if not success:
        return error_response(message="规则不存在", code=404)

    return success_response(message="规则删除成功")


@router.post("/test", response_model=dict)
async def test_rule(
    message: str = Query(..., description="测试消息"),
    hr_account_id: int = Query(..., description="HR账户ID"),
    db: aiosqlite.Connection = Depends(get_database),
):
    """测试消息匹配"""
    engine = ReplyEngine(db)
    rule = await engine.match_rule(message, hr_account_id)

    if not rule:
        return success_response(data={"matched": False}, message="没有匹配的规则")

    reply = rule.format_reply({"candidate_name": "候选人", "message": message})

    return success_response(
        data={
            "matched": True,
            "rule_id": rule.id,
            "trigger_keywords": rule.trigger_keywords,
            "reply": reply,
        },
        message="匹配成功",
    )
