# 文档中心 (Documentation)

欢迎来到 BOSS直聘自动化招聘系统的文档中心。

## 📚 文档分类

### 📖 [指南文档 (Guides)](./guides/)

详细的开发和使用指南。

- **[开发指南 (Development Guide)](./guides/development.md)** - Claude Code 开发指南
  - 项目架构和代码组织
  - 开发模式和最佳实践
  - 测试策略和代码质量

- **[部署指南 (Deployment)](./guides/deployment.md)** - 部署和迁移文档
  - MongoDB 到 SQLite 迁移步骤
  - 数据备份和恢复

- **[脚本使用指南 (Scripts)](./guides/scripts.md)** - 批处理脚本说明
  - 启动脚本使用方法
  - 进程管理和端口配置

### 🔧 [故障排查 (Troubleshooting)](./troubleshooting/)

常见问题和解决方案。

- **[错误指南 (Error Guide)](./troubleshooting/error-guide.md)** - 常见错误预防
  - 导入错误分析
  - 代码模式问题
  - 最佳实践建议

- **[启动警告 (Startup Warnings)](./troubleshooting/startup-warnings.md)** - 启动时的问题和修复
  - 已知启动问题
  - 解决方案和配置调整

### 📝 [变更记录 (Changelog)](./changelog/)

项目变更和版本更新历史。

- **[CHANGELOG](./changelog/CHANGELOG.md)** - 完整的版本变更日志
- **[数据库迁移 (Migration)](./changelog/migration.md)** - MongoDB 到 SQLite 迁移摘要
- **[端口更新 (Port Update)](./changelog/port-update.md)** - 端口配置更新说明
- **[提交记录 (Commits)](./changelog/commits.md)** - Git 提交摘要

### ✨ [功能实现 (Features)](./features/)

已实现功能的详细文档。

- **[安全登录 UI (Secure Login UI)](./features/secure-login-ui.md)** - BOSS 安全登录界面实现
  - 前端现代化改造
  - Tailwind CSS 设计系统
  - 实施进度和任务清单

### 🐛 [问题修复 (Bug Fixes)](./bugs/)

问题修复记录。

- **[DrissionPage 修复 (DrissionPage Fixes)](./bugs/drissionpage-fixes.md)** - DrissionPage 相关问题修复
- **[错误修复摘要 (Error Fixes)](./bugs/error-fixes.md)** - 错误修复汇总

### 📦 [DrissionPage 文档](./DrissionPage/)

DrissionPage 浏览器自动化框架的中文文档。

- 包含完整的 DrissionPage 使用指南
- 浏览器控制、元素定位、数据采集等教程

## 🚀 快速导航

### 新用户入门
1. 阅读 [README.md](../README.md) 了解项目概述
2. 查看 [CHANGELOG](./changelog/CHANGELOG.md) 了解版本更新
3. 查看 [部署指南](./guides/deployment.md) 安装和配置项目
4. 参考 [脚本使用指南](./guides/scripts.md) 启动项目

### 开发者指南
1. 阅读 [开发指南](./guides/development.md) 了解项目架构
2. 查看 [错误指南](./troubleshooting/error-guide.md) 避免常见错误
3. 浏览 [变更记录](./changelog/) 了解最新更新

### 遇到问题？
1. 查看 [故障排查](./troubleshooting/) 部分
2. 阅读 [启动警告](./troubleshooting/startup-warnings.md) 了解已知问题
3. 浏览 [问题修复](./bugs/) 查看是否有类似问题的解决方案

## 📂 文档结构

```
docs/
├── README.md                  # 本文档 - 文档中心索引
├── guides/                    # 指南文档
│   ├── development.md         # 开发指南
│   ├── deployment.md          # 部署指南
│   └── scripts.md             # 脚本使用指南
├── troubleshooting/           # 故障排查
│   ├── error-guide.md         # 错误指南
│   └── startup-warnings.md    # 启动警告
├── changelog/                 # 变更记录
│   ├── migration.md           # 迁移记录
│   ├── port-update.md         # 端口更新
│   └── commits.md             # 提交记录
├── features/                  # 功能实现
│   └── secure-login-ui.md     # 安全登录 UI
├── bugs/                      # 问题修复
│   ├── drissionpage-fixes.md  # DrissionPage 修复
│   └── error-fixes.md         # 错误修复摘要
└── DrissionPage/              # DrissionPage 框架文档
    └── ...                    # 中文教程文档
```

## 💡 贡献指南

如果你发现文档有错误或需要补充：

1. 直接编辑对应的 Markdown 文件
2. 保持清晰的标题层级
3. 使用中文编写（技术术语保留英文）
4. 提交 Pull Request

---

**最后更新**: 2026-02-07
