from nova_client import NovaClient

class EmbeddingsService:
    def __init__(self, nova_client: NovaClient):
        self.nova_client = nova_client

    async def analyze_screenshot(self, image_bytes: bytes) -> str:
        """
        Analyzes a screenshot using Nova Multimodal capabilities.
        """
        prompt = (
            "Analyze this screenshot from a customer support request. "
            "Identify what is shown, extract any error messages, "
            "and suggest what the problem might be."
        )
        return self.nova_client.analyze_image(image_bytes, prompt)
