# imgdata-core

本仓库定义图像解析系统的核心数据结构和抽象接口，包括：

- BBox、ImageObject、ImageParseResult 等数据结构定义
- 文件读写接口（FileHandlerBase）
- Embedding 计算接口（EmbeddingModule）

该仓库只定义接口和数据结构，不包含具体实现，便于其他功能模块进行调用和扩展。

图像解析类说明：
1.原始图像（图像格式一定是 numpy.ndarray 格式），可以直接访问获取：height,width,channel,dtype。
2.原始图像的基本信息，包括：id,url,embedding
3.原始图像的可选信息，用 metadata 记录
4.解析结果列表
5.单个解析结果的基本信息，包括：id, mask, mask_path, bbox, mask_image, mask_image_path, score, label, text, source_module, embedding
6.单个解析结果的可选信息，用 metadata 记录
