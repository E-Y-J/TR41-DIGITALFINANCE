import torch
import os
import re 
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

class TransactionClassifier:
    def __init__(self, model_dir="transaction_classification_model"):
        """
        Load the model artifacts into memory when the class is initialized.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, model_dir)
    
        # Setup Device (CPU / GPU / MPS) to run the model on (performance optimization)
        self.device = "cpu" 
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")   
        
        try:
            # Load Model & Tokenizer
            self.tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
            self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
            
            self.model.to(self.device)
            
            # setup so that the model is in eval mode (no dropout, etc) 
            # might change later so the model can be further fine tuned and learn on the fly
            self.model.eval()
        except Exception as e:
            print(f"Could not load model. {e}")
            raise e

    def _preprocess(self, text):
        """
        Clean the input string to match exactly how the training data looked.
        """
        
        # come back to this later, might change the way we format the user input
        # since we ask for merchant and description
        clean_text = text.lower()
        clean_text = re.sub(r'\s*#\d+', '', clean_text)
        clean_text = re.sub(r'[a-z]+\d+', '', clean_text)
        clean_text = re.sub(r'\((.*?)\)', '', clean_text)
        clean_text = re.sub(r'\s*-.*', '', clean_text)
        clean_text = clean_text.strip()   
        
        return clean_text 

    def predict(self, raw_text):
        """
        Take a raw string, predict the category, and apply business logic (thresholds).
        Returns: (Label String, Confidence Score Float)
        """
        clean_text = self._preprocess(raw_text)

        # disables gradient calculations since we are only doing inference, saving memory and computation
        with torch.no_grad():
            inputs = self.tokenizer(
                clean_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=64
            ).to(self.device)

            outputs = self.model(**inputs)

            # Convert to Probability since the model outputs logits (raw scores)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get the highest probability and its corresponding label
            score, predicted_id = torch.max(probs, dim=1)

            # Convert to native Python types
            confidence = score.item()
            label = self.model.config.id2label[predicted_id.item()]

            if confidence < 0.80:
                return "Unknown", confidence
            else:
                return label, confidence
        

if __name__ == "__main__":
    classifier = TransactionClassifier()
    test_cases = ["Walmart", "Check #105", "Uber Trip"]
    edge_cases = [
        "SHELL OIL 12345",          
        "SHELL POINT MORTGAGE",     
        "CHECK #105",               
        "TARGET DEBIT CARD PAY",    
        "ATM WDL 554300",           
        "7-ELEVEN"                  
    ]
    for tx in test_cases:
        label, conf = classifier.predict(tx)
        print(f"Input: {tx} | Predicted: {label} | Confidence: {conf}")
        
    print("\n--- EDGE CASES ---")
    for tx in edge_cases:
        label, conf = classifier.predict(tx)
        print(f"Input: {tx} | Predicted: {label} | Confidence: {conf} ")