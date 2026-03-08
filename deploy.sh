#!/bin/bash
# deploy-to-github.sh — 将看板更新推送到 GitHub Pages
# 使用前需配置 GITHUB_TOKEN 环境变量或 ~/.netrc
#
# 使用方法:
#   GITHUB_TOKEN=ghp_xxx bash deploy-to-github.sh
#   或: export GITHUB_TOKEN=ghp_xxx && bash deploy-to-github.sh

set -e

REPO_DIR="$HOME/Desktop/宏观研究中心/7-数据看板"
GITHUB_USER="chenchenai"
GITHUB_REPO="macro-oracle"   # 根据实际 repo name 修改
BRANCH="main"                # 或 gh-pages

cd "$REPO_DIR"

# 检查 git remote
if ! git remote get-url origin &>/dev/null; then
  if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 未找到 git remote，且 GITHUB_TOKEN 未设置"
    echo "   请先运行: git remote add origin https://github.com/$GITHUB_USER/$GITHUB_REPO.git"
    exit 1
  fi
  git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$GITHUB_REPO.git"
else
  # 如果已有 remote，注入 token
  if [ -n "$GITHUB_TOKEN" ]; then
    git remote set-url origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$GITHUB_REPO.git"
  fi
fi

# Stage 变更的文件
git add 代码/macro-oracle-standalone.html 代码/events.json 2>/dev/null || true
git add macro-oracle-standalone.html events.json 2>/dev/null || true

if git diff --cached --quiet; then
  echo "ℹ️  没有变更需要推送"
  exit 0
fi

TIMESTAMP=$(TZ=Asia/Shanghai date +"%Y-%m-%d %H:%M CST")
git commit -m "事件更新 $TIMESTAMP"
git push origin "$BRANCH"
echo "✅ 已推送到 GitHub Pages: https://$GITHUB_USER.github.io/$GITHUB_REPO/"
