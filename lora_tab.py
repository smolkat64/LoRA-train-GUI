scheduler_list = ["linear", "cosine", "cosine_with_restarts",
                  "polynomial", "constant", "constant_with_warmup"]
max_token_length_list = ["75", "150", "225"]
training_method_list = ["Использовать эпохи", "Обучать в течении времени", "Своё количество шагов"]


default_settings_dict = { "pretrained_model_name_or_path": "",
                          "v2": False,
                          "v_parameterization": False,
                          "use_vae": False,
                          "vae": "",
                          "train_data_dir": "",
                          "use_reg_data": False,
                          "reg_data_dir": "",
                          "output_dir": "",
                          "output_name": "",
                          "training_duration_method": "Использовать эпохи",
                          "max_train_epochs": "10",
                          "train_time": {'hour': 0, 'min': 60, 'sec': 0},
                          "train_speed": "1.00",
                          "train_speed_type": "it/s",
                          "max_train_steps": "1000",
                          "train_batch_size": "1",
                          "save_every_n_epochs": "1",
                          "save_last_n_epochs": "1",
                          "use_separate_lr": False,
                          "learning_rate": "5e-4",
                          "unet_lr": "5e-4",
                          "text_encoder_lr": "2.5e-4",
                          "lr_scheduler": scheduler_list[0],
                          "lr_warmup_ratio": 0.0,
                          "resolution": "512,512",
                          "clip_skip": 1,
                          "network_dim": "128",
                          "network_alpha": "",
                          "shuffle_caption": True,
                          "max_token_length": max_token_length_list[2],
                          "keep_tokens": "1",
                          "seed": "-1",
                          "additional_parameters": """--caption_extension=\".txt\" --prior_loss_weight=1 \
                                                   --enable_bucket --min_bucket_reso=256 --max_bucket_reso=1024 --use_8bit_adam \
                                                   --xformers --save_model_as=safetensors --cache_latents"}""",
                          "gradient_checkpointing": False,
                          "gradient_accumulation_steps": "1",
                          "max_data_loader_n_workers": "8",
                          "save_precision": "fp16",
                          "mixed_precision": "fp16",
                          "logging_dir": "",
                          "use_custom_log_prefix": False,
                          "log_prefix": ""}


class LoRATab():
    def __init__(self, input_dict):
        for key, value in input_dict.items():
            setattr(self, key, value)
