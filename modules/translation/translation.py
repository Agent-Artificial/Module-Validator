import io
import scipy
import torch
import base64
import torchaudio

from loguru import logger
from typing import Optional
from functools import lru_cache
from typing import Dict, Tuple, Union
from transformers import AutoProcessor, SeamlessM4Tv2Model
from pydub import AudioSegment

from .data_models import TARGET_LANGUAGES, TASK_STRINGS, TranslationRequest, TranslationConfig

translation_config = TranslationConfig()

class Translation:
    def __init__(self):
        """
        Initializes a new instance of the Translation class.

        Args:
            translation_config (TranslationConfig): The configuration object for translation.

        Initializes the following instance variables:
            - translation_config (TranslationConfig): The configuration object for translation.
            - processor (AutoProcessor): The processor object for preprocessing input data.
            - model (SeamlessM4Tv2Model): The model object for translation.
            - device (torch.device): The device to run the model on (CUDA if available, otherwise CPU).
            - target_languages (Dict[str, str]): A dictionary mapping target languages to their codes.
            - task_strings (Dict[str, str]): A dictionary mapping task strings to their codes.
            - data_input (None): The input data for translation.
            - task_string (None): The task string for translation.
            - source_language (None): The source language for translation.
            - target_language (None): The target language for translation.
        """
        self.translation_config = translation_config
        self.processor = AutoProcessor.from_pretrained(translation_config.model_name_or_card)
        self.model = SeamlessM4Tv2Model.from_pretrained(translation_config.model_name_or_card)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.target_languages: Dict[str, str] = TARGET_LANGUAGES
        self.task_strings: Dict[str, str] = TASK_STRINGS
        self.data_input = None
        self.task_string = None
        self.source_language = None
        self.target_language = None

    @lru_cache(maxsize=128)
    def _get_language(self, language: str) -> str:
        """
        Function to retrieve the language from the target_languages dictionary.
        
        Parameters:
            self: The Translation object.
            language: A string representing the language to retrieve.
        
        Returns:
            A string representing the language from the target_languages dictionary.
        """
        try:
            return self.target_languages[language]
        except KeyError as e:
            logger.error(f"Invalid language: {language} {e}")
            raise ValueError(f"Invalid language: {language}") from e

    def process(self, miner_request: TranslationRequest) -> Tuple[Union[str, None], Union[torch.Tensor, None]]:
        """
        A function that processes a TranslationRequest object to perform translation tasks. 
        Retrieves input data, task string, source and target languages, preprocesses the input data, 
        predicts the output based on the input and languages, and processes the final output. 
        Raises ValueErrors for invalid task strings and missing input data.

        Parameters:
            self: The Translation object.
            miner_request (TranslationRequest): The request object containing input data, task string, 
                source language, and target language.

        Returns:
            Tuple[Union[str, None], Union[torch.Tensor, None]]: 
                A tuple containing either a string or None, and either a torch.Tensor or None, 
                representing the processed output.
        """
        if "input" in miner_request.data:
            self.data_input = miner_request.data["input"]
        if "task_string" in miner_request.data:
            self.task_string = miner_request.data["task_string"]
        if "source_language" in miner_request.data:
            self.source_language = miner_request.data["source_language"].title()
        if "target_language" in miner_request.data:
            self.target_language = miner_request.data["target_language"].title()

        if not self.task_string:
            raise ValueError(f"Invalid task string: {miner_request.data}")

        if self.data_input is None:
            raise ValueError("No input provided")
        if self.task_string.startswith("speech"):
            try:
            
                self.data_input = self._preprocess(self.data_input)
            except Exception as e:
                logger.error(f"Error preprocessing input: {e}")
                raise ValueError(f"Error preprocessing input: {e}") from e
        
        output = None
        with torch.no_grad():
            output = self._predict(
                input=self.data_input,
                task_str=self.task_strings[self.task_string],
                src_lang=self.target_languages[self.source_language],
                tgt_lang=self.target_languages[self.target_language]
            )
            
        if self.task_string.endswith("speech"):
            output = self._process_audio_output(output)
        else:
            output = output.encode("utf-8")

        return self._process_output(output)
    
    def _preprocess(self, input_data):
        """
        Preprocesses the input data by writing it to a file and returning the file path.

        Args:
            input_data (str): The base64 encoded audio data to be preprocessed.

        Returns:
            str: The file path of the preprocessed audio file.

        Raises:
            None
        """
        with open("modules/translation/in/audio_request.wav", "wb") as f:
            f.write(base64.b64decode(input_data))
        return "modules/translation/in/audio_request.wav"
    
    def _process_text_inputs(self, input_data: str, src_lang: str) -> Dict[str, torch.Tensor]:
        """
        Processes text inputs by utilizing the processor to convert input data into torch tensors.

        Parameters:
            self: The Translation object.
            input_data (str): The input text data to be processed.
            src_lang (str): The source language of the input text.

        Returns:
            Dict[str, torch.Tensor]: A dictionary containing torch tensors as values for different keys.
        """
        return self.processor(text=input_data, src_lang=src_lang, return_tensors="pt")

    def _process_audio_input(self, input_data: str, src_lang: str) -> Dict[str, torch.Tensor]:
        """
        Processes the audio input data and returns a dictionary of tensors.

        Args:
            input_data (str): The path to the audio file.
            src_lang (str): The source language of the audio.

        Returns:
            Dict[str, torch.Tensor]: A dictionary containing the processed tensors.
        """
        waveform, sample_rate = torchaudio.load(input_data)
        if sample_rate != 16000:
            waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
        return self.processor(audios=waveform.squeeze(), src_lang=src_lang, sampling_rate=16000, return_tensors="pt")

    def _generate_audio(self, input_data: Dict[str, torch.Tensor], tgt_lang: str) -> torch.Tensor:
        """
        Generate an audio tensor based on the input data and target language.

        Args:
            input_data (Dict[str, torch.Tensor]): A dictionary containing input data tensors.
            tgt_lang (str): The target language for the generated audio.

        Returns:
            torch.Tensor: The generated audio tensor.

        """
        input_data = {k: v.to(self.device) for k, v in input_data.items()}
        return self.model.generate(**input_data, tgt_lang=tgt_lang)[0]

    def _generate_text(self, input_data: Dict[str, torch.Tensor], tgt_lang: str) -> str:
        """
        Generates text based on the input data and target language.

        Args:
            input_data (Dict[str, torch.Tensor]): A dictionary containing input data tensors.
            tgt_lang (str): The target language for the generated text.

        Returns:
            str: The generated text.
        """
        input_data = {k: v.to(self.device) for k, v in input_data.items()}
        output_tokens = self.model.generate(**input_data, tgt_lang=tgt_lang, generate_speech=False)
        return self.processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

    def _predict(self, **kwargs) -> Tuple[Union[str, None], Union[torch.Tensor, None]]:
        """
        A function that processes input data for prediction. 
        Retrieves input data, task string, source and target languages, preprocesses the input data based on the task string, 
        generates output based on the input and languages, and returns the output. 
        Logs intermediate information for debugging. 
        Raises errors for processing and prediction failures.

        Args:
            **kwargs: A dictionary containing input data, task string, source language, and target language.

        Returns:
            Tuple[Union[str, None], Union[torch.Tensor, None]]: 
                A tuple containing either a string or None, and either a torch.Tensor or None, 
                representing the predicted output.
        """
        try:
            input_data = kwargs['input']
            task_str = kwargs['task_str']
            src_lang = kwargs['src_lang']
            tgt_lang = kwargs['tgt_lang']
            
            if task_str.startswith('s2'):
                input_data = self._process_audio_input(input_data, src_lang)
            else:
                input_data = self._process_text_inputs(input_data, src_lang)
                
            logger.debug(str(input_data)[:30])
            logger.debug(type(input_data))
            logger.debug(kwargs)
            output = None
            try:
                if self.task_string.endswith("speech"):
                    output = self._generate_audio(input_data, tgt_lang)
                else:
                    output = self._generate_text(input_data, tgt_lang)
            except AttributeError as e:
                logger.error(f"Error processing translation: {e}")
                raise ValueError(f"Error processing translation: {e}") from e
            logger.debug(output)
            logger.debug(type(output))
            return output
        
        except Exception as e:
            logger.error(f"Error processing translation: {e}")
            raise
        
    def _process_audio_output(self, output: torch.Tensor) -> torch.Tensor:
        """
        Process the audio output tensor and return it as a bytes object.

        Args:
            output (torch.Tensor): The audio output tensor to be processed.

        Returns:
            torch.Tensor: The processed audio output as a bytes object.

        Raises:
            ValueError: If there is an error processing the audio output.
        """
        try:
            buffer = io.BytesIO()
            torch.save(output, buffer)
        except Exception as e:
            logger.error(f"Error processing audio output: {e}")
            raise ValueError(f"Error processing audio output: {e}") from e
        return buffer.getvalue()
    
    def _process_output(self, output: str) -> str:
        """
        Process the final output to encode it in base64 and decode it to utf-8.

        Args:
            output (str): The final output to be processed.

        Returns:
            str: The processed output after encoding and decoding.
        Raises:
            ValueError: If there is an error processing the final output.
        """
        try:
            output = base64.b64encode(output).decode("utf-8")
        except Exception as e:
            logger.error(f"Error processing final output: {e}")
            raise ValueError(f"Error processing final output: {e}") from e
        return output

    
