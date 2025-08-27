#!/usr/bin/env python3
"""
流式传输阻断问题调试脚本
用于测试和诊断 playground API 的流式响应问题
"""

import asyncio
import aiohttp
import time
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试配置
API_BASE_URL = "http://localhost:8001/v1/playground"
TEST_AGENT_ID = "agno_assist"  # 根据你的配置调整
TEST_MESSAGE = "请解释一下爱因斯坦的质能方程 E=mc²，并用LaTeX公式展示。"

async def test_streaming_response():
    """测试流式响应，监控潜在的阻断问题"""
    
    url = f"{API_BASE_URL}/agents/{TEST_AGENT_ID}/runs"
    
    # 构建FormData
    data = aiohttp.FormData()
    data.add_field('message', TEST_MESSAGE)
    data.add_field('stream', 'true')
    data.add_field('session_id', f'test_session_{int(time.time())}')
    
    logger.info(f"🚀 开始流式请求: {url}")
    start_time = time.time()
    
    timeout = aiohttp.ClientTimeout(total=300)  # 5分钟超时
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, data=data) as response:
                if response.status != 200:
                    logger.error(f"❌ HTTP错误: {response.status}")
                    text = await response.text()
                    logger.error(f"错误内容: {text}")
                    return
                
                logger.info(f"✅ 连接成功，开始接收流式数据...")
                
                chunk_count = 0
                last_chunk_time = time.time()
                total_content = ""
                json_buffer = ""  # 用于累积JSON数据
                json_count = 0
                
                async for line in response.content:
                    if not line:
                        continue
                        
                    chunk_count += 1
                    current_time = time.time()
                    chunk_interval = current_time - last_chunk_time
                    total_elapsed = current_time - start_time
                    
                    try:
                        # 将接收到的数据添加到缓冲区
                        chunk_text = line.decode('utf-8')
                        json_buffer += chunk_text
                        
                        # 尝试解析完整的JSON对象
                        while True:
                            # 查找完整的JSON对象
                            brace_count = 0
                            json_start = -1
                            json_end = -1
                            
                            for i, char in enumerate(json_buffer):
                                if char == '{':
                                    if json_start == -1:
                                        json_start = i
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0 and json_start != -1:
                                        json_end = i
                                        break
                            
                            if json_start != -1 and json_end != -1:
                                # 找到完整的JSON对象
                                json_str = json_buffer[json_start:json_end + 1]
                                json_buffer = json_buffer[json_end + 1:]  # 移除已处理的部分
                                
                                try:
                                    chunk_data = json.loads(json_str)
                                    json_count += 1
                                    
                                    content = chunk_data.get('content', '')
                                    event = chunk_data.get('event', 'unknown')
                                    
                                    if content:
                                        total_content += content
                                    
                                    if json_count <= 10 or json_count % 100 == 0:  # 只显示前10个和每100个
                                        logger.info(f"📦 JSON #{json_count} (chunk #{chunk_count}, 间隔: {chunk_interval:.3f}s)")
                                        logger.info(f"   事件类型: {event}")
                                        logger.info(f"   内容长度: {len(content)} 字符")
                                        logger.info(f"   累计内容: {len(total_content)} 字符")
                                    
                                    # 检查是否包含数学公式
                                    if any(marker in content for marker in ['$$', '\\[', '\\(', 'E=mc']):
                                        logger.info(f"🧮 检测到数学公式内容 (JSON #{json_count})")
                                        logger.info(f"   公式片段: {content[:100]}...")
                                    
                                except json.JSONDecodeError as e:
                                    logger.warning(f"⚠️ JSON解析失败 (JSON #{json_count}): {e}")
                                    logger.warning(f"JSON内容: {json_str[:200]}...")
                            else:
                                # 没有找到完整的JSON对象，等待更多数据
                                break
                        
                        # 检测潜在的阻断
                        if chunk_interval > 10.0:
                            logger.warning(f"⚠️ 检测到慢速chunk! 间隔: {chunk_interval:.3f}s")
                        
                    except UnicodeDecodeError as e:
                        logger.warning(f"⚠️ Unicode解码失败: {e}")
                    
                    last_chunk_time = current_time
                
                total_time = time.time() - start_time
                logger.info(f"🎉 流式传输完成!")
                logger.info(f"   总chunk数: {chunk_count}")
                logger.info(f"   解析的JSON对象数: {json_count}")
                logger.info(f"   总时间: {total_time:.3f}s")
                logger.info(f"   平均chunk间隔: {total_time/max(1, chunk_count):.3f}s")
                logger.info(f"   最终内容长度: {len(total_content)} 字符")
                logger.info(f"   剩余缓冲区: {len(json_buffer)} 字符")
                
                # 显示最终内容的前几行
                if total_content:
                    lines = total_content.split('\n')[:5]
                    logger.info(f"📄 内容预览:")
                    for i, line in enumerate(lines, 1):
                        logger.info(f"   {i}: {line[:100]}...")
                
    except asyncio.TimeoutError:
        logger.error("❌ 请求超时!")
    except aiohttp.ClientError as e:
        logger.error(f"❌ 客户端错误: {e}")
    except Exception as e:
        logger.error(f"❌ 未知错误: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def test_multiple_requests():
    """测试多个连续请求，观察是否有性能下降"""
    
    for i in range(3):
        logger.info(f"\n{'='*50}")
        logger.info(f"开始第 {i+1} 次测试")
        logger.info(f"{'='*50}")
        
        await test_streaming_response()
        
        if i < 2:  # 不是最后一次
            logger.info("⏱️ 等待5秒后进行下一次测试...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("🔍 流式传输调试脚本")
    print("=" * 50)
    
    # 单次测试
    print("\n1. 运行单次流式请求测试...")
    asyncio.run(test_streaming_response())
    
    # 多次测试
    # print("\n2. 运行多次连续测试...")
    # asyncio.run(test_multiple_requests())