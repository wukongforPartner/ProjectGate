# SOP：Runtime Fact 入口地图

## 触发条件

任何涉及 runtime facts、analytics events、event fields 或 gameplay fact reporting 的任务。

## 必需流程

1. 保持只读审查。
2. 搜索所有可能产生该机制的真实代码入口。
3. 对每个入口分类：路径、方法、行号、触发机制、是否创建 RuntimeGridItem、是否加入库存、是否尝试上格、是否有 origin 标记、入口类别。
4. 分类完成前不得定义事件名或字段。
5. 如果只能覆盖局部入口，必须标记为局部语义。

## 停手条件

- 缺入口地图。
- 入口类别未知。
- 用户质疑“你怎么知道只有这条路径”。