def text2text(translation: Translation, miner_request: Optional[TranslationRequest] = None):
    """
    Generates a translation of the input text from English to French using the given Translation object.

    Args:
        translation (Translation): The Translation object used to generate the translation.
        miner_request (Optional[TranslationRequest], optional): The optional TranslationRequest object containing additional data for the translation. Defaults to None.

    Returns:
        str: The translated text from English to French.

    Example:
        >>> translation = Translation()
        >>> miner_request = TranslationRequest(data={"input": "Hello, my name is John Doe.", "task_string": "text2text", "source_language": "English", "target_language": "French"})
        >>> text2text(translation, miner_request)
        'Bonjour, je m'appelle John Doe.'
    """
    translation_request = miner_request or TranslationRequest(
        data={"input": "Hello, my name is John Doe.", "task_string": "text2text", "source_language": "English", "target_language": "French"}
    )
    return translation.process(translation_request)


def text2speech(translation: Translation, miner_request: Optional[TranslationRequest] = None):
    """
    Generates speech from text using the given Translation object.

    Args:
        translation (Translation): The Translation object used to generate the speech.
        miner_request (Optional[TranslationRequest], optional): The optional TranslationRequest object containing additional data for the speech generation. Defaults to None.

    Returns:
        Union[str, None]: The generated speech as a string, or None if an error occurred.
    """
    translation_request = miner_request or TranslationRequest(
        data={"input": "Hello, my name is John Doe.", "task_string": "text2speech", "source_language": "English", "target_language": "French"}
    )
    return translation.process(translation_request)


