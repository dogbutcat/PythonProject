import mlx.core as mx
import mlx.nn as nn
import torch
from transformers import AutoModel, AutoTokenizer
import numpy as np
from typing import Dict, Optional
from pathlib import Path

class JinaMLXEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.embeddings = nn.Embedding(config.vocab_size, config.hidden_size)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.layer_norm = nn.LayerNorm(config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        
        self.encoder = nn.TransformerEncoder(
            num_layers=config.num_hidden_layers,
            dims=config.hidden_size,
            num_heads=config.num_attention_heads,
            mlp_dims=config.intermediate_size,
            dropout=config.hidden_dropout_prob
        )
        
        # Project to embedding dimension
        self.proj = nn.Linear(config.hidden_size, 1024)
        
    def __call__(self, input_ids, attention_mask=None, training=False):
        seq_length = input_ids.shape[1]
        
        # Create position IDs
        position_ids = mx.arange(seq_length)[None, :]
        
        # Get embeddings
        inputs_embeds = self.embeddings(input_ids)
        position_embeddings = self.position_embeddings(position_ids)
        
        # Combine embeddings
        embeddings = inputs_embeds + position_embeddings
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        
        # Apply transformer layers
        hidden_states = self.encoder(embeddings, attention_mask)
        
        # Mean pooling
        if attention_mask is not None:
            attention_mask = attention_mask[:, :, None]
            hidden_states = hidden_states * attention_mask
            pooled = hidden_states.sum(axis=1) / attention_mask.sum(axis=1)
        else:
            pooled = hidden_states.mean(axis=1)
            
        # Project to final dimension
        embeddings = self.proj(pooled)
        
        # Normalize
        embeddings = embeddings / mx.linalg.norm(embeddings, axis=-1, keepdims=True)
        
        return embeddings

def convert_state_dict(torch_state_dict: Dict) -> Dict:
    """Convert PyTorch state dict to MLX compatible format."""
    mlx_state_dict = {}
    
    # Mapping dictionary for layer names
    name_mapping = {
        "embeddings.word_embeddings": "embeddings",
        "embeddings.position_embeddings": "position_embeddings",
        "embeddings.LayerNorm": "layer_norm",
    }
    
    for key, value in torch_state_dict.items():
        if isinstance(value, torch.Tensor):
            # Convert the tensor to numpy array
            numpy_value = value.detach().cpu().numpy()
            
            # Apply name mapping if needed
            for torch_name, mlx_name in name_mapping.items():
                key = key.replace(torch_name, mlx_name)
                
            # Convert encoder layer names
            if "encoder.layer" in key:
                key = key.replace("encoder.layer", "encoder.layers")
                
            # Handle attention layer names
            if "attention.self" in key:
                key = key.replace("attention.self", "attention")
                
            # Create MLX array
            mlx_value = mx.array(numpy_value)
            mlx_state_dict[key] = mlx_value
            
    return mlx_state_dict

def save_model_weights(weights: Dict[str, mx.array], path: str):
    """Save all model weights in a single file."""
    # # Convert MLX arrays to NumPy arrays
    # save_dict = {}
    # for key, value in weights.items():
    #     # Convert MLX array to NumPy array via Python list
    #     numpy_value = np.array(value.tolist())
    #     save_dict[key] = numpy_value
    
    # # Save using numpy.savez
    # np.savez(f"{path}.npz", **save_dict)
    mx.save_safetensors(f"{path}.safetensors", weights)

def create_mlx_model(model_name: str = "jinaai/jina-embeddings-v3", 
                    output_path: Optional[str] = "jina_mlx_model"):
    """
    Convert Jina Embeddings v3 model to MLX format
    
    Args:
        model_name: Name or path of the model
        output_path: Base path to save the MLX model weights
    """
    # Load the original model
    model = AutoModel.from_pretrained(model_name, trust_remote_code = True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Get the PyTorch state dict
    torch_state_dict = model.state_dict()
    
    # Convert to MLX format
    mlx_state_dict = convert_state_dict(torch_state_dict)
    
    if output_path:
        # Save individual weight arrays
        save_model_weights(mlx_state_dict, output_path)
        print(f"Model weights saved to {output_path}.npz")
    
    return mlx_state_dict, model.config, tokenizer

def load_model_weights(path: str) -> Dict[str, mx.array]:
    """Load model weights from a single npz file."""
    loaded = np.load(f"{path}.npz")
    return {key: mx.array(value) for key, value in loaded.items()}
    
    return weights

def test_model(model, tokenizer, text: str = "Hello, World!"):
    """Test the converted model with a sample input."""
    # Tokenize input
    inputs = tokenizer(text, return_tensors="pt")
    input_ids = mx.array(inputs["input_ids"].numpy())
    attention_mask = mx.array(inputs["attention_mask"].numpy())
    
    # Get embeddings
    embeddings = model(input_ids, attention_mask)
    print(f"Generated embeddings shape: {embeddings.shape}")
    return embeddings

def main():
    # Convert model
    state_dict, config, tokenizer = create_mlx_model()
    
    # Initialize MLX model
    model = JinaMLXEmbeddings(config)
    
    # Load weights
    model.update(state_dict)
    
    # Test the model
    # test_model(model, tokenizer)
    
    print("Conversion and test complete!")

if __name__ == "__main__":
    main()
