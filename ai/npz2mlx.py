import mlx.core as mx
import json
from pathlib import Path
from typing import Dict, Union, Optional
from transformers import AutoModel, AutoTokenizer

def save_mlx_model(
    state_dict: Dict,
    config: Dict,
    save_path: Union[str, Path],
    tokenizer: Optional[object] = None
):
    """
    Save MLX model in a flat file structure
    
    Args:
        state_dict: MLX model state dictionary
        config: Model configuration
        save_path: Directory to save the model
        tokenizer: Tokenizer object (optional)
    """
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Save config
    config_dict = config.to_dict() if hasattr(config, "to_dict") else config
    config_dict["model_type"] = "mlx_transformer"
    config_dict["architecture"] = "MLXTransformer"
    
    with open(save_path / "config.json", "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2)
    
    # 2. Split and save weights
    chunk_size = 100
    state_dict_items = list(state_dict.items())
    total_chunks = (len(state_dict_items) + chunk_size - 1) // chunk_size
    
    for i in range(0, len(state_dict_items), chunk_size):
        chunk = {k: v for k, v in state_dict_items[i:i+chunk_size]}
        chunk_num = i // chunk_size
        chunk_file = save_path / f"model-{chunk_num:05d}-of-{total_chunks:05d}"
        mx.save_safetensors(str(chunk_file), chunk)
    
    # 3. Save tokenizer files if provided
    if tokenizer is not None:
        # 直接使用 tokenizer 的 save_pretrained 方法
        tokenizer.save_pretrained(str(save_path))
        
        # 如果有 merges 文件，确保它被正确保存
        if hasattr(tokenizer, "merges"):
            with open(save_path / "merges.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(tokenizer.merges))

def load_mlx_model(model_path: Union[str, Path]):
    """
    Load MLX model from saved format
    
    Args:
        model_path: Path to the saved model directory
    """
    model_path = Path(model_path)
    
    # Load config
    with open(model_path / "config.json", "r") as f:
        config = json.load(f)
    
    # Load weights
    weights = {}
    for weight_file in model_path.glob("model-*"):
        weights.update(mx.load(str(weight_file)))
    
    return config, weights

def convert_and_save_model(
    model_name: str = "./jina-embeddings-v3",
    output_path: str = "mlx_jina_embeddings_v3"
):
    """
    Convert and save a model in flat structure
    """
    # Load original model
    print(f"Loading model {model_name}...")
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    # Convert state dict
    print("Converting weights...")
    torch_state_dict = model.state_dict()
    mlx_state_dict = {k: mx.array(v.detach().cpu().numpy()) 
                      for k, v in torch_state_dict.items()}
    
    # Save in flat format
    print(f"Saving to {output_path}...")
    save_mlx_model(
        mlx_state_dict,
        model.config,
        output_path,
        tokenizer
    )
    
    print("Model conversion complete!")
    print("\nSaved files:")
    for file in Path(output_path).glob("*"):
        print(f"- {file.name}")

if __name__ == "__main__":
    convert_and_save_model()