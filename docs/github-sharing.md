# GitHub 发布与分享指南 (Publishing Guide)

本文档面向维护者或准备基于本项目建立自己二次分发版本的开发者，介绍如何将 Learning Foundation 发布到 GitHub。

---

## 🚀 发布前检查清单

在向 GitHub 推送新版本或发布 Release 前，请确保已在本地完成以下检查：

1. **版本与许可核对**：检查根目录的 [VERSION](../VERSION) 与 [LICENSE](../LICENSE) 文件；
2. **执行全套自动化测试**：
   ```sh
   python tools/check_release.py
   python -m unittest discover -s tests -v
   ```
3. **构建发布归档与校验指纹**：
   ```sh
   python tools/build_release.py --output ../learning-foundation-releases
   ```
   工具会自动在指定的外部目录生成带时间戳归一化的 `.zip` 压缩包以及对应的 `.zip.sha256` 校验和文件。

---

## 📦 推送到 GitHub 仓库

如果你是第一次将项目推送到全新的 GitHub 仓库：

```sh
# 1. 初始化 Git 仓库（如果尚未初始化）
git init
git add .
git commit -m "feat: release Learning Foundation 0.2.0"

# 2. 关联 GitHub 远程仓库并推送
git branch -M main
git remote add origin https://github.com/<your-username>/learning-foundation.git
git push -u origin main

# 3. 创建版本标签
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

---

## 🏷️ 创建 GitHub Release

1. 访问 GitHub 仓库的 **Releases** 页面，点击 **Draft a new release**；
2. 选择刚才推送的 `v0.2.0` 标签；
3. 将本地构建生成的 `learning-foundation-0.2.0.zip` 和 `.zip.sha256` 拖拽上传到附件区；
4. 填写简要的更新说明并点击 **Publish release**。

现在，社区用户即可直接克隆你的仓库，或通过安装器以你的仓库为源直接添加技能！
