import os
import torch
import datetime
from pathlib import Path
from omegaconf import OmegaConf
from diffusers import AutoencoderKL, DDIMScheduler
from transformers import CLIPTextModel, CLIPTokenizer
from animatediff.models.unet import UNet3DConditionModel
from animatediff.pipelines.pipeline_animation import AnimationPipeline
from animatediff.utils.util import save_videos_grid
import napm

class VideoGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.project_root = Path(__file__).parent.parent
        self.models_path = self.project_root / "models"
        self.output_path = self.project_root / "videos"
        
        # Load config from napm package
        cfg = napm.config.NapmConfig().load()
        pkg_root = Path(cfg['packages']['animatediff']['install_dir'])
        self.inference_config = OmegaConf.load(pkg_root / "configs/inference/inference.yaml")
        
        self.sd_path = str(self.models_path / "StableDiffusion")
        self.mm_path = str(self.models_path / "Motion_Module" / "mm_sd_v15.ckpt")

        self._setup_pipeline()

    def _setup_pipeline(self):
        try:
            tokenizer = CLIPTokenizer.from_pretrained(self.sd_path, subfolder="tokenizer")
            text_encoder = CLIPTextModel.from_pretrained(self.sd_path, subfolder="text_encoder")
            vae = AutoencoderKL.from_pretrained(self.sd_path, subfolder="vae")
            
            unet_kwargs = OmegaConf.to_container(self.inference_config.get("unet_additional_kwargs", {}))
            unet = UNet3DConditionModel.from_pretrained_2d(
                self.sd_path, 
                subfolder="unet", 
                unet_additional_kwargs=unet_kwargs
            )

            self.pipeline = AnimationPipeline(
                vae=vae,
                text_encoder=text_encoder,
                tokenizer=tokenizer,
                unet=unet,
                scheduler=DDIMScheduler(**OmegaConf.to_container(self.inference_config.noise_scheduler_kwargs)),
            ).to(self.device)

            # Load motion module
            motion_module_state_dict = torch.load(self.mm_path, map_location="cpu")
            self.pipeline.unet.load_state_dict(motion_module_state_dict, strict=False)
            
        except Exception as e:
            print(f"Error initializing models: {e}")
            raise

    def generate(self, prompt, n_frames=16, steps=25, guidance_scale=7.5, seed=-1):
        if seed == -1:
            seed = torch.seed()
        
        generator = torch.Generator(device=self.device).manual_seed(seed)
        
        try:
            sample = self.pipeline(
                prompt=prompt,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                width=448,
                height=320,
                video_length=n_frames,
                generator=generator
            ).videos

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            out_filename = f"gen_{timestamp}.gif"
            out_path = self.output_path / out_filename
            
            save_videos_grid(sample, str(out_path), n_rows=1)
            return str(out_path)
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                torch.cuda.empty_cache()
            raise e
        except Exception as e:
            raise e