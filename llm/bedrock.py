import boto3
from botocore.config import Config
import json
import base64

class BedrockLLM:
    def __init__(self, settings: dict):
        self.name = "Bedrock"
        self.model_id = settings['model']
        self.max_tokens = settings['max_tokens']

        # Instantiate Bedrock LLM Client
        config = Config(read_timeout=1000)
        self.client = boto3.client("bedrock-runtime", config=config)
        self.image_client = boto3.client("bedrock-runtime", config=config)

    def prompt(self, prompt):
        # Construct the prompt to bedrock
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "messages": [
                    { "role": "user", "content": [ { "text": prompt } ] }
                ],
                "inferenceConfig": { "temperature": 0.5, "topP": 0.9 }
            }),
            accept="application/json",
            contentType="application/json"
        )
        print(response)

        response_body = json.loads(response['body'].read())
        
        response_text = response_body["output"]["message"]["content"][0]["text"]
        print(response_text)
        return response_text

    def conversation(self, conversation, temperature: float = 0.5):
        # Convert conversation into messages
        messages = []
        for message in conversation:
            role = "user"
            if message["role"] == "ai":
                role = "assistant"

            messages.append({"role": role, "content": [{"text": message["content"]} ]})

        # Construct the prompt to bedrock
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "messages": messages,
                "inferenceConfig": {"maxTokens": self.max_tokens, "temperature": temperature, "topP": 0.9}
            }),
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response["body"].read())
        
        response_text = response_body["output"]["message"]["content"][0]["text"]

        return response_text

    def image(self, prompt):
        # Construct the prompt to bedrock

        # check if the image model id starts with stability
        if self.image_model_id.startswith("stability"):
            response = self.image_client.invoke_model(
                modelId=self.image_model_id,
                body= json.dumps({
                    "prompt": "The described person should be photo realistic. " + prompt,
                    "aspect_ratio": "1:1",
                    "output_format": "png"
                }),
                accept="application/json",
                contentType="application/json"
            )
            
        if self.image_model_id.startswith("amazon"):
            response = self.image_client.invoke_model(
                modelId=self.image_model_id,
                body= json.dumps({
                    "textToImageParams": {
                        "text": "Do not base this image on real people, but should be photo realistic. " + prompt
                    },
                    "taskType": "TEXT_IMAGE",
                    "imageGenerationConfig": {
                        "cfgScale": 8,
                        "seed": 42,
                        "quality": "standard",
                        "height": 1024,
                        "width": 1024,
                        "numberOfImages": 1
                    }
                }),
                accept="application/json",
                contentType="application/json"
            )

        response_body = json.loads(response.get("body").read())
        base64_image = response_body.get("images")[0]
        base64_bytes = base64_image.encode('ascii')
        image_bytes = base64.b64decode(base64_bytes)

        return image_bytes
