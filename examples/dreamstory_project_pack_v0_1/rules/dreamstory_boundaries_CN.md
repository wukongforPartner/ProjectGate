# DreamStory 项目边界

## Runtime fact

runtime fact 工作不能从一个样本路径直接进入补丁。必须先完成入口地图，分类所有可能的真实代码入口，再定义事件名、字段或第一刀范围。

## 补丁流程

补丁必须确认当前项目事实、git 状态、目标文件、真实方法结构、锚点地图和 owner 授权。

## Unity scene 保护

StartScene.unity 默认保护。除非 owner 明确授权，否则不得修改。

## 动画 / Effect

动画和 Effect 工作必须遵守项目当前动画所有权规则，不得引入未经批准的直接 flush。
