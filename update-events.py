#!/usr/bin/env python3
"""
update-events.py — 宏观事件看板更新脚本
用法：
  python3 update-events.py add --json '<JSON>'          # 追加单个/多个事件
  python3 update-events.py prune                        # 仅清理7天外事件
  python3 update-events.py list                         # 列出当前事件

JSON 格式（单个事件）：
{
  "id": "YYYYMMDD-001",           # 唯一ID，格式 日期-序号
  "date": "2026-03-08",           # 事件日期
  "priority": "P0",               # P0/P1/P2
  "color": "red",                 # red/orange/yellow/green/purple/blue
  "title": "事件标题",
  "fact": "客观事实（1-2句）",
  "importance": "为何重要（1句）",
  "investment": "投资含义（1-2句）",
  "sources": [
    {"label": "来源名称", "url": "https://..."}
  ]
}

也可传入数组 [...] 一次添加多个。
"""

import json
import sys
import os
import argparse
from datetime import datetime, timezone, timedelta

EVENTS_JSON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../代码/events.json'
)
RETAIN_DAYS = 7

def load():
    if os.path.exists(EVENTS_JSON):
        with open(EVENTS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"retain_days": RETAIN_DAYS, "events": []}

def save(data):
    data['updated'] = datetime.now(tz=timezone(timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M:%S+08:00')
    os.makedirs(os.path.dirname(EVENTS_JSON), exist_ok=True)
    with open(EVENTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ events.json 已更新 → {EVENTS_JSON}")

def prune(data):
    cutoff = (datetime.now() - timedelta(days=RETAIN_DAYS)).strftime('%Y-%m-%d')
    before = len(data['events'])
    data['events'] = [e for e in data['events'] if e.get('date','') >= cutoff]
    pruned = before - len(data['events'])
    if pruned:
        print(f"🗑  已清理 {pruned} 条7天外事件")
    return data

def validate(ev):
    required = ['id', 'date', 'priority', 'color', 'title', 'fact', 'importance', 'investment']
    for k in required:
        if not ev.get(k):
            raise ValueError(f"缺少必填字段: {k}")
    if ev['priority'] not in ('P0','P1','P2'):
        raise ValueError(f"priority 必须为 P0/P1/P2，当前: {ev['priority']}")
    colors = ('red','orange','yellow','green','purple','blue')
    if ev['color'] not in colors:
        raise ValueError(f"color 必须为 {colors}，当前: {ev['color']}")
    ev.setdefault('sources', [])
    return ev

def add_events(new_events, data):
    existing_ids = {e['id'] for e in data['events']}
    added = 0
    for ev in new_events:
        try:
            ev = validate(ev)
        except ValueError as e:
            print(f"⚠️  跳过无效事件 [{ev.get('id','?')}]: {e}")
            continue
        if ev['id'] in existing_ids:
            print(f"ℹ️  已存在，跳过: {ev['id']}")
            continue
        data['events'].append(ev)
        existing_ids.add(ev['id'])
        added += 1
        print(f"➕ 新增: [{ev['priority']}] {ev['date']} {ev['title']}")
    return data, added

def main():
    parser = argparse.ArgumentParser(description='宏观事件看板更新工具')
    sub = parser.add_subparsers(dest='cmd')

    p_add = sub.add_parser('add', help='追加事件')
    p_add.add_argument('--json', required=True, help='事件 JSON（单个对象或数组）')

    sub.add_parser('prune', help='仅清理过期事件')
    sub.add_parser('list',  help='列出当前事件')

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    data = load()
    data = prune(data)

    if args.cmd == 'add':
        try:
            payload = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            sys.exit(1)
        if isinstance(payload, dict):
            payload = [payload]
        elif not isinstance(payload, list):
            print("❌ JSON 必须为对象或数组")
            sys.exit(1)
        data, added = add_events(payload, data)
        save(data)
        print(f"\n✅ 共新增 {added} 条事件，当前总计 {len(data['events'])} 条")

    elif args.cmd == 'prune':
        save(data)
        print(f"✅ 清理完成，当前 {len(data['events'])} 条事件")

    elif args.cmd == 'list':
        evs = sorted(data['events'], key=lambda e: e['date'], reverse=True)
        print(f"\n{'─'*60}")
        print(f"  📋 当前事件总计: {len(evs)} 条")
        print(f"{'─'*60}")
        for e in evs:
            print(f"  [{e['priority']}] {e['date']}  {e['title'][:40]}")
        print(f"{'─'*60}\n")

if __name__ == '__main__':
    main()
