import numpy as np
from typing import Dict, Any, List, Union, Optional, Any

class Embedding:
    def __init__(self, module_config: Dict[str, Any]):
        self.config = module_config
        self.dimension = self.config.get('dimension', 100)
        print(f"Embedding module initialized with dimension: {self.dimension}")

    def process(self, data: Union[str, Dict[str, Any]], params: Optional[Dict[str, Any]] = None) -> List[float]:
        """
        A simple embedding function that converts input data to a vector.
        This is a naive implementation for demonstration purposes.
        In a real-world scenario, you'd use a more sophisticated embedding technique.
        """
        # Convert input data to a string representation
        if isinstance(data, dict):
            data_str = str(sorted(data.items()))  # Sort to ensure consistency
        else:
            data_str = str(data)
        
        # Generate a seed from the string representation
        seed = sum(ord(c) for c in data_str)
        np.random.seed(seed)
        
        # Generate a random vector
        embedding = np.random.randn(self.dimension)
        
        # Normalize the vector
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()

# For testing purposes
if __name__ == "__main__":
    config = {"dimension": 50}
    embedding_module = Embedding(config)
    
    # Test with a string
    test_data_str = "Hello, world!"
    result_str = embedding_module.process(test_data_str, {})
    print(f"Test embedding for string (first 5 dimensions): {result_str[:5]}")
    
    # Test with a dictionary
    test_data_dict = {"key1": "value1", "key2": "value2"}
    result_dict = embedding_module.process(test_data_dict, {})
    print(f"Test embedding for dict (first 5 dimensions): {result_dict[:5]}")