def speech2text(translation: Translation, miner_request: Optional[TranslationRequest] = None):
    """
    A function that converts speech input to text using a given Translation object.
    
    Args:
        translation (Translation): The Translation object used for the conversion.
        miner_request (Optional[TranslationRequest], optional): Additional data for the conversion. Defaults to None.
        
    Returns:
        The processed text output.
    """
    translation_request = miner_request or TranslationRequest(
        data={"input": "modules/translation/in/audio_request.wav", "task_string": "speech2text", "source_language": "English", "target_language": "French"}
    )
    return translation.process(translation_request)


def speech2speech(translation: Translation, miner_request: Optional[TranslationRequest] = None):
    """
    Converts speech input to speech output using a given Translation object.
    
    Args:
        translation (Translation): The Translation object used for the conversion.
        miner_request (Optional[TranslationRequest], optional): Additional data for the conversion. Defaults to None.
        
    Returns:
        The processed speech output.
    """
    translation_request = miner_request or TranslationRequest(
        data={"input": "modules/translation/in/audio_request.wav", "task_string": "speech2speech", "source_language": "English", "target_language": "French"}
    )
    return translation.process(translation_request)
    

if __name__ == "__main__":
    translation = Translation(TranslationConfig())
    result = speech2text(translation)
    print(f"speech2text: {result}")
    result = speech2speech(translation)
    print(f"speech2speech: {result}")
    result = text2text(translation)
    print(f"text2text: {result}")
    result = text2speech(translation)
    print(f"text2speech: {result}")
        
    