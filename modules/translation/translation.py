import torchaudio
import torch

from pathlib import Path

from loguru import logger
from typing import Union, Tuple, List, Dict, Optional, Any

from .seamless.src.seamless_communication.inference.translator import Translator
from .data_models import TARGET_LANGUAGES, TASK_STRINGS, MinerRequest


class Translation:
    """A class for performing translation tasks using a specified model and vocoder.

    Attributes:
        model_name (str): The name of the translation model.
        vocoder_name (str): The name of the vocoder.
        translator (Translator): The translator object.
        target_languages (Dict[str, str]): A dictionary mapping language names to language codes.
        task_strings (Dict[str, str]): A dictionary mapping task strings to abbreviations.

    Args:
        in_file (Union[str, Path]): The input file for translation.
        task_string (str): The type of translation task.
        target_languages (List[str]): The target languages for translation.

    Returns:
        Tuple[Path, Path] | None: A tuple containing the paths to the translated text and audio files, or None if translation fails.
    """

    model_name: str
    vocoder_name: str
    translator: Translator
    target_languages: Dict[str, str]
    task_strings: Dict[str, str]

    def __init__(self) -> None:
        """
        Initializes the SeamlessTranslator object with the specified model and vocoder names,
        and creates a translator object using the specified model and vocoder. The translator
        object is created with the device set to "cuda:0" and the data type set to "torch.float16".
        The target_languages dictionary maps language names to language codes, and the task_strings
        dictionary maps task strings to abbreviations.
        """
        self.model_name = "seamlessM4T_v2_large"
        self.vocoder_name = (
            "vocoder_v2"
            if self.model_name == "seamlessM4T_v2_large"
            else "vocoder_36langs"
        )

        self.translator = Translator(
            model_name_or_card=self.model_name,
            vocoder_name_or_card=self.vocoder_name,
            device=torch.device(device="cuda:0"),
            dtype=torch.float16,
        )
        self.task_strings = TASK_STRINGS
        self.target_languages = TARGET_LANGUAGES

    def process(
        self,
        in_file: Union[str, Path],
        task_string: str = "speech2text",
        source_langauge: Optional[str] = "English",
        target_languages: List[str] = ["English"],
    ):
        return self.translation_inference(
            in_file=in_file,
            task_string=task_string,
            source_langauge=source_langauge,
            target_languages=target_languages,
        )

    def translation_inference(
        self,
        in_file: Union[str, Path],
        task_string: str = "speech2text",
        source_langauge: Optional[str] = "English",
        target_languages: List[str] = ["English"],
    ) -> Tuple[Path, Path] | None:
        """
        Perform translation inference on the given input file.

        Args:
            in_file (Union[str, Path]): The path to the input file.
            task_string (str, optional): The task string. Defaults to "s2st".
            target_languages (List[str], optional): The list of target languages. Defaults to ["eng"].

        Returns:
            Tuple[Path, Path] | None: A tuple containing the absolute paths to the output text file and output audio file, or None if the input file is not found.

        Raises:
            FileNotFoundError: If the input file is not found.
            ValueError: If the task string or target language is invalid.

        """

        if not Path(in_file).exists():
            logger.error(f"File {in_file} not found")
            raise FileNotFoundError(f"File {in_file} not found")

        input_file = Path(in_file)
        output_text = Path(f"modules/translation/out/{input_file.stem}.txt")
        output_audio = Path(f"modules/translation/out/{input_file.stem}.wav")
        
        task_str: str = self.task_strings[task_string]
        if not task_str:
            logger.error("Invalid task string")
            raise ValueError("Invalid task string")

        for tgt_lang in target_languages:

            tgt_lang: str = self.target_languages[tgt_lang]
            if not tgt_lang:
                logger.error("Invalid target language")
                raise ValueError("Invalid target language")

            if task_str.startswith("t"):
                text_output, speech_output = self.translator.predict(
                    input=str(input_file.read_text(encoding="utf-8")),
                    task_str=task_str,
                    src_lang=self.target_languages[source_langauge],
                    tgt_lang=tgt_lang,
                    )
            if task_str.startswith("s"):
                text_output, speech_output = self.translator.predict(
                    input=str(input_file),
                    task_str=task_str,
                    src_lang=self.target_languages[source_langauge],
                    tgt_lang=tgt_lang,
                )
            logger.info(f"Translated text in {tgt_lang}: {text_output[0]}")

            if speech_output:
                torchaudio.save(
                    uri=output_audio,
                    src=speech_output.audio_wavs[0][0].to(torch.float32).cpu(),
                    sample_rate=speech_output.sample_rate,
                )
            if text_output:
                output_text.write_text(
                    data=str(object=text_output[0]), encoding="utf-8"
                )

            logger.info("Translated target file")

            return text_output, speech_output


