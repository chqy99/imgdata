# imgdata-core

本仓库定义图像解析系统的核心数据结构和抽象接口，包括：

- BBox、ImageObject、ImageParseResult 等数据结构定义
- 文件读写接口（FileHandlerBase）
- Embedding 计算接口（EmbeddingModule）

该仓库只定义接口和数据结构，不包含具体实现，便于其他功能模块进行调用和扩展。
