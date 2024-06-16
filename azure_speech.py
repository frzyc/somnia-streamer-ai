from dotenv import load_dotenv
import time
import azure.cognitiveservices.speech as speechsdk
import keyboard
import os

# Just in case this file is loaded alone
load_dotenv(dotenv_path=".env.local")


class AzureSpeechAIManager:
    azure_speechconfig = None
    azure_audioconfig = None
    azure_speechrecognizer = None

    def __init__(self):
        try:
            self.azure_speechconfig = speechsdk.SpeechConfig(
                subscription=os.getenv("AZURE_TTS_KEY"),
                region=os.getenv("AZURE_TTS_REGION"),
            )
        except TypeError:
            exit(
                "[red]Err: You forgot to set AZURE_TTS_KEY or AZURE_TTS_REGION in your environment."
            )

        self.azure_speechconfig.speech_recognition_language = "en-US"
        self.azure_speechconfig.speech_synthesis_voice_name = (
            "en-US-AvaMultilingualNeural"
        )
        self.azure_speechsynthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.azure_speechconfig
        )

        self.azure_audioconfig = speechsdk.audio.AudioConfig(
            use_default_microphone=True
        )
        self.azure_speechrecognizer = speechsdk.SpeechRecognizer(
            speech_config=self.azure_speechconfig, audio_config=self.azure_audioconfig
        )

    def stt_from_mic(self):

        print("Speak into your microphone.")
        speech_recognition_result = (
            self.azure_speechrecognizer.recognize_once_async().get()
        )
        text_result = speech_recognition_result.text

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print(
                "No speech could be recognized: {}".format(
                    speech_recognition_result.no_match_details
                )
            )
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

        return text_result

    def stt_from_mic_continuous(self, stop_key="p"):
        self.azure_speechrecognizer = speechsdk.SpeechRecognizer(
            speech_config=self.azure_speechconfig
        )

        done = False

        # This gets called basically every word.
        # def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        #    print('RECOGNIZING: {}'.format(evt))
        # self.azure_speechrecognizer.recognizing.connect(recognizing_cb)

        # Optional callback to print out whenever a chunk of speech is finished being recognized. Make sure to let this finish before ending the speech recognition.
        def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
            print("RECOGNIZED: {}".format(evt))

        self.azure_speechrecognizer.recognized.connect(recognized_cb)

        # We register this to fire if we get a session_stopped or cancelled event.
        def stop_cb(evt: speechsdk.SessionEventArgs):
            print("CLOSING speech recognition on {}".format(evt))
            nonlocal done
            done = True

        # Connect callbacks to the events fired by the speech recognizer
        self.azure_speechrecognizer.session_stopped.connect(stop_cb)
        self.azure_speechrecognizer.canceled.connect(stop_cb)

        # This is where we compile the results we receive from the ongoing "Recognized" events
        all_results = []

        def handle_final_result(evt):
            all_results.append(evt.result.text)

        self.azure_speechrecognizer.recognized.connect(handle_final_result)

        # Perform recognition. `start_continuous_recognition_async asynchronously initiates continuous recognition operation,
        # Other tasks can be performed on this thread while recognition starts...
        # wait on result_future.get() to know when initialization is done.
        # Call stop_continuous_recognition_async() to stop recognition.
        result_future = self.azure_speechrecognizer.start_continuous_recognition_async()
        result_future.get()  # wait for voidfuture, so we know engine initialization is done.
        print("Continuous Speech Recognition is now running, say something.")

        while not done:
            # Press the stop key. This is 'p' by default but user can provide different key
            if keyboard.read_key() == stop_key:
                print("\nEnding azure speech recognition\n")
                self.azure_speechrecognizer.stop_continuous_recognition_async()
                break

        final_result = " ".join(all_results).strip()
        print(f"\n\nHeres the result we got!\n\n{final_result}\n\n")
        return final_result

    def tts(self, text):
        result = self.azure_speechsynthesizer.speak_ssml_async(self.ssml(text)).get()
        # result = self.azure_speechsynthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # print("Speech synthesized for text: {}".format(text))
            return
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

    def ssml(self, text, voice_style="affectionate", role="Girl"):
        return f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xmlns:emo='http://www.w3.org/2009/10/emotionml' xml:lang='en-US'>
        <voice name="en-US-AvaMultilingualNeural">
        <mstts:express-as style='{voice_style}' role='{role}'>
            <prosody rate="fast">
            {text}
            </prosody>
        </mstts:express-as>
        </voice>
        </speak>
        """


# Tests
if __name__ == "__main__":

    speechtotext_manager = AzureSpeechAIManager()

    # speechtotext_manager.speechtotext_from_mic()

    # result = speechtotext_manager.speechtotext_from_mic_continuous()
    # print(f"[green]HERE IS THE RESULT:\n{result}")

    speechtotext_manager.tts("what are you doing now?")
