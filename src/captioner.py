import tqdm
from PIL import Image
import os
import torch
from transformers import AutoProcessor, AutoModelForCausalLM

class CaptionGenerator:
    def __init__(self,model_name="microsoft/git-base"):
        print(f"Generating Captions via {model_name}")
        self.device = ("cuda" if torch.cuda.is_available() else "cpu")
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            torch_dtype=self.torch_dtype,
            trust_remote_code=True
        ).to(self.device)
        print(f"Model Parameter Device: {self.device.upper()}")

    def generate_caption(self,imgs):
        min_kb = 5
        valid_images = []
        for img in imgs:
            img_path = img["image_path"]
            if(str(img_path).endswith(".svg")):
                img_path = str(img_path).replace(".svg",".png")
                img["image_path"] = img_path
            file_size_kb = os.path.getsize(img_path) / 1024
            if(file_size_kb>min_kb):
                with Image.open(img_path) as pil_img:
                    width, height = pil_img.size        
                if width > 500 and height > 500:
                    valid_images.append(img)
        imgs = valid_images 
        captioned_images = []
        for img in tqdm.tqdm(imgs,desc="Captioning Images"):
            img_path = img["image_path"]
            with Image.open(img_path).convert("RGB") as pil_img:
                pil_img.thumbnail((512, 512))
                inputs = self.processor(images=pil_img, return_tensors="pt").to(self.device, dtype=self.torch_dtype)
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        pixel_values=inputs.pixel_values,
                        max_length=100
                    )

                    generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

                captioned_images.append({
                        "caption": generated_text,
                        "image_path": img_path,
                        "metadata": img["metadata"]
                })

        return captioned_images

# imgs = [os.path.join("temp-images",i) for i in os.listdir("temp-images")]
# cap = CaptionGenerator()
# c = cap.generate_caption(imgs)
