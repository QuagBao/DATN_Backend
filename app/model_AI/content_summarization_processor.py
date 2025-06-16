import torch
import logging
from transformers import T5ForConditionalGeneration, AutoTokenizer
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detect device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

def load_model_and_tokenizer():
    """
    Load the Vietnamese T5 model and tokenizer from Hugging Face.
    Returns:
        model: T5 model for conditional generation
        tokenizer: Corresponding tokenizer
    """
    model_name_vie = "NlpHUST/t5-small-vi-summarization"
    model_name_eng = "t5-base"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name_vie)
        model = T5ForConditionalGeneration.from_pretrained(model_name_vie).to(device)
        model.eval()
        logger.info(f"Loaded model: {model_name_vie}")
        return model, tokenizer
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise Exception(f"Model loading failed: {str(e)}")

def summarize_text(text: str, model, tokenizer, max_length: int = 512, summary_max_length: int = 50, num_beams: int = 5) -> str:
    """
    Generate a summary for the input text using the T5 model.

    Args:
        text (str): Input text to summarize.
        model: Loaded T5 model.
        tokenizer: Loaded T5 tokenizer.
        max_length (int): Maximum input token length.
        summary_max_length (int): Maximum output summary length.
        num_beams (int): Beam search size.

    Returns:
        str: Generated summary text.
    """
    try:
        if not text.strip():
            raise ValueError("Input text is empty")

        # Encode input
        input_ids = tokenizer.encode(
            "summarize: " + text,
            return_tensors="pt",
            max_length=max_length,
            truncation=True
        ).to(device)

        # Generate summary
        summary_ids = model.generate(
            input_ids,
            max_length=summary_max_length,
            num_beams=num_beams,
            repetition_penalty=2.5,
            length_penalty=1.0,
            early_stopping=True
        )

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        raise Exception(f"Summarization failed: {str(e)}")

