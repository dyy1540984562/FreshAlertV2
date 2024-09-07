import json
from openai import OpenAI
from pathlib import Path
from secret_key import KIMI_API_KEY

class FoodRecognizer:
    def __init__(self, kimi_api_key, logger):
        self.client = OpenAI(api_key=kimi_api_key, base_url="https://api.moonshot.cn/v1")
        self.logger = logger

    def recognize_with_kimi(self, image_path):
        self.logger.info("Starting recognition with Kimi")
        
        # xlnet.pdf 是一个示例文件, 我们支持 pdf, doc 以及图片等格式, 对于图片和 pdf 文件，提供 ocr 相关能力
        file_object = self.client.files.create(file=Path(image_path), purpose="file-extract")
        
        # 获取结果
        file_content = self.client.files.content(file_id=file_object.id).text
        
        # 把它放进请求中
        messages = [
            {
                "role": "system",
                "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
            },
            {
                "role": "user",
                "content": "这是一张食品包装的图片。请识别出食品名称、生产日期和保质期。如果无法识别出，请返回null。请用JSON格式返回结果，包含name、productionDate和shelfLife三个字段。请确保productionDate的格式为YYYY-MM-DD，shelfLife的格式为整数天数。"
            },
            {
                "role": "system",
                "content": file_content
            }
        ]
        try:
           # 然后调用 chat-completion, 获取 Kimi 的回答
            completion = self.client.chat.completions.create(
                model="moonshot-v1-32k",
                messages=messages,
                temperature=0.3,
            )
            answer = completion.choices[0].message.content
            self.logger.info(answer)
            try:
                food_info = json.loads(answer)
                self.logger.info("Recognition with Kimi successful")
                return food_info
            except json.JSONDecodeError:
                self.logger.error("Failed to parse Kimi response")
                return {"name": None, "productionDate": None, "shelfLife": None}
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return {"name": None, "productionDate": None, "shelfLife": None}

# # 初始化 FoodRecognizer
# food_recognizer = FoodRecognizer(KIMI_API_KEY)
# food_recognizer.recognize_with_kimi('test.jpg')
