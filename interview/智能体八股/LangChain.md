## LangChain
1. AI Agent 开发框架
LangChain 提供模型、Prompt、工具、Agent 和中间件等通用抽象，集成范围比较广，适合快速构建工具调用、RAG、SQL 查询等 AI 应用。
LangGraph 更偏底层的状态与流程编排。面对循环、分支、并行、断点恢复和人工审批等复杂流程时，可以使用图结构显式控制 Agent 的执行路径。现在 LangChain 的 Agent 也运行在 LangGraph 之上，因此二者更多是上下层关系，而不是互相替代的竞争关系。
LlamaIndex 的优势集中在数据接入、文档解析、索引和检索，适合企业知识库、文档问答和复杂 RAG 等数据密集型应用。

OpenAI Agents SDK 和 CrewAI。前者适合以 OpenAI 模型为主的轻量 Agent，后者擅长使用角色和任务表达多 Agent 协作。

2. 请你谈谈对 LangChain 中核心概念「Chain」的理解，以及它的核心作用与设计理念。
是一种应用编排思路：把 Prompt、模型、检索器、输出解析器和自定义逻辑等步骤，按照明确的数据流连接起来，让上一步的输出成为下一步的输入，最终形成一个可以整体执行的流程。

在现在的 LangChain 里，Chain 最重要的技术基础是 Runnable。每个步骤都尽量遵守统一的输入输出和执行接口，，再通过 LCEL 的 | 做串行组合，或者通过字典、RunnableParallel 做并行组合。

组合后的整条 Chain 本身仍然是 Runnable，所以可以继续嵌套，也能统一使用 invoke、ainvoke、batch 和 stream 等能力。

3. langchain的底层架构与实现
首先，langchain-core 使用 Message、Model、Tool 和 Runnable 等标准协议隔离厂商差异。用户消息进入 Agent State 后，模型生成 AIMessage ；
如果其中包含工具调用，LangGraph 会路由到工具节点，工具结果以带相同调用 ID 的 ToolMessage 写回状态，模型再继续判断，直到产生最终回答。

其次，要讲清数据和控制的职责：State 保存可变状态，Context 提供可信依赖，Store 保存跨线程数据，Middleware 负责权限、重试、摘要和人工审批，LangGraph 负责状态推进、路由、检查点与恢复。

最后补充版本边界：LangChain v1 的主线是「标准协议 + create_agent + LangGraph Runtime」；

4. LangChain 中注册 Tool 的本质 
是同时向模型提供一份工具说明，并向运行时提供一个真正可执行的函数。工具说明主要包含名称、用途和参数 Schema，模型根据它选择工具并生成参数，LangChain 再执行对应函数。
最常用的实现方式有四种：
1) 简单的已有函数，可以带上类型注解和 docstring 后直接放入 tools。
2) 大多数业务工具使用 @tool，便于自定义名称、描述和参数 Schema。
3) 需要在运行时组装同步函数、异步函数和 Schema 时，可以使用 StructuredTool。
4) 工具需要封装客户端、维护资源或定制执行过程时，再继承 BaseTool。

5. langchain 实现记忆机制
1) 短期记忆属于当前会话线程。Agent State 保存消息、当前步骤和中间结果；Checkpointer 按 thread_id 保存状态快照。使用同一个 thread_id 再次调用时，可以恢复前面的对话和执行状态。
2) 长期记忆不应该绑定某个线程，而是保存到 Store。Store 使用 namespace 和 key 组织数据，namespace 通常包含租户、用户和记忆类型。即使用户新建了线程，只要使用相同的可信用户身份和 namespace，仍然可以读取以前保存的偏好或经验。


6. langGraph的区别
create_agent 本身就运行在 LangGraph 上；LangGraph 是更低层的编排框架与运行时，让开发者直接控制 State、节点、边、路由、并行、子图、中断和恢复。
LangChain v1 是高层 Agent 开发框架，负责提供模型、工具、结构化输出和 middleware 等常用能力。LangGraph 则是低层的 Agent 编排框架与运行时，让开发者直接设计状态、节点、路由、并行、中断和恢复。

开发者控制哪一层。若需求是常见的「模型判断 -> 调用工具 -> 返回模型」循环，我会优先用 LangChain，再借助 middleware 做提示词、重试、护栏和审批等定制。

若业务需要显式控制多个阶段，让确定性步骤与 Agent 步骤混排，或者要处理复杂并行、长期暂停和多 Agent 协作，我会直接用 LangGraph。
