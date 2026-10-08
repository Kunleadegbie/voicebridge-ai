
(() => {
  const get = (id) => document.getElementById(id);

  const supportedLanguages = new Set(["en-NG", "yo-NG", "ig-NG", "ha-NG"]);

  let player = null;
  let audioUrl = null;
  let cachedKey = null;
  let cachedBlob = null;
  let requestController = null;
  let generation = 0;

  function setStatus(message) {
    get("speechStatus").textContent = message;
  }

  function stopPlayback() {
    if (player) {
      player.pause();
      player.currentTime = 0;
    }
    if (requestController) {
      requestController.abort();
      requestController = null;
    }
    generation += 1;
    get("stopAnswer").disabled = true;
  }

  function clearAudio() {
    stopPlayback();
    player = null;
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      audioUrl = null;
    }
    cachedKey = null;
    cachedBlob = null;
  }

  async function speakAnswer(text, language) {
    if (!supportedLanguages.has(language)) {
      setStatus("Spoken answers are not configured for this language yet.");
      return;
    }

    const key = JSON.stringify([language, text]);
    stopPlayback();
    const currentGeneration = generation;

    get("playAnswer").disabled = true;
    get("stopAnswer").disabled = false;

    try {
      if (cachedKey !== key || !cachedBlob) {
        setStatus("Preparing spoken answer...");

        requestController = new AbortController();

        const response = await fetch("/tts/speak", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, language }),
          signal: requestController.signal
        });

        if (!response.ok) {
          throw new Error("Speech service unavailable");
        }

        const blob = await response.blob();

        if (generation !== currentGeneration) return;
        if (!blob.size) throw new Error("Empty audio received");

        if (audioUrl) URL.revokeObjectURL(audioUrl);

        cachedBlob = blob;
        cachedKey = key;
        audioUrl = URL.createObjectURL(blob);
      }

      if (generation !== currentGeneration) return;

      player = new Audio(audioUrl);

      player.onended = () => {
        if (generation === currentGeneration) {
          setStatus("Finished speaking.");
          get("stopAnswer").disabled = true;
        }
      };

      setStatus("Playing spoken answer...");
      await player.play();

    } catch (error) {
      if (generation !== currentGeneration) return;

      if (error.name === "NotAllowedError") {
        setStatus("Tap Listen to answer to play the audio.");
      } else if (error.name !== "AbortError") {
        setStatus("Audio unavailable. You can still read the answer.");
      }
    } finally {
      if (generation === currentGeneration) {
        requestController = null;
        get("playAnswer").disabled = false;
      }
    }
  }

  window.voiceBridgeSpeech = {
    onAnswer(data, language) {
      clearAudio();

      const text = data.response || "";
      const supported = supportedLanguages.has(language);

      get("playAnswer").disabled = !supported || !text;
      get("stopAnswer").disabled = true;

      if (!supported) {
        setStatus("Spoken answers for this language are coming soon.");
        return;
      }

      setStatus("Spoken answer available.");

      if (data.interaction_source === "voice" && get("autoSpeak").checked) {
        speakAnswer(text, language);
      }
    }
  };

  get("playAnswer").addEventListener("click", () => {
    speakAnswer(get("answer").textContent, get("language").value);
  });

  get("stopAnswer").addEventListener("click", () => {
    stopPlayback();
    setStatus("Playback stopped.");
    get("playAnswer").disabled = false;
  });

  get("language").addEventListener("change", () => {
    clearAudio();
    get("playAnswer").disabled = true;
    setStatus("");
  });
})();
