from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop


def _download_default_model():
    try:
        from faster_whisper import WhisperModel
        print("Downloading default Whisper model (small)...")
        WhisperModel("small", device="auto", compute_type="auto")
        print("Default model ready.")
    except Exception as e:
        print(f"Warning: could not pre-download Whisper model: {e}")


class PostInstall(install):
    def run(self):
        super().run()
        _download_default_model()


class PostDevelop(develop):
    def run(self):
        super().run()
        _download_default_model()


setup(cmdclass={"install": PostInstall, "develop": PostDevelop})
