import logging

# 配置日志：同时输出控制台 + 写入文件
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("run.log",encoding="utf‑8"),
        logging.StreamHandler()
    ]
)

logging.info("====测试开始执行====")
logging.info("发送get接口请求")
logging.warning("这是警告日志")
logging.error("模拟错误日志输出")
logging.info("====测试执行结束====")